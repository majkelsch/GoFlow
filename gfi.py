# Custom libraries
import db_control_simple
import app_secrets
import gs_mngr
import gm_mngr

# Libs
import datetime
import time
from googleapiclient.errors import HttpError
from dateutil import parser as date_parser
import json
















##############################

def getSolidpixelsData():
    """
    Get data from SP sheets and insert them to the DB
    """
    try:
        support_data = gs_mngr.getSheet("SOLIDPIXELS_SPREADSHEET_ID", "Solidpixels").get_all_values()
        support_data.pop(0)
        print(support_data)

        rowIndex = 2
        for row in support_data:
            # Change to row[8] when put to production
            if row[9] != 'TRUE':
                newData: db_control_simple.TaskDict = {
                    "support_id": f"SUP{str(datetime.datetime.now().year)[2:]}{str(db_control_simple.get_newTaskID()).zfill(4)}",
                    "client": str(row[0]),
                    "project": str(row[2]),
                    "title": "SUPPORT FORM",
                    "description": str(row[4]),
                    "employee": str(app_secrets.get("DEFAULT_SUPPORT_OWNER")),
                    "priority": "Low",
                    "status": "Income",
                    "arrived": datetime.datetime.now().replace(microsecond=0),
                    "due": datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=7),
                    "duration": 0,
                    "started": None,
                    "finished": None,
                    "email_id": None,
                    "last_edit_by": "GoFlow Importer"
                }
                db_control_simple.createTask_DB(newData)
                time.sleep(1)
                # Change to sheet_Solidpixels.update_cell(rowIndex, 9, True) when put to production
                gs_mngr.getSheet("SOLIDPIXELS_SPREADSHEET_ID", "Solidpixels").update_cell(rowIndex, 10, True)
                rowIndex += 1

    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in getSolidpixelsData: {e}")




def getGmailData():
    """
    Get data from Gmail and insert them to the DB
    """

    messages = []
    page_token = None
    while True:
        try:
            response = gm_mngr.getService().users().messages().list(userId='me', pageToken=page_token, labelIds=['INBOX']).execute()
            if 'messages' in response:
                messages.extend(response['messages'])
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break
        except HttpError as e:
            print(f'[{datetime.datetime.now()}] Error in getGmailData {e}')
            break
    
    for message in messages:
        sender = "Unknown"
        subject = "No Subject"
        email_id = "No ID"
        try:
            response = gm_mngr.getService().users().messages().get(userId='me', id=message['id'], format='full').execute()
            
            email_id = response['id']
            if db_control_simple.exists_email(email_id) == False:

                content = gm_mngr.extractTextFromPayload(response['payload'])
                if content == None:
                    content = "Unknown"

                date = datetime.datetime.now()
                for i in response['payload']['headers']:
                    if i['name'] == "From":
                        sender = i['value']
                    if i['name'] == "Subject":
                        subject = i['value']
                    if i['name'] == "Date":
                        date_str = i['value'].replace(" (CEST)", "").replace(" (GMT)", "").replace(" (CET)", "").replace(" (PST)", "").replace(" GMT", "")
                        try:
                            date = date_parser.parse(date_str)
                        except Exception as e:
                            print(f"[{datetime.datetime.now()}] Failed to parse date: {date_str}, error: {e}")
                            date = datetime.datetime.now()


                db_control_simple.insert_email({
                    "email_id": email_id,
                    "sender": sender,
                    "subject": subject,
                    "content": content,
                    "date": date.replace(microsecond=0)
                })
            
        except HttpError as error:
            print(f'[{datetime.datetime.now()}] An error occurred: {error}')
            break
    
    db_control_simple.transfer_emailsToTasks()
