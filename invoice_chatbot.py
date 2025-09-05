import os
import json
import datetime
import pandas as pd
from pathlib import Path
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm
import io
import contextlib

# --- Configuration ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Google API key not found. Please set it in your .env file.")
genai.configure(api_key=GOOGLE_API_KEY)

# --- (This function remains the same) ---
def parse_invoices_from_images(directory_path: str) -> list:
    """Analyzes all images in a directory using a vision model to extract invoice data."""
    print(f"📄 Parsing invoices from '{directory_path}'...")
    invoice_data = []
    image_files = [f for f in os.listdir(directory_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt_template = """
    You are an expert invoice data extraction assistant.
    Analyze the invoice image and extract the following fields in a clean JSON format:
    - vendor: The name of the company that sent the invoice.
    - invoice_number: The unique identifier for the invoice.
    - invoice_date: The date the invoice was issued (in YYYY-MM-DD format). If the year is ambiguous (e.g., '19), assume it's in the 21st century (2019).
    - due_date: The date the payment is due (in YYYY-MM-DD format). If the year is ambiguous (e.g., '19), assume it's in the 21st century (2019).
    - total: The total amount due as a floating-point number (e.g., 2450.00).

    Do not include any text or explanations before or after the JSON object.
    """
    for filename in tqdm(image_files, desc="Processing Images"):
        try:
            image_path = Path(directory_path) / filename
            image = Image.open(image_path)
            response = vision_model.generate_content([prompt_template, image])
            json_text = response.text.strip().replace('```json', '').replace('```', '')
            data = json.loads(json_text)
            invoice_data.append(data)
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    return invoice_data

def create_pandas_dataframe(invoice_data: list) -> pd.DataFrame:
    """Converts the list of invoice data into a clean Pandas DataFrame."""
    if not invoice_data:
        return pd.DataFrame()
    df = pd.DataFrame(invoice_data)
    # Convert date columns to actual datetime objects for proper calculations
    df['invoice_date'] = pd.to_datetime(df['invoice_date'])
    df['due_date'] = pd.to_datetime(df['due_date'])
    # Ensure total is a numeric type
    df['total'] = pd.to_numeric(df['total'])
    print("\n✅ Invoice data loaded into Pandas DataFrame.")
    print(df.info())
    return df

def start_chatbot_agent(df: pd.DataFrame):
    """Starts an interactive chatbot that uses an LLM to generate and execute Pandas code."""
    if df.empty:
        print("⚠️ DataFrame is empty. Cannot start chatbot.")
        return

    print("\n🤖 Agent Chatbot Initialized. Ask complex questions about your invoices.")
    print("Type 'exit' to quit.\n")

    # Use a powerful model for code generation
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    today_date = pd.to_datetime(datetime.date.today())

    # The new prompt template for generating Pandas code
    code_generation_prompt_template = f"""
    You are a data analysis expert. Your task is to translate a user's question into a single-line Python script that uses a Pandas DataFrame named `df`.

    The DataFrame `df` has the following columns and data types:
    {df.info()}

    A variable `today_date` is available and is set to {today_date.strftime('%Y-%m-%d')}.

    RULES:
    1.  Generate ONLY the Python code to answer the question.
    2.  The code must be a single line that can be executed.
    3.  The code must print the final result.
    4.  Do NOT include any explanations, comments, or markdown formatting.
    5.  For complex answers involving multiple data points (like listing invoices), format the output clearly within the print statement (e.g., using .to_string()).

    EXAMPLES:
    User question: "How many invoices do I have?"
    print(len(df))

    User question: "What is the total amount I owe?"
    print(df['total'].sum())

    User question: "How many invoices are due in the next 7 days?"
    print(df[df['due_date'].between(today_date, today_date + pd.Timedelta(days=7))].shape[0])

    User question: "List the vendors of invoices over $2000"
    print(df[df['total'] > 2000][['vendor', 'total']].to_string(index=False))
    ---
    User question: "{{user_question}}"
    """

    while True:
        user_question = input("You: ")
        if user_question.lower() == 'exit':
            print("🤖 Goodbye!")
            break

        try:
            # 1. Generate Pandas code from the user's question
            prompt = code_generation_prompt_template.format(user_question=user_question)
            response = model.generate_content(prompt)
            generated_code = response.text.strip().replace("```python", "").replace("```", "")
            
            print(f"⚙️ Generated Code: {generated_code}")

            # 2. Execute the generated code safely and capture the output
            # This is a simplified execution context. In a production system,
            # use a more secure sandboxed environment.
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                exec(generated_code, {"df": df, "pd": pd, "today_date": today_date})
            code_result = buffer.getvalue().strip()
            
            # 3. Use the LLM to summarize the result in natural language
            summarization_prompt = f"""
            You are a helpful assistant.
            The user asked: "{user_question}"
            The answer, derived from data analysis, is: "{code_result}"
            
            Please formulate a friendly, natural language response based on this answer.
            """
            
            final_response = model.generate_content(summarization_prompt)
            print(f"🤖 Assistant: {final_response.text}\n")

        except Exception as e:
            print(f"❌ An error occurred: {e}\nCould not answer the question. Please try rephrasing.")

# --- Main Execution ---
if __name__ == "__main__":
    INVOICES_DIR = "invoices"
    
    # 1. Parse invoices into structured data
    parsed_data = parse_invoices_from_images(INVOICES_DIR)
    
    # 2. Load structured data into a Pandas DataFrame
    invoice_df = create_pandas_dataframe(parsed_data)
    
    # 3. Start the advanced agent-based chatbot
    start_chatbot_agent(invoice_df)