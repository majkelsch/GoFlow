# Custom libs
import gfe
import gftools
import gfdb
import gfm

from db.gflog import Base

# Libs
import flask
import requests
import flask_cors
import threading
import datetime
import time
import json
import random
import base64


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


def parse_include_exclude(request):
    """Parse 'include' and 'exclude' parameters from a request dict."""
    include = request.get('include')
    exclude = request.get('exclude')
    if isinstance(exclude, list):
        exclude = exclude
    elif exclude:
        exclude = exclude.split(';')
    else:
        exclude = None

    if str(include).lower() == 'true':
        include = True
    elif include:
        include = include.split(';')
    else:
        include = None

    return include, exclude


# MODEL_LOOKUP = {cls.__name__: cls for cls in Base.registry.mappers for cls in [cls.class_]}


def get_model_by_name(model_name: str):
    """
    Returns SQLAlchemy model by class name.
    
    :param model_name: Model class name
    :return: Model class or None
    """
    for mapper in Base.registry.mappers:
        cls = mapper.class_
        if cls.__name__ == model_name:
            return cls
    return None









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
        print(payload)
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
        gftools.detect_collision_flag("gs_sync", "syncing", 5, lambda: gfe.end_task(support_id=payload['task_id']), max_retries=50, debug=True)

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
            include, exclude = parse_include_exclude(request)
            return json.dumps(clean(gfdb.get_positions(exclude_relationships=exclude, include_relationships=include)), cls=gftools.EnhancedJSONEncoder)
        elif command == 'getClients':
            include, exclude = parse_include_exclude(request)
            return json.dumps(clean(gfdb.get_clients(exclude_relationships=exclude, include_relationships=include)), cls=gftools.EnhancedJSONEncoder)
        elif command == 'getProjects':
            include, exclude = parse_include_exclude(request)
            return json.dumps(clean(gfdb.get_projects(exclude_relationships=exclude, include_relationships=include)), cls=gftools.EnhancedJSONEncoder)
        elif command == 'getEmployees':
            include, exclude = parse_include_exclude(request)
            return json.dumps(clean(gfdb.get_employees(exclude_relationships=exclude, include_relationships=include)), cls=gftools.EnhancedJSONEncoder)
        elif command == 'getTaskPriorities':
            include, exclude = parse_include_exclude(request)
            return json.dumps(clean(gfdb.get_task_priorities(exclude_relationships=exclude, include_relationships=include)), cls=gftools.EnhancedJSONEncoder)
        elif command == 'getTaskStatuses':
            include, exclude = parse_include_exclude(request)
            return json.dumps(clean(gfdb.get_task_statuses(exclude_relationships=exclude, include_relationships=include)), cls=gftools.EnhancedJSONEncoder)
        elif command == 'getProjectStatuses':
            include, exclude = parse_include_exclude(request)
            return json.dumps(clean(gfdb.get_project_statuses(exclude_relationships=exclude, include_relationships=include)), cls=gftools.EnhancedJSONEncoder)
        elif command == 'getTasks':
            include, exclude = parse_include_exclude(request)
            return json.dumps(clean(gfdb.get_tasks(exclude_relationships=exclude, include_relationships=include)), cls=gftools.EnhancedJSONEncoder)
        elif command == 'getProjectsByClient':
            return json.dumps(gfdb.get_client(id=request.get('client_id'))['projects'], cls=gftools.EnhancedJSONEncoder)
        elif command == 'getClientsByProject':
            return json.dumps(gfdb.get_project(id=request.get('project_id'))['clients'], cls=gftools.EnhancedJSONEncoder)
        elif command == 'serverStatus':
            return json.dumps({"api_up": True}, cls=gftools.EnhancedJSONEncoder)
        else:
            return {"message": f"Invalid request."}, 200







def accept_post_request_v1(data):
    command = data.get("command")
    payload = data.get("payload")
    req_id = random.randint(1000,9999)
    model = get_model_by_name(payload['model'])

    gftools.log(f"┌ ({req_id}) [API V1 - POST] Command: {command} | Payload: {payload}", level='info')

    match command:
        case 'insert_one':
            gftools.log(f"├ ({req_id}) Identified command", level='info')
            if model:
                return_id = gfdb.insert_one(
                    model=model,
                    data=payload['data'],
                    related_fields=payload.get('related_fields', None)
                    )
                gftools.log(f"└ ({req_id}) Inserted into DB with id: {return_id}", level='info')

        case 'update_one':
            gftools.log(f"├ ({req_id}) Identified command", level='info')
            if model:
                return_id = gfdb.update_one(
                    model=model,
                    record_id=payload['record_id'],
                    updates=payload['updates']
                )
                gftools.log(f"└ ({req_id}) Updated id: {return_id} in {model} to {payload['updates']}", level='info')
        
        case 'delete_one':
            gftools.log(f"├ ({req_id}) Identified command", level='info')
            if model:
                return_id = gfdb.delete_one(
                    model=model,
                    record_id=payload['record_id']
                )
                if return_id:
                    gftools.log(f"└ ({req_id}) Deleted id: {payload['record_id']} in {model}", level='info')
                else:
                    gftools.log(f"└ [X] ({req_id}) Couldn't delete id: {payload['record_id']} in {model}", level='warning')
        
        case 'delete_by_filters':
            gftools.log(f"├ ({req_id}) Identified command", level='info')
            if model:
                return_id = gfdb.delete_by_filters(
                    model=model,
                    filters=payload['filters']
                )
                if return_id > 0:
                    gftools.log(f"└ ({req_id}) Deleted {return_id} in {model}", level='info')
                else:
                    gftools.log(f"└ [X] ({req_id}) No records deleted in {model}", level='info')
        case _:
            gftools.log(f"├ ({req_id}) Command: `{command}`, not identified.", level='warning')


def accept_get_request_v1(data):
    if data:
        data_json = json.loads(data)
        command = data_json['command']
        match command:
            case 'get_one':
                include, exclude = parse_include_exclude(data_json)
                model = get_model_by_name(data_json.get('model', None))
                identifiers = data_json.get('identifiers', None)
                if model and identifiers:
                    return gfdb.get_one(
                        model=model,
                        include_relationships=include,
                        exclude_relationships=exclude,
                        max_depth=data_json.get('max-depth', 1),
                        **identifiers
                    )
                else:
                    return {"message": f"Error: MODEL or IDENTIFIERS are missing or incorrect."}, 200
            case 'get_all':
                include, exclude = parse_include_exclude(data_json)
                model = get_model_by_name(data_json.get('model', None))
                filters = data_json.get('filters', None)
                if model:
                    return json.dumps(gfdb.get_all(
                        model=model,
                        include_relationships=include,
                        exclude_relationships=exclude,
                        max_depth=data_json.get('max-depth', 1),
                        filters=filters
                    ), cls=gftools.EnhancedJSONEncoder)
                else:
                    return {"message": f"Error: MODEL is missing or incorrect."}, 200
            case 'get_tables':
                return [cls.__name__ for cls in Base.__subclasses__()]
            case _:
                return {"message": f"Invalid request."}, 200
    else:
        return {"message": f"Error: Invalid request."}, 400






@app.route("/api/v1", methods=["GET", "POST"])
def api_v1():
    if flask.request.method == "POST":
        data = flask.request.get_json()
        threading.Thread(target=accept_post_request_v1, args=(data,)).start()
        return {"status": "processing"}, 200
    else:
        data = flask.request.args.get('data')
        if data:
            return accept_get_request_v1(data)
        else:
            return flask.render_template('api-help.html')


@app.route("/server-status")
def server_status():
    return flask.render_template('server-status.html', api_status="functional", scripts_status=gftools.get_flag('status_scripts'))

@app.route("/db-editor")
def db_editor():
    if flask.request.headers.getlist("X-Forwarded-For"):
        user_ip = flask.request.headers.getlist("X-Forwarded-For")[0]
    else:
        user_ip = flask.request.remote_addr
    if user_ip:
        gftools.log(f"CONNECTION: {user_ip}", level='debug')
    return flask.render_template('db-editor.html')


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8080, debug=True)


