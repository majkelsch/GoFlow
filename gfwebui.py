# Custom libs
import gfe
import gftools
import gfdb
import gfm

# Libs
import flask
import requests
import flask_cors
import threading
import datetime
import time
import json


#############
app = flask.Flask(__name__)
flask_cors.CORS(app)


def clean(data):
    """Clean the data by removing unwanted keys."""
    if type(data) == list:
        cleaned_data = []
        for item in data:
            cleaned_item = {key: value for key, value in item.items() if key != '_sa_instance_state'}
            cleaned_data.append(cleaned_item)
        return cleaned_data
    else:
        cleaned_data = {key: value for key, value in data.items() if key != '_sa_instance_state'}
        return cleaned_data

















def accept_request(data):
    command = data.get("command")
    payload = data.get("data")

    if gftools.get_config("advancedDebug"):
        print(f"[API REQUEST RECEIVED - POST] Command: {command} | Data: {payload}")

    if command == "insert_task":
        if gftools.get_config("advancedDebug"):
            print(f"├ Identified command - Inserting to DB")
        return_id = gfdb.insert_task({
                    "support_id": f"SUP{str(datetime.datetime.now().year)[2:]}{str(gfdb.get_newTaskID()).zfill(4)}",
                    "client": payload["client"],
                    "project": payload["project"],
                    "title": payload["title"],
                    "description": payload["description"],
                    "employee": payload["employee"],
                    "priority": payload["priority"],
                    "status": payload["status"],
                    "arrived": datetime.datetime.now().replace(microsecond=0),
                    "due": payload["due_date"] if payload["due_date"] else datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=7)
                })
        if gftools.get_config("advancedDebug"):
            print(f"└ Inserted data into DB with id = {return_id}")

        if gftools.get_flag("gs_sync") == "syncing":
            gftools.create_flag("gs_sync_recalculate", "recalculate")
            if gftools.get_config("advancedDebug"):
                print(f"[!] Triggered a recalculate flag event")
        else:
            if gftools.get_config("advancedDebug"):
                print(f"Exporting data to Google Sheets.")
            gfe.exportTasksToSheets()
            if gftools.get_config("advancedDebug"):
                print(f"[END OF API REQUEST]")
        






    elif command == "insert_employee":
        if gftools.get_config("advancedDebug"):
            print(f"├ Identified command - Inserting to DB")
        return_id = gfdb.insert_employee({
            "first_name": payload["first_name"],
            "last_name": payload["last_name"],
            "email": payload["email"],
            "phone": payload["phone"],
            "position": payload["position"]
        })
        if gftools.get_config("advancedDebug"):
            print(f"└ Inserted data into DB with id = {return_id}")
            print(f"[END OF API REQUEST]")






    elif command == "insert_timetrack":
        if gftools.get_config("advancedDebug"):
            print(f"├ Identified command - Inserting to DB")
        return_id = gfdb.insert_timetrack({
            "task_id": gfdb.get_task(support_id=payload["task_id"])['id'],
            "employee_id": gfdb.get_employee(email=payload["employee"])['id']
        })
        if gftools.get_config("advancedDebug"):
            print(f"└ Inserted data into DB with id = {return_id}")
            print(f"[END OF API REQUEST]")



    elif command == "end_timetrack":
        if gftools.get_config("advancedDebug"):
            print(f"├ Identified command - Initiating sequence")


        return_id = gfdb.end_timetrack(identifiers={"task_id" : gfdb.get_task(support_id=payload["task_id"])['id'], "employee_id" : gfdb.get_employee(email=payload["employee"])['id'], "end": None})
        if return_id is not None:
            if gftools.get_config("advancedDebug"):
                print(f"├ [1/3] Ended timetrack with id = {return_id}")

            gfdb.sum_task_timetracks(gfdb.get_task(support_id=payload["task_id"])['id'])
            if gftools.get_config("advancedDebug"):
                print(f"├ [2/3] Summed the duration from records")

            gfe.update_task(payload["task_id"])
            if gftools.get_config("advancedDebug"):
                print(f"└ [3/3] Updated task in Google Sheets")
                print(f"[END OF API REQUEST]")
        else:
            if gftools.get_config("advancedDebug"):
                print(f"└ [!] Sequence aborted: No timetrackers found")
                print(f"[END OF API REQUEST]")





    elif command == "update_task":
        if gftools.get_config("advancedDebug"):
            print(f"├ Identified command - Updating DB records")
        gfdb.sync_task(
            identifiers=payload["identifiers"],
            updates=payload["updates"]
            )
        if gftools.get_config("advancedDebug"):
            print(f"└ DB records updated")
            print(f"[END OF API REQUEST]")
        



    elif command == "insert_client":
        if gftools.get_config("advancedDebug"):
            print(f"├ Identified command - Inserting to DB")
        return_id = gfdb.insert_client(payload)
        if gftools.get_config("advancedDebug"):
            print(f"├ Inserted data into DB with id = {return_id}")
        return_id = gfdb.insert_client_email({"client_id": return_id, "email": payload['email']})
        if gftools.get_config("advancedDebug"):
            print(f"└ Paired client-email relationship with id = {return_id}")
            print(f"[END OF API REQUEST]")






    elif command == "insert_project":
        if gftools.get_config("advancedDebug"):
            print(f"├ Identified command - Inserting to DB")
        return_id = gfdb.insert_project(payload)
        if gftools.get_config("advancedDebug"):
            print(f"└ Inserted data into DB with id = {return_id}")
            print(f"[END OF API REQUEST]")






    elif command == "end_task":
        if gftools.get_config("advancedDebug"):
            print(f"├ Identified command - Initiating sequence")

        if payload['sendAutoMail'] == True:
            if gftools.get_config("advancedDebug"):
                print(f"[!] Sending automail")

            task = gfdb.get_task(support_id=payload['task_id'])
            if gftools.get_config("advancedDebug"):
                print(f"├ [1/4] Found related task with id = {task['id']}")
            client = gfdb.get_client(id=task['client_id'])
            if gftools.get_config("advancedDebug"):
                print(f"├ [2/4] Found related client with id = {client['id']}")
            mails = gfdb.get_client_emails(client_id=client['id'])
            if gftools.get_config("advancedDebug"):
                print(f"├ [3/4] Found related client's emails with ids = {[mail['id'] for mail in mails]}")
            mail=mails[0]['email']
            if gftools.get_config("advancedDebug"):
                print(f"├ [WARNING] Multiple emails results in the first record being chosen as the primary one.")

            if gftools.get_config("sendClientMails"):
                gfm.send_html_email(mail, f"Požadavek {payload['task_id']} vyřízen.", gfm.generateTaskFinishedEmail('email_templates/task-finished-client.html', payload['task_id']))
                if gftools.get_config("advancedDebug"):
                    print(f"└ [4/4] Sending email")
        else:
            if gftools.get_config("advancedDebug"):
                print(f"[!] Only ending task")
        gfdb.end_task(support_id=payload['task_id'])
        gftools.wait_for_flag("gs_sync", "syncing", 5, lambda: gfe.end_task(support_id=payload['task_id']))

        if gftools.get_config("advancedDebug"):
            print(f"[END OF API REQUEST]")



    elif data.get("command") == "pairProjectClient":
        if gftools.get_config("advancedDebug"):
            print(f"├ Identified command - Pairing records")
        gfdb.assignProjectToClient(data['data']['client'], data['data']['project'])
        if gftools.get_config("advancedDebug"):
            print(f"└ Records paired")
            print(f"[END OF API REQUEST]")







@app.route("/api", methods=["GET", "POST"])
def api_endpoint():
    if flask.request.method == "POST":
        data = flask.request.get_json()
        threading.Thread(target=accept_request, args=(data,)).start()
        return {"status": "success"}, 200
    else:  # GET request
        request = flask.request.args.to_dict()
        command = request.get('command')

        if command == 'getPositions':
            return json.dumps(clean(gfdb.get_positions()))
        elif command == 'getClients':
            return json.dumps(clean(gfdb.get_clients()))
        elif command == 'getProjects':
            return json.dumps(clean(gfdb.get_projects()))
        elif command == 'getEmployees':
            return json.dumps(clean(gfdb.get_employees()))
        elif command == 'getTaskPriorities':
            return json.dumps(clean(gfdb.get_task_priorities()))
        elif command == 'getTaskStatuses':
            return json.dumps(clean(gfdb.get_task_statuses()))
        elif command == 'getProjectStatuses':
            return json.dumps(clean(gfdb.get_project_statuses()))
        elif command == 'getTasks':
            return json.dumps(clean(gfdb.get_tasks()), cls=gftools.EnhancedJSONEncoder)
        elif command == 'getProjectsByClient':
            return json.dumps(gfdb.get_client(id=request.get('client_id'))['projects'])
        elif command == 'getClientsByProject':
            return json.dumps(gfdb.get_project(id=request.get('project_id'))['clients'])
        elif command == 'serverStatus':
            return json.dumps({"api_up": True})
        else:
            return {"message": f"Invalid request."}, 200


@app.route("/server-status")
def server_status():
    return flask.render_template('server-status.html', api_status="functional", scripts_status="down")


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8080, debug=True)


