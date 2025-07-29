# Custom libs
import gfe
import db_control_simple

# Libs
import flask
import threading
import datetime
import time
import json


#############
app = flask.Flask(__name__)


def clean(data):
    """Clean the data by removing unwanted keys."""
    cleaned_data = []
    for item in data:
        cleaned_item = {key: value for key, value in item.items() if key != '_sa_instance_state'}
        cleaned_data.append(cleaned_item)
    return cleaned_data
















def accept_request(data):
    if data.get("command") == "create_task":
        db_control_simple.createTask_DB({
                    "support_id": f"SUP{str(datetime.datetime.now().year)[2:]}{str(db_control_simple.get_newTaskID()).zfill(4)}",
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
                    "email_id": None,
                    "last_edit_by": data["task_data"].get("last_edit_by", "No Last Edit By")
                })
        gfe.exportTasksToSheets()







@app.route("/api", methods=["GET", "POST"])
def api_endpoint():
    if flask.request.method == "POST":
        data = flask.request.get_json()
        threading.Thread(target=accept_request, args=(data,)).start()
        return {"status": "success"}, 200
    else:  # GET request
        data = flask.request.get_json()
        if data.get("command") == "get_clients":
            out = json.dumps(clean(db_control_simple.get_Clients_DB()), ensure_ascii=False)
            return {"clients": out}, 200
        elif data.get("command") == "get_projects":
            out = json.dumps(clean(db_control_simple.get_Projects_DB()), ensure_ascii=False)
            return {"projects": out}, 200
        else:
            return {"message": f"Invalid request. {data}"}, 200






if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8080, debug=True)


