import uvicorn
from fastapi import FastAPI, HTTPException
from email.mime.text import MIMEText
import base64
from gmail_service import get_gmail_service, send_email, apply_label_to_email
from llm_handler import classify_email_intent_local, generate_reply_local
from rag_service import query_rag
from main import get_email_body 

app = FastAPI(
    title="Intelligent Mail Assistant API",
    description="An API to process incoming emails, generate replies using an LLM, and send them.",
    version="1.0.0"
)

def process_email_for_server(service, message_info):
    """
    Contains the logic to process one single email automatically without user input.
    Returns a string describing the outcome.
    """
    msg_id = message_info['id']
    message_data = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

    email_content = get_email_body(message_data)
    original_sender = next((h['value'] for h in message_data['payload']['headers'] if h['name'].lower() == 'from'), 'No Sender')
    original_subject = next((h['value'] for h in message_data['payload']['headers'] if h['name'].lower() == 'subject'), 'No Subject')

    outcome = f"Processing email from: {original_sender} | Subject: {original_subject}. "

    email_content_for_llm = f"Subject: {original_subject}\nFrom: {original_sender}\n\n{email_content}"
    classification = classify_email_intent_local(email_content_for_llm)
    
    outcome += f"Classification: {classification.get('intent', 'unknown')}. "

    if classification and classification.get('intent') != 'spam':
        intent = classification.get('intent')
        context_for_llm = None
        
        if intent == 'information_request':
            retrieved_docs = query_rag(email_content_for_llm)
            if retrieved_docs:
                context_for_llm = "Relevant notes:\n" + "\n".join(retrieved_docs)

        reply_body = generate_reply_local(email_content_for_llm, intent, context=context_for_llm)
        
        if reply_body:
            # The server sends the email automatically
            message = MIMEText(reply_body)
            message['to'] = original_sender
            message['subject'] = f"Re: {original_subject}"
            original_msg_id_header = next((h['value'] for h in message_data['payload']['headers'] if h['name'].lower() == 'message-id'), '')
            if original_msg_id_header:
                message['In-Reply-To'] = original_msg_id_header
                message['References'] = original_msg_id_header
            
            send_email(service, 'me', message)
            outcome += "AI-generated reply sent."
        else:
            outcome += "Reply generation failed."
    else:
        outcome += "Email classified as spam or could not be classified. No action taken."

    # Apply the label to prevent re-processing
    apply_label_to_email(service, 'me', msg_id, 'ProcessedByAI')
    return outcome


@app.post("/process-emails")
async def trigger_email_processing():
    """
    This endpoint triggers a one-time check for new emails.
    It finds all unread emails, processes them, sends replies, and applies a label.
    """
    print("API endpoint /process-emails triggered.")
    try:
        service = get_gmail_service()
        if not service:
            raise HTTPException(status_code=500, detail="Could not connect to Gmail service.")

        results = service.users().messages().list(
            userId='me', 
            labelIds=['INBOX'],
            q="-label:ProcessedByAI"
        ).execute()
        
        messages_to_process = results.get('messages', [])
        
        if not messages_to_process:
            return {"status": "success", "message": "No new mail to process."}

        processing_outcomes = []
        for message_info in messages_to_process:
            outcome = process_email_for_server(service, message_info)
            processing_outcomes.append(outcome)
            print(f"-> {outcome}")

        return {
            "status": "success",
            "message": f"Processed {len(messages_to_process)} email(s).",
            "details": processing_outcomes
        }

    except Exception as e:
        print(f"An unexpected error occurred in the API endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")



if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)