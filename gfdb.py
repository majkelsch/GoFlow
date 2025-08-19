from db.gfmodels import *
from db.gfsessions import session, db_init
from db.gflog import attach_logger, DBChangeLog, Base
from db.gfdict import *

import gftools
import app_secrets


import json
from typing import Optional, Type, Any




attach_logger(Clients, session)
attach_logger(ClientsEmails, session)
attach_logger(Emails, session)
attach_logger(EmployeePositions, session)
attach_logger(Employees, session)
attach_logger(Projects, session)
attach_logger(ProjectsStatuses, session)
attach_logger(TaskPriorities, session)
attach_logger(Tasks, session)
attach_logger(TaskPriorities, session)
attach_logger(Timetrackers, session)

# Create all tables including the log
Base.metadata.create_all(bind=session.get_bind())






##########

def populate_db_on_init():
    session = db_init()

    with open("dbinit.json", "r") as file:
        data = json.load(file)

    model_map = {
        "clients": Clients,
        "employeePositions": EmployeePositions,
        "employees": Employees,
        "projects": Projects,
        "projectStatuses": ProjectsStatuses,
        "taskPriorities": TaskPriorities,
        "taskStatuses": TaskStatuses
    }

    for table_name, records in data.items():
        model = model_map.get(table_name)
        if not model:
            print(f"Unknown table: {table_name}")
            continue

        for record in records:
            # Make sure record is a dict
            if isinstance(record, dict):
                obj = model(**record)
                session.add(obj)
            else:
                print(f"Unexpected record format in {table_name}: {record}")

    session.commit()

########## Timetracker ##########

def get_timetrack(identifiers: dict):
    session = db_init()

    try:
        filters = [getattr(Timetrackers, k) == v for k, v in identifiers.items()]
        timetrack = session.query(Timetrackers).filter(*filters).first()
        if timetrack:
            return timetrack.to_dict()
        else:
            raise Exception(f"Timetrack searched by '{filters}' not found.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_timetrack: {e}")
        return None
    finally:
        session.close()

def insert_timetrack(data):
    session = db_init()

    try:
        record = Timetrackers(
            task_id = data['task_id'],
            employee_id = data['employee_id'],
            start = datetime.datetime.now().replace(microsecond=0)
        )
        session.add(record)
        session.commit()
        return record.id
    except Exception as e:
        print(f"Error creating timetracker: {e}")
        session.rollback()  
    finally:
        session.close()

def set_timetrack(identifiers: dict, updates: dict):
    session = db_init()
    
    try:
        filters = [getattr(Timetrackers, k) == v for k, v in identifiers.items()]
        timetrack = session.query(Timetrackers).filter(*filters).first()

        if timetrack:
            for key, value in updates.items():
                setattr(timetrack, key, value)
        else:
            raise Exception("No records found.")
    except Exception as e:
        print(f"Error updating timetracker: {e}")
        session.rollback()  
    finally:
        session.commit()

def end_timetrack(identifiers: dict):
    session = db_init()

    try:
        filters = [getattr(Timetrackers, k) == v for k, v in identifiers.items()]
        timetrack = session.query(Timetrackers).filter(*filters).first()

        if timetrack:
            timetrack.end = datetime.datetime.now().replace(microsecond=0)
            duration = timetrack.end - timetrack.start
            seconds = duration.total_seconds()
            timetrack.duration = seconds
            return timetrack.id
        else:
            raise Exception("No records found.")
    except Exception as e:
        print(f"Error ending timetracker: {e}")
        session.rollback()  
    finally:
        session.commit()


def sum_task_timetracks(task_id):
    session = db_init()

    try:
        timetrack_sum = session.query(func.sum(Timetrackers.duration)).filter(Timetrackers.task_id == task_id).scalar()

        task = session.query(Tasks).filter_by(id=task_id).first()

        if task:
            task.duration = timetrack_sum
        else:
            raise Exception("No records found.")

    except Exception as e:
        print(f"Error creating a sum: {e}")
        session.rollback()  
    finally:
        session.commit()
















def get_newTaskID():
    session = db_init()

    try:
        max_id = session.query(func.max(Tasks.id)).scalar()
        if max_id:
            return max_id + 1
        else:
            return 1
    finally:
        session.close()



def get_tasks(exclude_relationships: Optional[list] = None, include_relationships: Optional[list] | Optional[bool] = False):
    session = db_init()

    try:
        tasks = session.query(Tasks).all()
        return [task.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships) for task in tasks]
    finally:
        session.close()



def get_task(**kwargs):
    session = db_init()

    try:
        task = session.query(Tasks).filter_by(**kwargs).first()
        if task:
            return task.to_dict()
        else:
            raise Exception(f"Task searched by '{kwargs}' not found")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_task: {e}")
        null = session.query(Tasks).first()
        return null.to_dict() if null else {}
    finally:
        session.close()

########## Tasks ##########

def insert_task(data):
    session = db_init()

    if type(data['client']) == int or data['client'].isnumeric():
        client = session.query(Clients).filter_by(id=data['client']).first()
    else:
        client = session.query(Clients).filter_by(full_name=data['client']).first()

    if type(data['project']) == int or data['project'].isnumeric():
        project = session.query(Projects).filter_by(id=data['project']).first()
    else:
        project = session.query(Projects).filter_by(name=data['project']).first()

    if type(data['employee']) == int or data['employee'].isnumeric():
        employee = session.query(Employees).filter_by(id=data['employee']).first()
    else:
        employee = session.query(Employees).filter_by(full_name=data['employee']).first()

    if type(data['priority']) == int or data['priority'].isnumeric():
        priority = session.query(TaskPriorities).filter_by(id=data['priority']).first()
    else:
        priority = session.query(TaskPriorities).filter_by(name=data['priority']).first()

    if type(data['status']) == int or data['status'].isnumeric():
        status = session.query(TaskStatuses).filter_by(id=data['status']).first()
    else:
        status = session.query(TaskStatuses).filter_by(name=data['status']).first()

    try:
        record = Tasks(
            support_id=data['support_id'],
            client=client,
            project=project,
            title=data['title'],
            description=data.get('description', ''),
            employee=employee,
            priority=priority,
            status=status,
            arrived=gftools.parse_datetime(data.get('arrived')),
            due=gftools.parse_datetime(data.get('due')),
            duration=data.get('duration', 0.0),
            started=gftools.parse_datetime(data.get('started')),
            finished=gftools.parse_datetime(data.get('finished')),
            email_id=data.get('email_id')
        )

        session.add(record)
        session.commit()
        return record.id
    except Exception as e:
        print(f"Error creating task: {e}")
        session.rollback()
    finally:
        session.close()

def get_task_priorities(exclude_relationships: Optional[list] = None, include_relationships: Optional[list] | Optional[bool] = False):
    session = db_init()

    try:
        priorities = session.query(TaskPriorities).all()
        return [priority.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships) for priority in priorities]
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_task_priorities: {e}")
        null = session.query(TaskPriorities).first()
        return [null.to_dict()] if null else []
    finally:
        session.close()

def get_task_priority(**kwargs) -> dict:
    session = db_init()

    try:
        priority = session.query(TaskPriorities).filter_by(**kwargs).first()
        if priority:
            return priority.to_dict()
        else:
            raise Exception(f"Priority searched by '{kwargs}' not found.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_task_priority: {e}")
        null = session.query(TaskPriorities).first()
        return null.to_dict() if null else {}
    finally:
        session.close()

def get_task_statuses(exclude_relationships: Optional[list] = None, include_relationships: Optional[list] | Optional[bool] = False):
    session = db_init()

    try:
        statuses = session.query(TaskStatuses).all()
        return [status.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships) for status in statuses]
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_task_statuses: {e}")
        null = session.query(TaskStatuses).first()
        return [null.to_dict()] if null else []
    finally:
        session.close()

def get_task_status(**kwargs) -> dict:
    session = db_init()

    try:
        status = session.query(TaskStatuses).filter_by(**kwargs).first()
        if status:
            return status.to_dict()
        else:
            raise Exception(f"Task status searched by '{kwargs}' not found.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_task_status: {e}")
        null = session.query(TaskStatuses).first()
        return null.to_dict() if null else {}
    finally:
        session.close()

def sync_task(identifiers: dict, updates: dict):
    session = db_init()
    
    try:
        filters = [getattr(Tasks, k) == v for k, v in identifiers.items()]
        task = session.query(Tasks).filter(*filters).first()

        if task:
            for key, value in updates.items():

                if key == "employee":
                    employee = get_employee(full_name=value)
                    setattr(task, "employee_id", employee["id"] if isinstance(employee, dict) else employee[0]["id"])
                elif key == "priority":
                    priority = get_task_priority(name=value)
                    setattr(task, "priority_id", priority["id"] if isinstance(priority, dict) else priority[0]["id"])
                elif key == "status":
                    status = get_task_status(name=value)
                    setattr(task, "status_id", status["id"] if isinstance(status, dict) else status[0]["id"])
                elif key == "description":
                    setattr(task, key, value)
        else:
            raise Exception("No records found.")
    except Exception as e:
        print(f"Error updating task: {e}")
        session.rollback()  
    finally:
        session.commit()

def end_task(**kwargs):
    session = db_init()

    try:
        task = session.query(Tasks).filter_by(**kwargs).first()
        if task:
            task.hidden = True
        else:
            raise Exception(f"Task searched by '{kwargs} not found.")

    except Exception as e:
        print(f"Error ending task: {e}")
        session.rollback()
    finally:
        session.commit()




########## CLIENTS ##########

def insert_client(data):
    session = db_init()

    try:
        record = Clients(
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        session.add(record)
        session.commit()
        return record.id
    except Exception as e:
        print(f"Error creating client: {e}")
        session.rollback()
        return 0
    finally:
        session.close()


def insert_client_email(data):
    session = db_init()

    try:
        record = ClientsEmails(
            client_id=data['client_id'],
            email=data['email']
        )
        session.add(record)
        session.commit()
        return record.id
    except Exception as e:
        print(f"Error creating client's email: {e}")
        session.rollback()
    finally:
        session.close()






def get_clients(exclude_relationships: Optional[list] = None, include_relationships: Optional[list] | Optional[bool] = False):
    session = db_init()

    try:
        clients = session.query(Clients).all()
        return [client.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships) for client in clients]
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_Clients_DB: {e}")
        null = session.query(Clients).first()
        return [null.to_dict()] if null else []
    finally:
        session.close()

def get_client(**kwargs):
    session = db_init()

    try:
        client = session.query(Clients).filter_by(**kwargs).first()
        if client:
            return client.to_dict(include_relationships=True)
        else:
            raise Exception(f"Client searched by '{kwargs}' not found.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_client: {e}")
        null = session.query(Clients).first()
        return null.to_dict() if null else {}
    finally:
        session.close()



def get_client_emails(**kwargs) -> list[dict]:
    session = db_init()

    try:
        emails = session.query(ClientsEmails).filter_by(**kwargs).all()
        return [email.to_dict() for email in emails]
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_client_emails: {e}")
        null = session.query(Clients).first()
        return [null.to_dict()] if null else []
    finally:
        session.close()

def get_all_client_emails(exclude_relationships: Optional[list] = None, include_relationships: Optional[list] | Optional[bool] = False):
    session = db_init()

    try:
        emails = session.query(ClientsEmails).all()
        return [email.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships) for email in emails]
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_all_client_emails: {e}")
        return []
    finally:
        session.close()

########## PROJECT ##########

def insert_project(data: ProjectDict):
    session = db_init()

    if type(data['status']) == int or data['status'].isnumeric():
        status = session.query(ProjectsStatuses).filter_by(id=data['status']).first()
    else:
        status = session.query(ProjectsStatuses).filter_by(name=data['status']).first()


    try:
        record = Projects(
            url=data['url'],
            status=status
        )
        session.add(record)
        session.commit()
        return record.id
    except Exception as e:
        print(f"Error creating project: {e}")
        session.rollback()
    finally:
        session.close()

def get_projects(exclude_relationships: Optional[list] = None, include_relationships: Optional[list] | Optional[bool] = False):
    session = db_init()

    try:
        projects = session.query(Projects).all()
        return [project.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships) for project in projects]
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_projects: {e}")
        null = session.query(Projects).first()
        return [null.to_dict()] if null else []
    finally:
        session.close()

def get_project(**kwargs) -> dict:
    session = db_init()

    try:
        project = session.query(Projects).filter_by(**kwargs).first()
        if project:
            return project.to_dict(include_relationships=True)
        else:
            raise Exception(f"Project searched by '{kwargs}' not found.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_project: {e}")
        null = session.query(Projects).first()
        return null.to_dict() if null else {}
    finally:
        session.close()


def insert_project_status(data: ProjectStatusDict):
    session = db_init()

    try:
        record = ProjectsStatuses(
            name=data['name']
        )
        session.add(record)
        session.commit()
        return record.id
    except Exception as e:
        print(f"Error creating project: {e}")
        session.rollback()
    finally:
        session.close()


def get_project_statuses(exclude_relationships: Optional[list] = None, include_relationships: Optional[list] | Optional[bool] = False):
    session = db_init()

    try:
        statuses = session.query(ProjectsStatuses).all()
        return [status.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships) for status in statuses]
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_project_statuses: {e}")
        null = session.query(Projects).first()
        return [null.to_dict()] if null else []
    finally:
        session.close()
    


########## EMPLOYEE ##########

def insert_employee(data: EmployeeDict):
    session = db_init()

    try:
        if type(data['position']) == int or data['position'].isnumeric():
            position = session.query(EmployeePositions).filter_by(id=data['position']).first()
        else:
            position = session.query(EmployeePositions).filter_by(name=data['position']).first()

        record = Employees(
            first_name = data['first_name'],
            last_name = data['last_name'],
            email = data['email'],
            phone = data['phone'].replace(" ", ""),
            position = position
        )
        session.add(record)
        session.commit()
        return record.id
    except Exception as e:
        print(f"Error creating employee record: {e}")
        session.rollback()
    finally:
        session.close()

def insert_employeePosition(data):
    session = db_init()

    try:
        newEmployeePosition = EmployeePositions(name = data['name'])
        session.add(newEmployeePosition)
        session.commit()
    except Exception as e:
        print(f"Error creating employee position record: {e}")
        session.rollback()
    finally:
        session.close()

def get_positions(exclude_relationships: Optional[list] = None, include_relationships: Optional[list] | Optional[bool] = False):
    session = db_init()

    try:
        positions = session.query(EmployeePositions).all()
        return [position.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships) for position in positions]
    except Exception as e:
        print(f"Error getting positions: {e}")
        null = session.query(EmployeePositions).first()
        return [null]
    finally:
        session.close()

def get_employees(exclude_relationships: Optional[list] = None, include_relationships: Optional[list] | Optional[bool] = False):
    session = db_init()

    try:
        employees = session.query(Employees).all()
        return [employee.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships) for employee in employees]
    except Exception as e:
        print(f"Error getting employees: {e}")
        null = session.query(Employees).first()
        return [null.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships)] if null else []
    finally:
        session.close()

def get_employee(**kwargs) -> dict:
    session = db_init()

    try:
        employee = session.query(Employees).filter_by(**kwargs).first()
        if employee:
            return employee.to_dict(include_relationships=True)
        else:
            raise Exception(f"Employee searched by '{kwargs}' not found.")
    except Exception as e:
        print(f"Error getting employee: {e}")
        null = session.query(Employees).first()
        return null.to_dict() if null else {}
    finally:
        session.close()


def update_employee(id, updates:dict):
    session = db_init()
    try:
        employee = session.query(Employees).filter_by(id=id).first()
        if employee:
            for key, value in updates.items():
                setattr(employee, key, value)
        else:
            raise Exception("No records found.")
    except Exception as e:
        print(f"Error updating employee: {e}")
        session.rollback()  
    finally:
        session.commit()



########## EMAILS ##########

def insert_email(data: EmailsDict):
    session = db_init()

    try:
        newEmail = Emails(
            email_id = data['email_id'],
            sender = data['sender'].split('<')[-1].strip('>'),
            subject = data['subject'],
            content = data['content'],
            date = data['date']
            
        )
        session.add(newEmail)
        session.commit()
    except Exception as e:
        print(f"Error creating email: {e}")
        session.rollback()
    finally:
        session.close()


def exists_email(id):
    session = db_init()

    try:
        exists = session.query(Emails).filter(Emails.email_id == id).first()
        return exists is not None
    finally:
        session.close()



def transfer_emailsToTasks():
    session = db_init()

    try:
        with open('config.json', 'r') as configFile:
            config = json.load(configFile)


        clientEmails = get_all_client_emails()
        clientEmailsList = []
        for record in clientEmails:
            clientEmailsList.append(record['email'])

        emails = session.query(Emails).filter(Emails.task == None).all()
        for email in emails:
            try:
                for ignore in config['ignore_emails']:
                    if ignore in email.sender or email.sender not in clientEmailsList:
                        raise Exception("Skip")
            except Exception:
                continue
            email = email.to_dict()

            client_id = get_client(id=get_client_emails(email=email["sender"])[0]['client_id'])['id']
            insert_task({
                "support_id": f"SUP{str(datetime.datetime.now().year)[2:]}{str(get_newTaskID()).zfill(4)}",
                "client": client_id,
                "project": get_client(id=client_id)['projects'][0]['id'],
                "title": email["subject"],
                "description": email["content"],
                "employee": get_employee(full_name=app_secrets.get("DEFAULT_SUPPORT_OWNER"))['id'],
                "priority": get_task_priority(name="Low")['id'],
                "status": get_task_status(name="Income")['id'],
                "arrived": email["date"],
                "due": email["date"] + timedelta(days=7),
                "email_id": str(email["id"]),
                "reply_email": str(email['sender'])
            })
    except Exception as e:
        print(f"Error transferring: {e}")
        session.rollback()
    finally:
        session.close()




def assignProjectToClient(client_id, project_id):
    session = db_init()

    try:
        client = session.query(Clients).filter_by(id=int(client_id)).first()
        project = session.query(Projects).filter_by(id=int(project_id)).first()

        if not client:
            raise ValueError("Client with id=1 not found")
        if not project:
            raise ValueError("Project with id=1 not found")

        client.projects.append(project)
        session.commit()
        

    except Exception as e:
        print(f"Error pairing records: {e}")
        session.rollback()
    finally:
        session.close()

#######################################################
#######################################################
#######################################################


def get_one(model: Type[Any], include_relationships: Optional[list] | Optional[bool] = False, exclude_relationships: Optional[list] = None, max_depth:Optional[int]=1, **kwargs) -> dict:
    """
    Parameters
    ----------
        model : Type[Any]
            - Class of the table

        include_relationships : Optional[list] | Optional[bool]
            - list: include listed tables
            - bool: True = include all, False = include none
            - default = False
        
        exclude_relationships : Optional[list]
            - list: exclude listed tables
            - default = None

        max_depth : Optional[int]
            - Max depth the relationshiops should be included
            - default = 1

        **kwargs
            - Identifiers
    
    """
    session = db_init()
    try:
        record = session.query(model).filter_by(**kwargs).first()
        if record:
            return record.to_dict(include_relationships=include_relationships ,exclude_relationships=exclude_relationships, max_depth=max_depth)
        raise Exception(f"{model.__name__} searched by '{kwargs}' not found.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_one({model.__name__}): {e}")
        null = session.query(model).first()
        return null.to_dict(include_relationships=include_relationships ,exclude_relationships=exclude_relationships) if null else {}
    finally:
        session.close()


def get_all(model: Type[Any], exclude_relationships: Optional[list] = None, include_relationships: Optional[list] | Optional[bool] = False, max_depth:Optional[int]=1, filters: Optional[dict] = None):
    session = db_init()
    try:
        query = session.query(model)
        if filters:
            query = query.filter_by(**filters)
        records = query.all()
        return [r.to_dict(exclude_relationships=exclude_relationships, include_relationships=include_relationships) for r in records]
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in get_all({model.__name__}): {e}")
        null = session.query(model).first()
        return [null.to_dict()] if null else []
    finally:
        session.close()


def insert_one(model: Type[Any], data: dict, related_fields: Optional[dict] = None):
    """
    Parameters
    ----------
        model : Type[Any]
            - Class of the table

        data : dict
            - Data to insert

        related_fields: Optional[dict]
            - Syntax: {"referenced_value": (ReferencedTableClass, "search_key")}
        
        Ex. `insert_one(Projects, {"url": "http://...", "status": 1}, related_fields={"status": (ProjectsStatuses, "name")})`
    
    """
    session = db_init()
    try:
        # Resolve related fields (foreign keys by name or id)
        if related_fields:
            for field, (related_model, key) in related_fields.items():
                value = data.get(field)
                if isinstance(value, int) or (isinstance(value, str) and value.isnumeric()):
                    rel_obj = session.query(related_model).filter_by(id=value).first()
                else:
                    rel_obj = session.query(related_model).filter_by(**{key: value}).first()
                data[field] = rel_obj

        record = model(**data)
        session.add(record)
        session.commit()
        return record.id
    except Exception as e:
        print(f"Error creating {model.__name__}: {e}")
        session.rollback()
    finally:
        session.close()


def update_one(model: Type[Any], record_id: Any, updates: dict):
    session = db_init()
    try:
        record = session.query(model).filter_by(id=record_id).first()
        if record:
            for key, value in updates.items():
                setattr(record, key, value)
        else:
            raise Exception(f"No {model.__name__} record found with id {record_id}.")
    except Exception as e:
        print(f"Error updating {model.__name__}: {e}")
        session.rollback()
    finally:
        session.commit()
        session.close()

def delete_one(model: Type[Any], record_id: Any):
    session = db_init()
    try:
        record = session.query(model).filter_by(id=record_id).first()
        if record:
            session.delete(record)
            session.commit()
            return True
        else:
            raise Exception(f"No {model.__name__} record found with id {record_id}.")
    except Exception as e:
        print(f"Error deleting {model.__name__}: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def delete_by_filters(model: Type[Any], filters: dict):
    session = db_init()
    try:
        query = session.query(model).filter_by(**filters)
        count = query.delete()
        session.commit()
        return count
    except Exception as e:
        print(f"Error deleting {model.__name__} by filters: {e}")
        session.rollback()
        return 0
    finally:
        session.close()
