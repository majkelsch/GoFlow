from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
load_dotenv()
from db_control_simple import *
import datetime
import re

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



def lookForProjectBySender(sender):
    session = db_init()
    match = re.search(r'<(.*?)>', sender)
    if match:
        sender = match.group(1)
    else:
        print("No email address found.")

    try:
        project = session.query(Projects).filter_by(email=sender, ignore=0).first()
        if project:
            return str(project.project_name)
        else:
            return None
    except Exception as e:
        print(f"Chyba při hledání projektu podle odesílatele: {e}")
        return None



def get_new_tasks_from_gmail():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_creds = creds.with_subject(USER_EMAIL_TO_IMPERSONATE)
    service = build('gmail', 'v1', credentials=delegated_creds)
    try:
        messages = []
        page_token = None
        while True:
            params = {'userId': 'me', 'labelIds': ['INBOX']}
            if page_token:
                params['pageToken'] = page_token
            results = service.users().messages().list(**params).execute()
            messages.extend(results.get('messages', []))
            page_token = results.get('nextPageToken')
            if not page_token:
                break

        if not messages:
            print(f'Ve schránce uživatele {USER_EMAIL_TO_IMPERSONATE} nejsou žádné nové zprávy.')
        else:
            print(f'Zpracovávám nové zprávy ve schránce uživatele {USER_EMAIL_TO_IMPERSONATE}:')
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']
                subject = next(header['value'] for header in headers if header['name'] == 'Subject')
                sender = next(header['value'] for header in headers if header['name'] == 'From')
                project = lookForProjectBySender(sender)
                if project:
                    createTask_DB({
                    'support_id': message['id'],
                    'client': sender,
                    'project': project,
                    'title': subject,
                    'description': 'Random',
                    'owner': 'Daniel Nevrklo',
                    'priority': 'Low',
                    'status': 'Income',
                    'arrived': datetime.datetime.now(),
                    'duration': 0.0,
                    'started': None,
                    'finished': None
                })
                #else:
                #    print(f'Projekt pro odesílatele {sender} nebyl nalezen. Zpráva přeskočena.')
                

    except Exception as e:
        print(f"Chyba při přístupu k Gmailu: {e}")

get_new_tasks_from_gmail()




