# Custom Lib
import gs_mngr
import app_secrets
import db_control_simple
import gfm

# Libs
import itertools
import time























########################


def createTask(data):
    body = {
        "requests": [
            {
                "insertDimension": {
                    "range": {
                        "sheetId": gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "EXP").id,
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
                                        "stringValue": data['owner'] or app_secrets.get("DEFAULT_SUPPORT_OWNER")
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
                        "sheetId": gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "EXP").id,
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
                        "sheetId": gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "EXP").id,
                        "dimension": "ROWS",
                        "startIndex": 1,
                        "endIndex": 2
                    }
                }
            }
        ]
    }

    response = gs_mngr.getService().spreadsheets().batchUpdate(
        spreadsheetId=app_secrets.get("GOFLOW_SPREADSHEET_ID"),
        body=body
    ).execute()

def exportTasksToSheets():
    tasks = db_control_simple.get_allTasks()
    if len(tasks) != 0:
        tasksID = []
        for x in tasks:
            tasksID.append(x['support_id'])
        tasksID = set(tasksID)
        existingTasksID = list(itertools.chain.from_iterable(gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "EXP").get_values(f'A2:A{gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "EXP").row_count}')))
        existingTasksID = set(existingTasksID)
        

        difference = tasksID.symmetric_difference(existingTasksID)

        pendingTasks = sorted(list(difference))
        for id in pendingTasks:
            taskData = db_control_simple.get_taskBySupportID(id)
            time.sleep(2)
            createTask(taskData)
            result = db_control_simple.get_employeeByEmail(taskData['owner'])
            if isinstance(result, dict):
                owner_email = result['email']
            else:
                owner_email = app_secrets.get("GOOGLE_SUPPORT_EMAIL")
            gfm.send_html_email(owner_email, "Máš nový úkol", gfm.generateTaskEmail("email_templates/task-listed-employee.html", taskData))