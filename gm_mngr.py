# Custom Libs
import app_secrets

# Libs
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64



















######################

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
GMAIL_CREDS = service_account.Credentials.from_service_account_file("credentials.json", scopes=GMAIL_SCOPES)
USER_EMAIL_TO_IMPERSONATE = app_secrets.get("GOOGLE_SUPPORT_EMAIL")
delegated_creds = GMAIL_CREDS.with_subject(USER_EMAIL_TO_IMPERSONATE)
gmail_service = build('gmail', 'v1', credentials=delegated_creds)


######################

def getService():
    """
    Returns the gmail service object

    Parameters
    ----------
        

    Returns
    -------
        out
            `gmail_service` object
    """
    return gmail_service


def extractTextFromPayload(payload):
    """
    Returns the text content of the gmail message

    Parameters
    ----------
        payload
            The payload object

    Returns
    -------
        str
            Text content of the message
    """
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'body' in part and 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data'].encode('utf-8')).decode('utf-8', errors='ignore')
            if 'parts' in part:
                recursive_text = extractTextFromPayload(part)
                if recursive_text:
                    return recursive_text
    elif 'body' in payload and 'data' in payload['body']:
        if payload['mimeType'] == 'text/plain':
            return base64.urlsafe_b64decode(payload['body']['data'].encode('utf-8')).decode('utf-8', errors='ignore')
    return None
