import os
import json
import datetime
from pathlib import Path
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm

# --- Configuration ---
# Load environment variables from .env file (for API key)
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("Google API key not found. Please set it in your .env file.")

# Configure the Generative AI client
genai.configure(api_key=GOOGLE_API_KEY)

# --- Core Functions ---

def parse_invoices_from_images(directory_path: str) -> list:
    """
    Analyzes all images in a directory using a vision model to extract invoice data.

    Args:
        directory_path: The path to the folder containing invoice images.

    Returns:
        A list of dictionaries, where each dictionary represents a parsed invoice.
    """
    print(f"📄 Parsing invoices from '{directory_path}'...")
    
    invoice_data = []
    image_files = [f for f in os.listdir(directory_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # --- CHANGE #1 HERE ---
    # Use the newer, more reliable model for vision tasks.
    vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # Prompt for the vision model - very specific to get clean JSON
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

    # Use tqdm for a progress bar
    for filename in tqdm(image_files, desc="Processing Images"):
        try:
            image_path = Path(directory_path) / filename
            image = Image.open(image_path)
            
            # Ask the vision model to parse the invoice
            response = vision_model.generate_content([prompt_template, image])
            
            # Clean up the response to get only the JSON part
            json_text = response.text.strip().replace('```json', '').replace('```', '')
            
            # Load the cleaned text as a JSON object
            data = json.loads(json_text)
            invoice_data.append(data)
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            
    return invoice_data


def start_chatbot(invoice_data: list):
    """
    Starts an interactive chatbot session to answer questions about the invoice data.

    Args:
        invoice_data: A list of parsed invoice dictionaries.
    """
    print("\n✅ Invoice parsing complete. Starting chatbot.")
    print("Ask questions like: 'How many invoices are due in the next 7 days?' or 'What is the total from Microsoft?'")
    print("Type 'exit' to quit.\n")

    # --- CHANGE #2 HERE ---
    # Use the same powerful model for Q&A.
    chat_model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # Get today's date to provide context for time-sensitive questions
    today_date = datetime.date.today().strftime("%Y-%m-%d")

    while True:
        user_question = input("You: ")
        if user_question.lower() == 'exit':
            print("🤖 Goodbye!")
            break

        # Construct a detailed prompt for the chatbot
        prompt = f"""
        You are a helpful invoice assistant. Your task is to answer the user's question based *only* on the provided invoice data.
        
        Today's date is: {today_date}

        Here is the available invoice data in JSON format:
        {json.dumps(invoice_data, indent=2)}

        User's question: "{user_question}"

        Please provide a clear and concise answer. If you perform any calculations (like counting invoices or summing totals), state the result clearly.
        For any questions about due dates, remember that the invoices from 2019 are long overdue.
        """

        try:
            response = chat_model.generate_content(prompt)
            print(f"🤖 Assistant: {response.text}\n")
        except Exception as e:
            print(f"❌ An error occurred: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    # The directory where your invoice images are stored
    INVOICES_DIR = "invoices"
    
    # 1. Parse the invoices from the images
    parsed_data = parse_invoices_from_images(INVOICES_DIR)
    
    if not parsed_data:
        print("⚠️ No invoice data could be parsed. Please check the 'invoices' folder and image files.")
    else:
        # 2. Start the interactive chatbot
        start_chatbot(parsed_data)