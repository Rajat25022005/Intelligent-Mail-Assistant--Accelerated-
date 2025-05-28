import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# In gmail_service.py
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.readonly"
]

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Logs in the user and returns the Gmail API service object.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
# Add this entire function to gmail_service.py

def apply_label_to_email(service, user_id, msg_id, label_name):
    """Applies a label to a specific email."""
    try:
        # First, get the list of all labels to find the ID of our target label
        results = service.users().labels().list(userId=user_id).execute()
        labels = results.get('labels', [])
        label_id = None
        for label in labels:
            if label['name'] == label_name:
                label_id = label['id']
                break

        if not label_id:
            print(f"Label '{label_name}' not found. Please create it in Gmail.")
            return

        # Apply the label to the message
        body = {'addLabelIds': [label_id], 'removeLabelIds': []}
        service.users().messages().modify(userId=user_id, id=msg_id, body=body).execute()
        print(f"Successfully applied label '{label_name}' to message ID {msg_id}")

    except HttpError as error:
        print(f'An error occurred while applying label: {error}')

def get_latest_email(service):
    """Gets the most recent email from the inbox."""
    try:
        # Call the Gmail API to fetch the user's messages
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=1).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No new messages found.")
            return

        msg_id = messages[0]['id']
        # Get the full message details
        message = service.users().messages().get(userId='me', id=msg_id).execute()

        # Extract headers to find the subject
        headers = message['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')

        print(f"Latest email subject: {subject}\n")

    except HttpError as error:
        print(f"An error occurred: {error}")

# ... (add this to your existing gmail_service.py file) ...
from email.mime.text import MIMEText
import base64

def create_draft(service, user_id, message_body, original_message):
    """Create and insert a draft email.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value 'me' can be used to indicate the authenticated user.
      message_body: The body of the email.
      original_message: The original message object to reply to.
    """
    try:
        # Get necessary headers from the original message
        original_headers = original_message['payload']['headers']
        subject = next((h['value'] for h in original_headers if h['name'].lower() == 'subject'), '')
        to = next((h['value'] for h in original_headers if h['name'].lower() == 'from'), '')
        original_msg_id = next((h['value'] for h in original_headers if h['name'].lower() == 'message-id'), '')

        # Create the message
        message = MIMEText(message_body)
        message['to'] = to
        message['subject'] = f"Re: {subject}"
        # Add In-Reply-To and References headers to make it a proper reply
        message['In-Reply-To'] = original_msg_id
        message['References'] = original_msg_id

        # Encode the message in base64
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {'message': {'raw': encoded_message, 'threadId': original_message['threadId']}}

        draft = service.users().drafts().create(userId=user_id, body=create_message).execute()
        print(f"Draft created successfully. Draft ID: {draft['id']}")
        return draft

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
# Add this entire function to the bottom of gmail_service.py

def send_email(service, user_id, message):
    """Send an email message.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value 'me' can be used.
      message: Message to be sent.

    Returns:
      Sent Message.
    """
    try:
        # The message body needs to be a base64url encoded string.
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': raw_message}
        
        sent_message = service.users().messages().send(userId=user_id, body=body).execute()
        print(f"Message sent successfully. Message ID: {sent_message['id']}")
        return sent_message
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

if __name__ == "__main__":
    gmail_service_client = get_gmail_service()
    if gmail_service_client:
        get_latest_email(gmail_service_client)