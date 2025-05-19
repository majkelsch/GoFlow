import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import json

from datetime import datetime
import logging
import sys

logging.basicConfig(filename='goflow.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
with open("config.json") as f:
    config = json.load(f)

# Setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

CREDS = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
DEBUG = config["DEBUG"]
UpdateTime = config["UpdateTime"]
GOFLOW_ID = config["GOFLOW_SPREADSHEET_ID"]
SOLIDPIXELS_ID = config["SOLIDPIXELS_SPREADSHEET_ID"]

Run = True


client = gspread.authorize(CREDS)
service = build('sheets', 'v4', credentials=CREDS)

if DEBUG:
    print(f"[{datetime.now()}] Opening spreadsheets...")
# Open spreadsheets
# GoFlow
spreadsheet_GoFlow = client.open_by_key(GOFLOW_ID)
sheet_GoFlow = spreadsheet_GoFlow.worksheet("GoFlow")
system_GoFlow = spreadsheet_GoFlow.worksheet("System")
command = system_GoFlow.get_all_values()[0][7]
#Solidpixels
spreadsheet_Solidpixels = client.open_by_key(SOLIDPIXELS_ID)
sheet_Solidpixels = spreadsheet_Solidpixels.worksheet("Solidpixels")

if DEBUG:
    print(f"[{datetime.now()}] Spreadsheets opened...")

# FUNCTIONS
def createTask(service, spreadsheet, sheet, row, taskData):
    request_body = {
        "requests": [
            {
                "insertDimension": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "ROWS",
                        "startIndex": row,
                        "endIndex": row + 1
                    },
                    "inheritFromBefore": True
                }
            },
            {
                "updateCells": {
                    "rows": {
                        "values": [
                            {
                                "userEnteredValue": {
                                    "stringValue": str(value)
                                },
                                "userEnteredFormat": {
                                    "horizontalAlignment": "LEFT",
                                    "verticalAlignment": "TOP",
                                    "wrapStrategy": "WRAP"
                                }
                            } for value in taskData
                        ]
                    },
                    "fields": "*",
                    "start": {
                        "sheetId": sheet.id,
                        "rowIndex": row,
                        "columnIndex": 0
                    }
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "ROWS",
                        "startIndex": row,  
                        "endIndex": row + 1 
                    },
                    "properties": {
                        "pixelSize": 21
                    },
                    "fields": "pixelSize"
                }
            }
        ]
    }
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id,
        body=request_body
    ).execute()

def syncSupport():
    try:
        system_GoFlow.update_cell(5, 2, True)
        data = sheet_Solidpixels.get_all_values()
        data.pop(0)

        lastindex = int(system_GoFlow.get_all_values()[0][1])
        defOwner = system_GoFlow.get_all_values()[5][1]
        success = 0
        total = 0

        updates = []
        task_updates = []

        for index, row in enumerate(data):
            if len(row) > 7 and row[7] != "TRUE":
                total += 1
                try:
                    task_id = f"SUP{str(datetime.now().year)[2:]}{str(lastindex).zfill(4)}"
                    updates.append({
                        "range": f"Solidpixels!G{index + 2}:H{index + 2}",
                        "values": [[task_id, True]]
                    })
                    taskData = [task_id, row[0], row[2], "SUPPORT", defOwner, "Low", "Income", datetime.now().replace(microsecond=0), 0, "", "", row[4]]
                    task_updates.append((1, taskData))
                    lastindex += 1
                    success += 1
                except Exception as e:
                    print(f"[{datetime.now()}] Error processing row {index}: {e}")
                    logging.error(f"Error processing row {index}: {e}")
            #else:
            #    print(f"[{datetime.now()}] Skipping invalid row: {row}")

        # Batch update for Solidpixels sheet
        if updates:
            body = {"valueInputOption": "USER_ENTERED", "data": updates}
            service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_Solidpixels.id, body=body).execute()

        # Batch create tasks
        for row, taskData in task_updates:
            createTask(service, spreadsheet_GoFlow, sheet_GoFlow, row, taskData)

        system_GoFlow.update_cell(1, 2, lastindex)
        system_GoFlow.update_cell(5, 2, False)
        system_GoFlow.update_cell(2, 8, f"[{datetime.now()}] Synced Successfully [{success}/{total}]")
        logging.info(f"Synced Successfully [{success}/{total}]")
    except Exception as e:
        print(f"[{datetime.now()}] Error in syncSupport: {e}")
        logging.error(f"Error in syncSupport: {e}")

def console():
    command = system_GoFlow.get_all_values()[0][7]

    if command == "end":
        global Run
        Run = False
        system_GoFlow.update_cell(2, 8, f"[{datetime.now()}] Ended")

    if "setupdatetime" in command:
        global UpdateTime
        UpdateTime = int(command.split(" ")[1])
        system_GoFlow.update_cell(2, 8, f"[{datetime.now()}] Update time set to {UpdateTime} seconds")
        
    system_GoFlow.update_cell(1, 8, "")
    

def sync():
    syncSupport()


def main_loop():
    global Run
    try:
        while Run:
            if DEBUG:
                print(f"[{datetime.now()}] Syncing...")
            console()
            sync()
            time.sleep(UpdateTime)
    except KeyboardInterrupt:
        print(f"[{datetime.now()}] Interrupted by user. Shutting down...")
        raise
    except Exception as e:
        logging.error(f"An error occurred in main_loop: {e}")
        raise
    finally:
        try:
            system_GoFlow.update_cell(1, 8, "")
        except Exception as e:
            logging.error(f"Failed to update cell in finally block: {e}")
        print(f"[{datetime.now()}] ### Stop ###")

while True:
    try:
        main_loop()
        break  # Exit if main_loop finishes normally (e.g., Run set to False)
    except KeyboardInterrupt:
        break
    except Exception as e:
        wait_minutes = 5
        print(f"[{datetime.now()}] Fatal error occurred. Restarting in {wait_minutes} minutes...")
        logging.error(f"Fatal error, restarting in {wait_minutes} minutes: {e}")
        time.sleep(wait_minutes * 60)




























#groupRows(spreadsheetID.id, sheet_GoFlow, 1, 10)

#taskData = ["SWB250001", "Macháček", "Autoškola Zdice", "Změny", "XYZ", "@Michal Schenk", "Low", "Done", "20", "15.04.2025", "15.04.2025"]
#createTask(spreadsheet_GoFlow, sheet_GoFlow, 1, taskData)


#for i in range(20):
#    createTask(spreadsheet_GoFlow, sheet_GoFlow, 1, [f"SWB25{i}", "Macháček", "Autoškola Zdice", "Změny", "XYZ", "@Michal Schenk", "Low", "Done", "20", "15.04.2025", "15.04.2025"])
#    time.sleep(0.5)









