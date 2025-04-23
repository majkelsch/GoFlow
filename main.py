import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
from gf_utils import *
from datetime import datetime


# Setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

CREDS = ServiceAccountCredentials.from_json_keyfile_name("goflow-454119-ab42a2f3f42d.json", SCOPE)
DEBUG = True

Run = True
UpdateTime = 10


client = gspread.authorize(CREDS)
service = build('sheets', 'v4', credentials=CREDS)





if DEBUG:
    print(f"[{datetime.now()}] Opening spreadsheets...")

# Open spreadsheets
# GoFlow
spreadsheet_GoFlow = client.open_by_key("1TeE3sE2t72mJJ9vGxvJRM2dk2f2zgdiWu8Uhmd7vBBU")
sheet_GoFlow = spreadsheet_GoFlow.worksheet("GoFlow")
system_GoFlow = spreadsheet_GoFlow.worksheet("System")
command = system_GoFlow.get_all_values()[0][7]
#Solidpixels
spreadsheet_Solidpixels = client.open_by_key("1igKn8Qc6D2arQC9zyQuSMolx3eSmUxbM0Q_LlBDXKk4")
sheet_Solidpixels = spreadsheet_Solidpixels.worksheet("Solidpixels")

if DEBUG:
    print(f"[{datetime.now()}] Spreadsheets opened...")

# FUNCTIONS
def syncSupport():
    data = sheet_Solidpixels.get_all_values()
    data.pop(0)

    lastindex = int(system_GoFlow.get_all_values()[0][1])
    defOwner = system_GoFlow.get_all_values()[5][1]

    index = 0
    for row in data:
        if row[7] != "TRUE":
            sheet_Solidpixels.update_cell(index + 2, 7, f"SUP{str(datetime.now().year)[2:]}{str(lastindex).zfill(4)}")
            sheet_Solidpixels.update_cell(index + 2, 8, True)
            taskData = [f"SUP{str(datetime.now().year)[2:]}{str(lastindex).zfill(4)}", row[0], row[2], "SUPPORT", defOwner, "Low", "Income", 0, "", "", row[4]]
            createTask(service, spreadsheet_GoFlow, sheet_GoFlow, 1, taskData)
            lastindex += 1
            time.sleep(3)
        index += 1
    system_GoFlow.update_cell(1, 2, lastindex)

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






while Run == True:
    if DEBUG:
        print(f"[{datetime.now()}] Syncing...")
    console()
    sync()
    time.sleep(UpdateTime)

system_GoFlow.update_cell(1, 8, "")
print(f"[{datetime.now()}] ### Stop ###")




























#groupRows(spreadsheetID.id, sheet_GoFlow, 1, 10)

#taskData = ["SWB250001", "Macháček", "Autoškola Zdice", "Změny", "XYZ", "@Michal Schenk", "Low", "Done", "20", "15.04.2025", "15.04.2025"]
#createTask(spreadsheet_GoFlow, sheet_GoFlow, 1, taskData)


#for i in range(20):
#    createTask(spreadsheet_GoFlow, sheet_GoFlow, 1, [f"SWB25{i}", "Macháček", "Autoškola Zdice", "Změny", "XYZ", "@Michal Schenk", "Low", "Done", "20", "15.04.2025", "15.04.2025"])
#    time.sleep(0.5)









