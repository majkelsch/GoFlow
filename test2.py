from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
load_dotenv()

# Cesta k JSON souboru s klíčem service accountu
SERVICE_ACCOUNT_FILE = 'credentials.json'

# E-mailová adresa uživatele, jehož schránku chcete vylistovat
USER_EMAIL_TO_IMPERSONATE = os.getenv("GOOGLE_SUPPORT_EMAIL")

# Rozsahy (scopes) pro Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def list_gmail_inbox():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Delegování v celé doméně - service account se vydává za konkrétního uživatele
    delegated_creds = creds.with_subject(USER_EMAIL_TO_IMPERSONATE)

    service = build('gmail', 'v1', credentials=delegated_creds)

    try:
        # Volání API pro získání seznamu zpráv
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = results.get('messages', [])

        if not messages:
            print(f'Ve schránce uživatele {USER_EMAIL_TO_IMPERSONATE} nejsou žádné zprávy.')
        else:
            print(f'Zprávy ve schránce uživatele {USER_EMAIL_TO_IMPERSONATE}:')
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                # Zde můžete zpracovat hlavičky, tělo zprávy atd.
                headers = msg['payload']['headers']
                subject = next(header['value'] for header in headers if header['name'] == 'Subject')
                sender = next(header['value'] for header in headers if header['name'] == 'From')
                print(f'- Předmět: {subject}, Od: {sender}')

    except Exception as e:
        print(f"Chyba při přístupu k Gmailu: {e}")

if __name__ == '__main__':
    list_gmail_inbox()