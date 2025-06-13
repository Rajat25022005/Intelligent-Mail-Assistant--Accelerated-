
import time
import datetime
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

# Import our custom service functions
from gmail_service import get_gmail_service, send_email, apply_label_to_email
from llm_handler import classify_email_intent_local, generate_reply_local
from rag_service import query_rag

# --- Helper Functions ---
def get_email_body(message):
    if 'parts' in message['payload']:
        parts = message['payload']['parts']
        data = ""
        for part in parts:
            if part.get('mimeType') == 'text/plain' and 'data' in part['body']:
                data = part['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8')
    elif 'data' in message['payload']['body']:
        data = message['payload']['body']['data']
        return base64.urlsafe_b64decode(data).decode('utf-8')
    return ""

def process_single_email(service, message_info):
    """
    Contains the logic to process one single email.
    """
    msg_id = message_info['id']
    
    # Get the full message details
    message_data = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    
    email_content = get_email_body(message_data)
    original_sender = next((h['value'] for h in message_data['payload']['headers'] if h['name'].lower() == 'from'), 'No Sender')
    original_subject = next((h['value'] for h in message_data['payload']['headers'] if h['name'].lower() == 'subject'), 'No Subject')

    print(f"\n-> Processing email from: {original_sender} | Subject: {original_subject}")

    # Classify, get context, and generate a reply
    email_content_for_llm = f"Subject: {original_subject}\nFrom: {original_sender}\n\n{email_content}"
    classification = classify_email_intent_local(email_content_for_llm)
    print(f"-> Classification: {classification}")

    if classification and classification.get('intent') != 'spam':
        intent = classification.get('intent')
        context_for_llm = None
        
        # Add context logic (RAG, Calendar)
        if intent == 'meeting_request':
            # Add calendar checking logic here if desired
            pass
        elif intent == 'information_request':
            retrieved_docs = query_rag(email_content_for_llm)
            if retrieved_docs:
                context_for_llm = "Relevant notes:\n" + "\n".join(retrieved_docs)

        reply_body = generate_reply_local(email_content_for_llm, intent, context=context_for_llm)
        
        if reply_body:
            # --- SAFETY CONFIRMATION STEP ---
            print("\n" + "="*50)
            print("!! AI-GENERATED REPLY TO BE SENT !!")
            print(f"   RECIPIENT: {original_sender}")
            print("="*50)
            print(reply_body)
            print("="*50)

            confirmation = input(">>> Send this reply? (yes/no): ")

            if confirmation.lower() == 'yes':
                print("\nUser confirmed. Sending email...")
                message = MIMEText(reply_body)
                message['to'] = original_sender
                message['subject'] = f"Re: {original_subject}"
                original_msg_id_header = next((h['value'] for h in message_data['payload']['headers'] if h['name'].lower() == 'message-id'), '')
                if original_msg_id_header:
                    message['In-Reply-To'] = original_msg_id_header
                    message['References'] = original_msg_id_header
                send_email(service, 'me', message)
            else:
                print("\nSend operation cancelled by user.")
    else:
        print("-> Email is spam or could not be classified. No action taken.")

    # IMPORTANT: Apply the label regardless of action to prevent re-processing
    apply_label_to_email(service, 'me', msg_id, 'ProcessedByAI')


def main_loop():
    """The main continuous loop of the application."""
    print("Starting Intelligent Mail Assistant Service...")
    service = get_gmail_service()
    if not service:
        print("Could not connect to Gmail. Exiting.")
        return

    while True:
        try:
            print(f"\n--- Checking for new mail at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            # Fetch only messages that are in INBOX and DO NOT have the 'ProcessedByAI' label
            results = service.users().messages().list(
                userId='me', 
                labelIds=['INBOX'],
                q="-label:ProcessedByAI" # The magic query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("No new mail to process.")
            else:
                print(f"Found {len(messages)} new email(s). Processing one by one...")
                for message_info in messages:
                    process_single_email(service, message_info)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Continuing...")

        # Wait for 10 minutes before the next check
        print("\n Waiting for 10 minutes (600 seconds) before next check")
        time.sleep(600)


if __name__ == '__main__':
    main_loop()
