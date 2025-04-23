DEBUG = False

def groupRows(service, spreadsheet, sheet, start, end):
    request_body = {
        "requests":[
            {
                "addDimensionGroup":{
                    "range":{
                    "sheetId": sheet.id,
                    "dimension": "ROWS",
                    "startIndex": start,
                    "endIndex": end
                    }
                }
            }
        ]
    }
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id,
        body=request_body
    ).execute()

    if DEBUG:
        print('Request body:', request_body)
        print('Response:', response)



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

    if DEBUG:
        print('Request body:', request_body)
        print('Response:', response)


