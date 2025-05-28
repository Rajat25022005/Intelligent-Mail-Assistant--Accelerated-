# 🤖 Intelligent Mail Assistant

An AI-powered Python script that automatically checks a Gmail inbox, classifies emails using a local LLM, and generates context-aware replies. The script can check for new mail in a continuous loop.

## ✨ Features

- **Secure Gmail Integration:** Uses the official Gmail API with OAuth 2.0 to read and send emails.
- **AI-Powered Triage:** Leverages a local LLM (via Ollama) to classify email intent and priority.
- **Context-Aware Replies:** Answers questions by retrieving information from a personal knowledge base and checks Google Calendar availability for meeting requests.
- **Safe Auto-Sending:** Includes a mandatory command-line confirmation step before any AI-generated email is sent.
- **Continuous Operation:** Can run in a loop to check for new emails every 10 minutes, using Gmail labels to prevent re-processing.

## 🔧 Setup & Installation

Follow these steps to set up the project on your local machine.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/intelligent-mail-assistant.git](https://github.com/YOUR_USERNAME/intelligent-mail-assistant.git)
    cd intelligent-mail-assistant
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install and Run Ollama:**
    - Download and install Ollama from the [official website](https://ollama.com/).
    - After installation, ensure the Ollama application is running in the background.

5.  **Download an LLM Model:**
    - Open your terminal and pull a model to use. This project was developed with `gemma2:9b`.
    ```bash
    ollama pull gemma2:9b
    ```
    - You can use other models like `llama3:8b` or `phi3`, but you will need to update the code as shown in the Configuration section below.

6.  **Set Up Google API Credentials:**
    - Follow the Google Cloud instructions to create an OAuth 2.0 Client ID for a **Desktop App**.
    - Download the credentials JSON file.
    - Place this file in your project folder and rename it to exactly `credentials.json`.
    - **Note:** This file is listed in `.gitignore` and must be added manually. Its contents are secret.

7.  **Create Gmail Label:**
    - In your Gmail account, create a new label named exactly `ProcessedByAI`.

8.  **Create Knowledge Base:**
    - Add your personal notes to the `my_notes.txt` file.
    - Run the script to build the database for the first time: `python create_knowledge_base.py`

## ⚙️ Configuration

To use a different LLM model from the one you downloaded, you need to make a small change in the code.

1.  Open the file `llm_handler.py`.
2.  Find the line that specifies the model name.
3.  Change the value of `model` to the name of your desired model. For example:
    ```python
    # Change this line in llm_handler.py
    response = ollama.chat(
        model='gemma2:9b', # <-- Change this value to 'llama3:8b' or another model
        # ... rest of the code
    )
    ```

## 🚀 How to Run

1.  Make sure your local Ollama server is running.
2.  Run the main script from your terminal:
    ```bash
    python main.py
    ```
3.  The first time you run it, a browser window will open for you to authenticate with Google. This will create a `token.json` file.
4.  The script will then run continuously, checking for new mail every 10 minutes. To stop it, press `Ctrl + C`.