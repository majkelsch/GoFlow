from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Date, Float, func, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.schema import Computed
import datetime
from typing import TypedDict, Optional
from datetime import timedelta

import app_secrets
import sys
import json

DATABASE_FILE = 'tasks-temp.db'
DATABASE_URL = f'sqlite:///{DATABASE_FILE}'

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class TaskDict(TypedDict):
    support_id: str
    client: str
    project: str
    title: str
    description: str
    employee: str
    priority: str
    status: str
    arrived: Optional[datetime.datetime]
    due: Optional[datetime.datetime]
    duration: float
    started: Optional[datetime.datetime]
    finished: Optional[datetime.datetime]
    email_id: Optional[str]
    last_edit_by: str

class ProjectDict(TypedDict):
    url: str
    status: str
    client: str
    mobile: Optional[str]
    mail: Optional[str]
    inv_mail: Optional[str]
    ignore: Optional[int]



class EmailsDict(TypedDict):
    email_id: str
    sender: str
    subject: str
    date: datetime.datetime
    content: str
    task: Optional[int]























class Employees(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    full_name = Column(String, Computed(text("first_name || ' ' || last_name"), persisted=True), nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    position = Column(String, nullable=False)           # bind to new table

    tasks = relationship('Tasks', back_populates='employee')


    
    

class Tasks(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    support_id = Column(String, nullable=False, unique=True)
    client = Column(String, nullable=False)                 # Bind to new table
    project = Column(String, nullable=False)                # Bind to updated table
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship('Employees', back_populates=('tasks'))

    priority_id = Column(Integer, ForeignKey('priorities.id'), nullable=False)
    priority = relationship('Priorities', back_populates='tasks')

    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    status = relationship('Statuses', back_populates='tasks')


    arrived = Column(DateTime, nullable=True)
    due = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True, default=0)
    started = Column(DateTime, nullable=True)
    finished = Column(DateTime, nullable=True)

    email_id = Column(Integer, ForeignKey('emails.id'), nullable=True)
    email = relationship('Emails', back_populates='task', uselist=False)

    last_edit_by = Column(String, nullable=True)            # Create logging

    

    def __repr__(self):
        return (f"<Task(id={self.id}, support_id='{self.support_id}', client='{self.client}', "
                f"project='{self.project}', title='{self.title}', employee='{self.employee}', "
                f"priority='{self.priority}', status='{self.status}', arrived={self.arrived}, "
                f"duration={self.duration}, started={self.started}, finished={self.finished})>")
    


class Priorities(Base):
    __tablename__ = 'priorities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='priority')

class Statuses(Base):
    __tablename__ = 'statuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='status')



class Emails(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, autoincrement=True)

    email_id = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    content = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)

    task = relationship('Tasks', back_populates='email', uselist=False)
    

class Projects(Base):   # REVISIT
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    status = Column(String, nullable=False)             # bind to new table
    client = Column(String, nullable=False)             
    mobile = Column(String, nullable=True)              
    mail = Column(String, nullable=True)
    inv_mail = Column(String, nullable=True)
    ignore = Column(Integer, nullable=True, default=0)

    def __repr__(self):
        return (f"<Project(id={self.id}, url='{self.url}', status='{self.status}', "
                f"client='{self.client}', mobile='{self.mobile}', mail='{self.mail}', "
                f"inv_mail='{self.inv_mail}', ignore={self.ignore})>")


Base.metadata.create_all(engine)

def db_init():
    DATABASE_FILE = 'tasks-temp.db'
    DATABASE_URL = f'sqlite:///{DATABASE_FILE}'
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def createTask_DB(data: TaskDict):
    session = db_init()
    try:
        newTask = Tasks(
            support_id=data['support_id'],
            client=data['client'],
            project=data['project'],
            title=data['title'],
            description=data.get('description', ''),
            employee=data['employee'],
            priority=data['priority'],
            status=data['status'],
            arrived=data.get('arrived', None),
            due=data.get('due', None),
            duration=data.get('duration', 0.0),
            started=data.get('started', None),
            finished=data.get('finished', None),
            email_id=data.get('email_id', None),
            last_edit_by=data.get('last_edit_by', None)
        )
        session.add(newTask)
        session.commit()
    except Exception as e:
        print(f"Error creating task: {e}")
        session.rollback()
    finally:
        session.close()

def createProject_DB(data: ProjectDict):
    session = db_init()

    try:
        newProject = Projects(
            url=data['url'],
            status=data['status'],
            client=data['client'],
            mobile=data.get('mobile', None),
            mail=data.get('mail', None),
            inv_mail=data.get('inv_mail', None),
            ignore=data.get('ignore', 0)
        )
        session.add(newProject)
        session.commit()
    except Exception as e:
        print(f"Error creating project: {e}")
        session.rollback()
    finally:
        session.close()

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





def set_lastEditBy(id):
    session = db_init()
    try:
        row = session.query(Tasks).filter(Tasks.id == id).first()
        if row is not None:
            row.last_edit_by = "GoFlow Importer" # type: ignore
            session.commit()
        else:
            print(f"Task with id {id} not found.")
    finally:
        session.close()

def get_allTasks():
    session = db_init()
    try:
        tasks = session.query(Tasks).all()
        return [task.__dict__ for task in tasks]
    finally:
        session.close()

def get_taskBySupportID(id):
    session = db_init()
    try:
        task_obj = session.query(Tasks).filter(Tasks.support_id == id).first()
        if task_obj is not None:
            return task_obj.__dict__.copy()
        else:
            print(f"Task with support_id {id} not found.")
            sys.exit(-1)
    finally:
        session.close()


def get_employeeByFullName(full_name):
    session = db_init()
    try:
        employee = session.query(Employees).filter(Employees.full_name == full_name).first()
        if employee is not None:
            return employee.__dict__
        else:
            print(f"Employee with full_name {full_name} not found.")
            return app_secrets.get("GOOGLE_SUPPORT_EMAIL")
    finally:
        session.close()

def get_employeeByEmail(email):
    session = db_init()
    try:
        employee = session.query(Employees).filter(Employees.email == email).first()
        if employee is not None:
            return employee.__dict__
        else:
            raise ValueError(f"Employee with email {email} not found.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in db_control_simple.py: {e}")
    finally:
        session.close()













########## EMAILS ##########

def insert_email(data: EmailsDict):
    session = db_init()

    try:
        newEmail = Emails(
            email_id = data['email_id'],
            sender = data['sender'],
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

        emails = session.query(Emails).filter(Emails.task == None).all()
        for email in emails:
            try:
                for ignore in config['ignore_emails']:
                    if ignore in email.sender:
                        raise Exception()
            except Exception:
                continue
            email = email.__dict__
            createTask_DB({
                "support_id": f"SUP{str(datetime.datetime.now().year)[2:]}{str(get_newTaskID()).zfill(4)}",
                "client": email["sender"],
                "project": email["sender"],
                "title": email["subject"],
                "description": email["content"],
                "employee": "Daniel",
                "priority": "Low",
                "status": "Income",
                "arrived": email["date"],
                "due": email["date"] + timedelta(days=7),
                "duration": 0.0,
                "started": None,
                "finished": None,
                "email_id": str(email["id"]),
                "last_edit_by": "GoFlow Importer"
            })
    except Exception as e:
        print(f"Error transferring: {e}")
        session.rollback()
    finally:
        session.close()

