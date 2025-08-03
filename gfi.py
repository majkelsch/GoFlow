# Custom libraries
import gfdb
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

        clientEmails = gfdb.get_all_client_emails()
        clientEmailsList = []
        for record in clientEmails:
            clientEmailsList.append(record['email'])



        rowIndex = 2
        for row in support_data:
            print(row)
            # Change to row[8] when put to production
            if row[9] != 'TRUE' and row[1].lower() in clientEmailsList:
                gfdb.insert_task({
                    "support_id": f"SUP{str(datetime.datetime.now().year)[2:]}{str(gfdb.get_newTaskID()).zfill(4)}",
                    "client": gfdb.get_client(full_name=row[0])['id'],
                    "project": gfdb.get_project(client_id=gfdb.get_client(full_name=row[0])['id'])['id'],
                    "title": "SUPPORT FORM",
                    "description": str(row[4]),
                    "employee": gfdb.get_employee(full_name=app_secrets.get("DEFAULT_SUPPORT_OWNER"))['id'],
                    "priority": gfdb.get_task_priority(name="Low")['id'],
                    "status": gfdb.get_task_status(name="Income")['id'],
                    "arrived": datetime.datetime.now().replace(microsecond=0),
                    "due": datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=7),
                    "hidden": False,
                    "duration": 0
                })
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
            if gfdb.exists_email(email_id) == False:

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


                gfdb.insert_email({
                    "email_id": email_id,
                    "sender": sender,
                    "subject": subject,
                    "content": content,
                    "date": date.replace(microsecond=0)
                })
            
        except HttpError as error:
            print(f'[{datetime.datetime.now()}] An error occurred: {error}')
            break
    
    gfdb.transfer_emailsToTasks()

