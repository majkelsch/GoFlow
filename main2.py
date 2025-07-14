#str(datetime.strptime(str(datetime.now() + timedelta(days=7)), "%Y-%m-%d %H:%M:%S.%f").replace(microsecond=0))

import html.parser
import gspread
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import dotenv
from datetime import datetime, timedelta
import os
import db_control_simple
from db_control_simple import TaskDict
import mailing

import base64
import email
from email.message import EmailMessage
import html
from dateutil import parser as date_parser
import itertools

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

if GOFLOW_ID is None:
    raise ValueError("GOFLOW_ID environment variable is not set or is missing.")
spreadsheet_GoFlow = client.open_by_key(GOFLOW_ID)
# Change to worksheet("GoFlow") when put to production
sheet_GoFlow = spreadsheet_GoFlow.worksheet("EXP")


def getSolidpixelsData():
    try:
        support_data = sheet_Solidpixels.get_all_values()
        support_data.pop(0)

        rowIndex = 2
        for row in support_data:
            # Change to row[8] when put to production
            if row[9] != 'TRUE':
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
                    "due": datetime.now().replace(microsecond=0) + timedelta(days=7),
                    "duration": 0,
                    "started": None,
                    "finished": None,
                    "last_edit_by": "GoFlow Importer"
                }
                db_control_simple.createTask_DB(newData)
                time.sleep(1)
                # Change to sheet_Solidpixels.update_cell(rowIndex, 9, True) when put to production
                sheet_Solidpixels.update_cell(rowIndex, 10, True)
                rowIndex += 1

    except Exception as e:
        print(f"[{datetime.now()}] Error in getSolidpixelsData: {e}")




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
        except HttpError as e:
            print(f'[{datetime.now()}] Error in getGmailData {e}')
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
                        #print(client)
                    if i['name'] == "Subject":
                        subject = i['value']
                        #print(subject)
                    if i['name'] == "Date":
                        date_str = i['value'].replace(" (CEST)", "").replace(" (GMT)", "").replace(" (CET)", "").replace(" (PST)", "").replace(" GMT", "")
                        try:
                            date = date_parser.parse(date_str)
                        except Exception as e:
                            print(f"[{datetime.now()}] Failed to parse date: {date_str}, error: {e}")
                            date = datetime.now()
                        #print(date)

                db_control_simple.createTask_DB({
                    "support_id": f"SUP{str(datetime.now().year)[2:]}{str(db_control_simple.get_newTaskID()).zfill(4)}",
                    "client": client,
                    "project": client,
                    "title": subject,
                    "description": description,
                    "owner": DEFAULT_SUPPORT_OWNER,  # type: ignore
                    "priority": "Low",
                    "status": "Income",
                    "arrived": date.replace(microsecond=0), # type: ignore
                    "due": date.replace(microsecond=0) + timedelta(days=7), # type: ignore
                    "duration": 0,
                    "started": None,
                    "finished": None,
                    "email_id": email_id,
                    "last_edit_by": "GoFlow Importer"
                })
            
        except HttpError as error:
            print(f'[{datetime.now()}] An error occurred: {error}')
            break

def createTask(data):
    body = {
        "requests": [
            {
                "insertDimension": {
                    "range": {
                        "sheetId": sheet_GoFlow.id,
                        "dimension": "ROWS",
                        "startIndex": 1,
                        "endIndex": 2
                    },
                    "inheritFromBefore": True
                }
            },
            {
                "updateCells": {
                    "rows": [
                        {
                            "values": [
                                {
                                    "userEnteredValue": {
                                        "stringValue": data['support_id']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": data['client']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": data['project']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": data['title']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": DEFAULT_SUPPORT_OWNER
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": data['priority']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": data['status']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": str(data['arrived'])
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": str(data['due'])
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "numberValue": data['duration']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "numberValue": 0
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": str(data['started']) if data['started'] is not None else ""
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": str(data['finished']) if data['finished'] is not None else ""
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": data['description'][:5000]
                                    }
                                }
                            ]
                        }
                    ],
                    "fields": "*",
                    "start": {
                        "sheetId": sheet_GoFlow.id,
                        "rowIndex": 1,
                        "columnIndex": 0
                    }
                }
            },
            {
                "updateDimensionProperties": {
                    "properties": {
                        "pixelSize": 28
                    },
                    "fields": "*",
                    "range": {
                        "sheetId": sheet_GoFlow.id,
                        "dimension": "ROWS",
                        "startIndex": 1,
                        "endIndex": 2
                    }
                }
            }
        ]
    }

    response = sheet_service.spreadsheets().batchUpdate(
        spreadsheetId=GOFLOW_ID,
        body=body
    ).execute()

def exportTasksToSheets():
    tasks = db_control_simple.get_allTasks()
    tasksID = []
    for x in tasks:
        tasksID.append(x['support_id'])
    tasksID = set(tasksID)
    existingTasksID = list(itertools.chain.from_iterable(sheet_GoFlow.get_values(f"A2:A{sheet_GoFlow.row_count}")))
    existingTasksID = set(existingTasksID)

    difference = tasksID.symmetric_difference(existingTasksID)

    pendingTasks = sorted(list(difference))
    for id in pendingTasks:
        taskData = db_control_simple.get_taskBySupportID(id)
        time.sleep(2)
        createTask(taskData) 

    
    




getSolidpixelsData()
getGmailData()
exportTasksToSheets()