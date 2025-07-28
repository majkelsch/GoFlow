from flask import Flask, request
import db_control_simple
import threading
import datetime
from datetime import timedelta
import os
import dotenv

#dotenv.load_dotenv()
#DEFAULT_SUPPORT_OWNER = os.getenv("DEFAULT_SUPPORT_OWNER")
#if DEFAULT_SUPPORT_OWNER is None:
#    raise ValueError("DEFAULT_SUPPORT_OWNER environment variable is not set or is missing.")

app = Flask(__name__)

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
                    "due": datetime.datetime.now().replace(microsecond=0) + timedelta(days=7),
                    "duration": 0,
                    "started": None,
                    "finished": None,
                    "email_id": None,
                    "last_edit_by": data["task_data"].get("last_edit_by", "No Last Edit By")
                })
        # Add a way to "intercept" ongoing export and include this incoming task into it. Also Declutter the whole project and change hierarchy to be HTTP based server
        #main2.exportTasksToSheets()



        

@app.route("/api", methods=["POST"])
def trigger_function():
    data = request.get_json()
    threading.Thread(target=accept_request, args=(data,)).start()
    return {"status": "success"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
