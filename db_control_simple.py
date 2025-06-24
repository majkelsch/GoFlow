from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Date, Float, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime
from typing import TypedDict, Optional

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
    owner: str
    priority: str
    status: str
    arrived: Optional[datetime.datetime]
    duration: float
    started: Optional[datetime.datetime]
    finished: Optional[datetime.datetime]

class ProjectDict(TypedDict):
    url: str
    status: str
    client: str
    mobile: Optional[str]
    mail: Optional[str]
    inv_mail: Optional[str]
    ignore: Optional[int]
    
    

class Tasks(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    support_id = Column(String, nullable=False, unique=True)
    client = Column(String, nullable=False)
    project = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    status = Column(String, nullable=False)
    arrived = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True, default=0)
    started = Column(DateTime, nullable=True)
    finished = Column(DateTime, nullable=True)
    email_id = Column(String, nullable=True)

    

    def __repr__(self):
        return (f"<Task(id={self.id}, support_id='{self.support_id}', client='{self.client}', "
                f"project='{self.project}', title='{self.title}', owner='{self.owner}', "
                f"priority='{self.priority}', status='{self.status}', arrived={self.arrived}, "
                f"duration={self.duration}, started={self.started}, finished={self.finished})>")
    

class Projects(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    status = Column(String, nullable=False)
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
            owner=data['owner'],
            priority=data['priority'],
            status=data['status'],
            arrived=data.get('arrived', None),
            duration=data.get('duration', 0.0),
            started=data.get('started', None),
            finished=data.get('finished', None),
            email_id=data.get('email_id', None)
        )
        session.add(newTask)
        session.commit()
    except Exception as e:
        print(f"Error creating task: {e}")
        session.rollback()
    finally:
        session.close()

def creteateProject_DB(data: ProjectDict):
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


def check_existingMailID(id):
    session = db_init()
    try:
        exists = session.query(Tasks).filter(Tasks.email_id == id).first()
        return exists is not None
    finally:
        session.close()