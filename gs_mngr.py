# Custom Libs
import app_secrets

# Libs
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread
import sys
import datetime




############################









SHEET_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
SHEET_CREDS = service_account.Credentials.from_service_account_file("credentials.json", scopes=SHEET_SCOPES)
client = gspread.authorize(SHEET_CREDS)
sheet_service = build('sheets', 'v4', credentials=SHEET_CREDS)










############################

def getService():
    return sheet_service


def getSheet(spreadsheet_id:str, sheet_name:str):
    """
    Returns the sheet object

    Parameters
    ----------
        spreadsheet_id : string
            Key to use for search in the `.env` file
        sheet_name : string
            Name of the sheet in the Google Spreadsheet

    Returns
    -------
        out
            `gspread.worksheet.Worksheet` object
    """
    try:
        spreadsheet = client.open_by_key(app_secrets.get(spreadsheet_id))
        sheet = spreadsheet.worksheet(sheet_name)
        return sheet
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in gs_mngmnt.py: {e}")
        sys.exit(1)
    


