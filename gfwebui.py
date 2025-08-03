# Custom libs
import gfe
import gftools
import gfdb
import gfm

# Libs
import flask
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
    if data.get("command") == "insert_task":
        gfdb.insert_task({
                    "support_id": f"SUP{str(datetime.datetime.now().year)[2:]}{str(gfdb.get_newTaskID()).zfill(4)}",
                    "client": data["task_data"].get("client", "Unknown Client"),
                    "project": data["task_data"].get("project", "Unknown Project"),
                    "title": data["task_data"].get("title", "No Title"),
                    "description": data["task_data"].get("description", "No Description"),
                    "employee": data["task_data"].get("employee", "No Owner"),
                    "priority": data["task_data"].get("priority", "No Priority"),
                    "status": data["task_data"].get("status", "No Status"),
                    "arrived": datetime.datetime.now().replace(microsecond=0),
                    "due": datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=7),
                    "duration": 0,
                    "started": None,
                    "finished": None,
                    "email_id": None
                })
        
        if gftools.get_flag("gs_sync") == "syncing":
            gftools.create_flag("gs_sync_recalculate", "recalculate")
        else:
            gfe.exportTasksToSheets()
        
    elif data.get("command") == "insert_employee":
        gfdb.insert_employee({
            "first_name": data["employee_data"].get("first_name"),
            "last_name": data["employee_data"].get("last_name"),
            "email": data["employee_data"].get("email"),
            "phone": data["employee_data"].get("phone"),
            "position": data["employee_data"].get("position")
        })

    elif data.get("command") == "insert_timetrack":
        gfdb.insert_timetrack({
            "task_id": gfdb.get_task(support_id=data["data"].get("support_id")).get('id'),
            "employee_id": gfdb.get_employee(email=data["data"].get("email")).get('id')
        })
    elif data.get("command") == "end_timetrack":
        gfdb.end_timetrack(identifiers={"task_id" : gfdb.get_task(support_id=data["data"].get("support_id")).get('id'), "employee_id" : gfdb.get_employee(email=data["data"].get("email")).get('id'), "end": None})
        gfdb.sum_task_timetracks(gfdb.get_task(support_id=data["data"].get("support_id")).get('id'))
        gfe.update_task(data["data"].get("support_id"))

    elif data.get("command") == "update_task":
        gfdb.sync_task(
            identifiers=data["data"]["identifiers"],
            updates=data["data"]["updates"]
            )
        
    elif data.get("command") == "insert_client":
        newClientId = gfdb.insert_client(data['data'])
        gfdb.insert_client_email({"client_id": newClientId, "email": data['data']['email']})

    elif data.get("command") == "insert_project":
        gfdb.insert_project(data['data'])

    elif data.get("command") == "end_task":
        if data['data']['sendAutoMail'] == True:
            task = gfdb.get_task(support_id=data['data']['task_id'])
            client = gfdb.get_client(id=task['client_id'])
            mails = gfdb.get_client_emails(client_id=client['id'])
            mail=mails[0]['email']
            with open('config.json', 'r') as configFile:
                config = json.load(configFile)
            if config['sendClientMails'] == True:
                gfm.send_html_email(mail, f"Požadavek {data['data']['task_id']} vyřízen.", gfm.generateTaskFinishedEmail('email_templates/task-finished-client.html', data['data']['task_id']))
            gfdb.end_task(support_id=data['data']['task_id'])
        else:
            gfdb.end_task(support_id=data['data']['task_id'])

    elif data.get("command") == "pairProjectClient":
        gfdb.assignProjectToClient(data['data']['client'], data['data']['project'])







@app.route("/api", methods=["GET", "POST"])
def api_endpoint():
    if flask.request.method == "POST":
        data = flask.request.get_json()
        threading.Thread(target=accept_request, args=(data,)).start()
        return {"status": "success"}, 200
    else:  # GET request
        request = flask.request.args.to_dict()
        if request.get('command') == 'getPositions':
            return json.dumps(clean(gfdb.get_positions()))
        elif request.get('command') == 'getClients':
            return json.dumps(clean(gfdb.get_clients()))
        elif request.get('command') == 'getProjects':
            return json.dumps(clean(gfdb.get_projects()))
        elif request.get('command') == 'getEmployees':
            return json.dumps(clean(gfdb.get_employees()))
        elif request.get('command') == 'getTaskPriorities':
            return json.dumps(clean(gfdb.get_task_priorities()))
        elif request.get('command') == 'getTaskStatuses':
            return json.dumps(clean(gfdb.get_task_statuses()))
        elif request.get('command') == 'getProjectStatuses':
            return json.dumps(clean(gfdb.get_project_statuses()))
        elif request.get('command') == 'getTasks':
            return json.dumps(clean(gfdb.get_tasks()))
        elif request.get('command') == 'getProjectsByClient':
            return json.dumps(gfdb.get_client(id=request.get('client_id'))['projects'])
            #return json.dumps(clean(gfdb.get_project(id=request.get('client_id'))))
        else:
            return {"message": f"Invalid request."}, 200




if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8080, debug=True)


