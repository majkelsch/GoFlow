# Custom libs
import app_secrets
import gfi
import gfe
import db_control_simple

# Libs
import flask
import threading
import datetime
import time
from multiprocessing import Process
import os


#############
app = flask.Flask(__name__)

updateTime = 30



















def accept_request(data):
    if data.get("command") == "create_task":
        db_control_simple.createTask_DB({
                    "support_id": f"SUP{str(datetime.datetime.now().year)[2:]}{str(db_control_simple.get_newTaskID()).zfill(4)}",
                    "client": data["task_data"].get("client", "Unknown Client"),
                    "project": data["task_data"].get("project", "Unknown Project"),
                    "title": data["task_data"].get("title", "No Title"),
                    "description": data["task_data"].get("description", "No Description"),
                    "owner": data["task_data"].get("owner", "No Owner"),
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







@app.route("/api", methods=["POST"])
def api_endpoint():
    data = flask.request.get_json()
    threading.Thread(target=accept_request, args=(data,)).start()
    return {"status": "success"}, 200









def main_loop():
    while True:
        try:
            #gfi.getSolidpixelsData()
            #gfi.getGmailData()

            gfe.exportTasksToSheets()
        except Exception as e:
            print(f"[{datetime.datetime.now()}] Error in main_loop: {e}")
        time.sleep(updateTime)

def start_process():
    p = Process(target=main_loop)
    p.daemon = True
    p.start()

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_process()
    app.run(host="0.0.0.0", port=8080, debug=True)


