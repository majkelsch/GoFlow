import html.parser
import gspread
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import dotenv
from datetime import datetime
import os
import db_control_simple
from db_control_simple import TaskDict
import base64
import email
import html
from dateutil import parser as date_parser

import json


# Setup
SHEET_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

dotenv.load_dotenv()

SHEET_CREDS = service_account.Credentials.from_service_account_file("credentials.json", scopes=SHEET_SCOPES)
GMAIL_CREDS = service_account.Credentials.from_service_account_file("credentials.json", scopes=GMAIL_SCOPES)
client = gspread.authorize(SHEET_CREDS)

DEBUG = False
UpdateTime = 300
GOFLOW_ID = os.getenv("GOFLOW_SPREADSHEET_ID")
SOLIDPIXELS_ID = os.getenv("SOLIDPIXELS_SPREADSHEET_ID")
DEFAULT_SUPPORT_OWNER = os.getenv("DEFAULT_SUPPORT_OWNER")

if DEFAULT_SUPPORT_OWNER is None:
    raise ValueError("DEFAULT_SUPPORT_OWNER environment variable is not set or is missing.")
USER_EMAIL_TO_IMPERSONATE = os.getenv("GOOGLE_SUPPORT_EMAIL")
if USER_EMAIL_TO_IMPERSONATE is None:
    raise ValueError("USER_EMAIL_TO_IMPERSONATE environment variable is not set or is missing.")


sheet_service = build('sheets', 'v4', credentials=SHEET_CREDS)

delegated_creds = GMAIL_CREDS.with_subject(USER_EMAIL_TO_IMPERSONATE)
gmail_service = build('gmail', 'v1', credentials=delegated_creds)



if SOLIDPIXELS_ID is None:
    raise ValueError("SOLIDPIXELS_SPREADSHEET_ID environment variable is not set or is missing.")
spreadsheet_Solidpixels = client.open_by_key(SOLIDPIXELS_ID)
sheet_Solidpixels = spreadsheet_Solidpixels.worksheet("Solidpixels")


def getSolidpixelsData():
    try:
        support_data = sheet_Solidpixels.get_all_values() # 1 Read request
        support_data.pop(0)

        for row in support_data:
            if row[8] != 'TRUE':
                newData: TaskDict = {
                    "support_id": f"SUP{str(datetime.now().year)[2:]}{str(db_control_simple.get_newTaskID()).zfill(4)}",
                    "client": str(row[0]),
                    "project": str(row[2]),
                    "title": "SUPPORT FORM",
                    "description": str(row[4]),
                    "owner": str(DEFAULT_SUPPORT_OWNER),
                    "priority": "Low",
                    "status": "Income",
                    "arrived": datetime.now().replace(microsecond=0),
                    "duration": 0,
                    "started": None,
                    "finished": None
                }
                db_control_simple.createTask_DB(newData)

    except Exception as e:
        print(f"[{datetime.now()}] Error in syncSupport: {e}")




def extractTextFromPayload(message_payload):
    if 'parts' in message_payload:
        for part in message_payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'body' in part and 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data'].encode('utf-8')).decode('utf-8', errors='ignore')
            if 'parts' in part:
                recursive_text = extractTextFromPayload(part)
                if recursive_text:
                    return recursive_text
    elif 'body' in message_payload and 'data' in message_payload['body']:
        if message_payload['mimeType'] == 'text/plain':
            return base64.urlsafe_b64decode(message_payload['body']['data'].encode('utf-8')).decode('utf-8', errors='ignore')
    return None


def getGmailData():
    messages = []
    page_token = None
    while True:
        try:
            response = gmail_service.users().messages().list(userId='me', pageToken=page_token, labelIds=['INBOX']).execute()
            if 'messages' in response:
                messages.extend(response['messages'])
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break
        except HttpError as error:
            print(f'An error occurred: {error}')
            break
    
    for message in messages:
        client = "Unknown"
        subject = "No Subject"
        email_id = "No ID"
        try:
            response = gmail_service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            
            email_id = response['id']
            if db_control_simple.check_existingMailID(email_id) == False:

                description = extractTextFromPayload(response['payload'])
                if description == None:
                    description = "Unknown"

                for i in response['payload']['headers']:
                    if i['name'] == "From":
                        client = i['value']
                        print(client)
                    if i['name'] == "Subject":
                        subject = i['value']
                        print(subject)
                    if i['name'] == "Date":
                        date_str = i['value'].replace(" (CEST)", "").replace(" (GMT)", "").replace(" (CET)", "").replace(" (PST)", "").replace(" GMT", "")
                        try:
                            date = date_parser.parse(date_str)
                        except Exception as e:
                            print(f"Failed to parse date: {date_str}, error: {e}")
                            date = datetime.now()
                        print(date)

                db_control_simple.createTask_DB({
                    "support_id": f"SUP{str(datetime.now().year)[2:]}{str(db_control_simple.get_newTaskID()).zfill(4)}",
                    "client": client,
                    "project": subject,
                    "title": subject,
                    "description": description,
                    "owner": DEFAULT_SUPPORT_OWNER,  # type: ignore
                    "priority": "Low",
                    "status": "Income",
                    "arrived": date.replace(microsecond=0), # type: ignore
                    "duration": 0,
                    "started": None,
                    "finished": None,
                    "email_id": email_id
                })
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            break


    


       
#getSolidpixelsData()
getGmailData()