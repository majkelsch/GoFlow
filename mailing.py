import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import db_control_simple
import json

# Scopes: Only sending email
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    creds = None
    # token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.json downloaded from Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file('credentials_oauth2.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def create_html_message(to, subject, html_content):
    message = MIMEText(html_content, 'html', 'utf-8')  # ← use 'html' instead of 'plain'
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email(to, subject, body):
    service = gmail_authenticate()
    message = create_message(to, subject, body)
    result = service.users().messages().send(userId='me', body=message).execute()
    print(f"Message sent! Message ID: {result['id']}")
    return result

def send_html_email(to, subject, body):
    service = gmail_authenticate()
    message = create_html_message(to, subject, body)
    result = service.users().messages().send(userId='me', body=message).execute()
    print(f"Message sent! Message ID: {result['id']}")
    return result



def generateTaskEmail(html_file_path, data):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_body = file.read().replace('{{data}}', repr(data))
    return html_body

# ---- Run it ----
if __name__ == '__main__':
    #send_email(service, "michal@cloudbusiness.cz", "Test Email", "This is a test email sent via Gmail API and OAuth2.")
    send_html_email("michal@cloudbusiness.cz", "Test HTML", generateTaskEmail('task-listed-employee.html', db_control_simple.get_taskBySupportID("SUP250001")))
    #print(generateTaskEmail('task-listed-employee.html', db_control_simple.get_taskBySupportID("SUP250001")))
