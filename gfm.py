# Custom Libs


# Libs
import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import json

###################
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
###################






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
    message = MIMEText(html_content, 'html', 'utf-8')
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

def send_html_email(to:str, subject:str, body:str):
    service = gmail_authenticate()
    message = create_html_message(to, subject, body)
    result = service.users().messages().send(userId='me', body=message).execute()
    print(f"Message sent! Message ID: {result['id']}")
    return result








def generateTaskEmail(html_file_path, data):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_body = file.read().replace('{{data}}', 
                                        f"""<table>
                                                <tr>
                                                    <th>Title:</th>
                                                    <td>{data['title']}</td>
                                                </tr>
                                                <tr>
                                                    <th>Description:</th>
                                                    <td>{data['description']}</td>
                                                </tr>
                                                <tr>
                                                    <th>Client:</th>
                                                    <td>{data['client_id']}</td>
                                                </tr>
                                                <tr>
                                                    <th>Priority:</th>
                                                    <td>{data['priority_id']}</td>
                                                </tr>
                                                <tr>
                                                    <th>Due Date:</th>
                                                    <td>{data['due'].strftime("%d.%m.%Y %H:%M:%S") if str(type(data['due'])) != "<class 'NoneType'>" else "None"}</td>
                                                </tr>
                                            </table>""")
        # I can't stress enough how much I hate 'str(type(data['due'])) != "<class 'NoneType'>"' I want to change it to something more normal but I have no idea how, at least now.
    return html_body


def generateTaskFinishedEmail(html_file_path, task_id):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_body = file.read().replace('{{data}}', 
                                        f"""<p>Váš požadavek vedený pod identifikátorem {task_id} jsme právě vyřídili. Prosíme Vás o kontrolu.</p>""")
    return html_body