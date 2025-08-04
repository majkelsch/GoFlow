# Custom Lib
import gs_mngr
import app_secrets
import gfdb
import gfm
import gftools

# Libs
import itertools
import time
import json























########################


def createTask(data):
    body = {
        "requests": [
            {
                "insertDimension": {
                    "range": {
                        "sheetId": gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "GoFlow").id,
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
                                        "stringValue": gfdb.get_client(id=data['client_id'])['full_name']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": gfdb.get_project(id=data['project_id'])['url']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": data['title']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": gfdb.get_employee(id=data['employee_id'])['full_name'] or app_secrets.get("DEFAULT_SUPPORT_OWNER")
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": gfdb.get_task_priority(id=data['priority_id'])['name']
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "stringValue": gfdb.get_task_status(id=data['status_id'])['name']
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
                                        "numberValue": data['duration']/60
                                    }
                                },
                                {
                                    "userEnteredValue": {
                                        "numberValue": data['duration']/60/60*1000
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
                        "sheetId": gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "GoFlow").id,
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
                        "sheetId": gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "GoFlow").id,
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
    if gftools.get_config("advancedDebug"):
        print(f"[API REQUEST SENT - POST] Response: {response}")



def getMissingTasks():
    tasks = gfdb.get_tasks()

    if len(tasks) != 0:
        tasksID = []
        for task in tasks:
            tasksID.append(task['support_id'])

        tasksID = set(tasksID)
        existingTasksID = list(itertools.chain.from_iterable(gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "GoFlow").get_values(f'A2:A{gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "GoFlow").row_count}')))
        existingTasksID = set(existingTasksID)
        
        difference = tasksID.symmetric_difference(existingTasksID)
        pendingTasks = sorted(list(difference))

        finalList = []
        for task_id in pendingTasks:
            if gfdb.get_task(support_id=task_id)['hidden'] == False:
                finalList.append(task_id)

        return list(finalList)
    else:
        return []



def exportTasksToSheets():
    gftools.create_flag("gs_sync", "syncing")
    pendingTasks = getMissingTasks()

    if gftools.get_config("advancedDebug"):
        print(f"[GFE: Pending tasks: {len(pendingTasks)}]")

    if len(pendingTasks) > 0:
        index = 0
        while index < len(pendingTasks):
            id = pendingTasks[index]

            if gftools.get_flag("gs_sync_recalculate") == "recalculate":
                if gftools.get_config("advancedDebug"):
                    print(f"[!] Caught a recalculate flag")
                pendingTasks = getMissingTasks()
                gftools.clear_flag("gs_sync_recalculate")
                index = 0
                continue
            else:
                taskData = gfdb.get_task(support_id=id)
                if taskData:
                    time.sleep(10)
                    createTask(taskData)

                    employee = gfdb.get_employee(id=taskData['employee_id'])
                    employee_email = employee['email']

                    if gftools.get_config("sendEmployeeMails"):
                        gfm.send_html_email(employee_email, "Máš nový úkol", gfm.generateTaskEmail("email_templates/task-listed-employee.html", taskData))

                    if gftools.get_config("advancedDebug"):
                        print(f"[GFE: Export progress: {index}/{len(pendingTasks)}]")
            index +=1
        if gftools.get_config("advancedDebug"):
            print(f"[GFE: Export finished.]")
    gftools.clear_flag("gs_sync")


def update_task(id):
    response = gs_mngr.getService().spreadsheets().values().get(
        spreadsheetId=app_secrets.get("GOFLOW_SPREADSHEET_ID"),
        range='GoFlow!A:A').execute()
    result = list(itertools.chain(*response['values']))

    row_id = result.index(id)

    task = gfdb.get_task(support_id=id)
    if task:

        body = {
            "requests": [
                {
                    "updateCells": {
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": task['support_id']
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": gfdb.get_client(id=task['client_id'])['full_name']
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": gfdb.get_project(id=task['project_id'])['url']
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": task['title']
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": gfdb.get_employee(id=task['employee_id'])['full_name'] or app_secrets.get("DEFAULT_SUPPORT_OWNER")
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": gfdb.get_task_priority(id=task['priority_id'])['name']
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": gfdb.get_task_status(id=task['status_id'])['name']
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": str(task['arrived'] if task['arrived'] is not None else "")
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": str(task['due'] if task['due'] is not None else "")
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": task['duration']/60
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": task['duration']/60/60*1000
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": str(task['started'] if task['started'] is not None else "")
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": str(task['finished'] if task['finished'] is not None else "")
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": task['description'][:5000]
                                        }
                                    }
                                ]
                            }
                        ],
                        "fields": "*",
                        "start": {
                            "sheetId": gs_mngr.getSheet("GOFLOW_SPREADSHEET_ID", "GoFlow").id,
                            "rowIndex": row_id,
                            "columnIndex": 0
                        }
                    }
                }
            ]
        }

        response = gs_mngr.getService().spreadsheets().batchUpdate(
            spreadsheetId=app_secrets.get("GOFLOW_SPREADSHEET_ID"),
            body=body
        ).execute()
        if gftools.get_config("advancedDebug"):
            print(f"[API REQUEST SENT - POST] Response: {response}")