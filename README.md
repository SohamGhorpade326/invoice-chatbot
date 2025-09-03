 🧾 Invoice Q&A Chatbot

This project is a simple, command-line chatbot that can read invoice images and answer questions about them. It uses Google's Gemini AI models to perform both image-to-data extraction and natural language question-answering.

 ✨ Features

  Automated Invoice Parsing: Uses the `gemini-1.5-flash-latest` model to extract structured data (vendor, total, due date, etc.) from invoice images.
  Natural Language Q&A: Employs the same model to answer user questions based on the extracted data.
  Beginner-Friendly: Minimal setup with a single script and clear instructions.

 📂 Project Structure
 invoice-chatbot/
├── invoices/                 # Directory for your invoice images
│   ├── invoice-1.PNG
│   └── ...
├── .env                      # Stores your API key (ignored by Git)
├── .gitignore                # Specifies files for Git to ignore
├── invoice_chatbot.py        # The main Python script
├── README.md                 # This file
└── requirements.txt          # Python dependencies

 🛠️ Setup Instructions

1.  Prerequisites: Python 3.8+ and a Google AI API Key.
2.  Clone the repository: `git clone <your-repo-url>`
3.  Set up your environment file:
    - Create a file named `.env` in the project root.
    - Add your API key to it: `GOOGLE_API_KEY="YOUR_API_KEY_HERE"`
4.  Install dependencies: `pip install -r requirements.txt`

 🚀 How to Run

1.  Place your invoice images inside the `invoices/` folder.
2.  Run the chatbot from your terminal:
    ```bash
    python invoice_chatbot.py
    ```
3.  The script will parse the invoices and then prompt you to ask questions. Type `exit` to quit.

 💬 Example Q&A Session

Here is an actual session with the chatbot using the sample invoices:
✅ Invoice parsing complete. Starting chatbot.
...
You: How many invoices do I have in total?
🤖 Assistant: You have a total of 3 invoices.

You: What is the total for the Microsoft invoice?
🤖 Assistant: The total for the Microsoft invoice (INV-0043) is $3100.00.

You: What is the total amount I owe across all invoices?
🤖 Assistant: The total amount owed across all invoices is $3308.06. This is the sum of $3100.00 (Microsoft invoice) and $208.06 (the two identical East Repair Inc. invoices totaled).

You: List all invoices with a total greater than $2000
🤖 Assistant: There is one invoice with a total greater than $2000:

Invoice Number: INV-0043

Vendor: Microsoft

Total: $3100.0

You: Which is the least expensive invoice?
🤖 Assistant: The least expensive invoice is US-001 from East Repair Inc., with a total of $154.06. Note that there are two identical entries for this invoice.

