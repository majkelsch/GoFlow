from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime
from typing import TypedDict, Optional

DATABASE_FILE = 'goflow.db'
DATABASE_URL = f'sqlite:///{DATABASE_FILE}'

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class TaskCategoryDict(TypedDict):
    name: str

class ClientDict(TypedDict):
    name: str

class ProjectDict(TypedDict):
    name: str

class OwnerDict(TypedDict):
    name: str

class PriorityDict(TypedDict):
    name: str

class StatusDict(TypedDict):
    name: str

class TaskDict(TypedDict):
    category_id: int
    client_id: int
    project_id: int
    title: str
    description: str
    owner_id: int
    priority_id: int
    status_id: int
    started_at: Optional[datetime.datetime]
    completed_at: Optional[datetime.datetime]
    due_date: datetime.datetime
    duration: int






# Could be used somewhere else, reconsider naming
class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='category')

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"





class Genders(Base):
    __tablename__ = 'genders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    clients = relationship('Clients', back_populates='genders')

    def __repr__(self):
        return f"<Gender(id={self.id}, name='{self.name}')>"
    


    
class Companies(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    ic = Column(String, nullable=True)
    dic = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    psc = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    url = Column(String, nullable=True)
    data_box = Column(String, nullable=True)
    contact_person_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    contact_person = relationship('Clients', back_populates='Companies')
    
    drive_folder_id = Column(String, nullable=True)
    company_status_id = Column(Integer, ForeignKey('companystatuses.id'), nullable=False)
    company_status = relationship('Companies', back_populates='Companies')

    # Possibly more


    clients = relationship('Clients', back_populates='companies')

    def __repr__(self):
        return f"<Company(id={self.id})>"
    


class CompanyStatuses(Base):
    __tablename__ = 'companystatuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    company = relationship('Companies', back_populates='companystatuses')

    def __repr__(self):
        return f"<Status(id={self.id}, name='{self.name}')>"



class ClientStatuses(Base):
    __tablename__ = 'clientstatuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    clients = relationship('Clients', back_populates='clientstatuses')

    def __repr__(self):
        return f"<Status(id={self.id}, name='{self.name}')>"






class Clients(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title_before = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    title_after = Column(String, nullable=False)
    gender_id = Column(Integer, ForeignKey('genders.id'), nullable=False)
    gender = relationship('Genders', back_populates='clients')

    date_of_birth = Column(Date, nullable=False)
    phone_primary = Column(String, nullable=False)
    phone_secondary = Column(String, nullable=True)
    email_primary = Column(String, nullable=False)
    email_secondary = Column(String, nullable=True)
    adress_as = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    company = relationship('Companies', back_populates='clients')

    client_status_id = Column(Integer, ForeignKey('clientstatuses.id'), nullable=False)
    client_status = relationship('ClientStatuses', back_populates='clients')

    # Possibly more data


    tasks = relationship('Tasks', back_populates='client')

    def __repr__(self):
        # Finish the rest
        return f"<Client(id={self.id})>"
    










class Projects(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='project')

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"

class Owners(Base):
    __tablename__ = 'owners'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='owner')

    def __repr__(self):
        return f"<Owner(id={self.id}, name='{self.name}')>"

class Priorities(Base):
    __tablename__ = 'priorities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='priority')

    def __repr__(self):
        return f"<Priority(id={self.id}, name='{self.name}')>"

class Statuses(Base):
    __tablename__ = 'statuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='status')

    def __repr__(self):
        return f"<Status(id={self.id}, name='{self.name}')>"

class Tasks(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship('Categories', back_populates='tasks')

    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship('Clients', back_populates='tasks')

    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    project = relationship('Projects', back_populates='tasks')

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey('owners.id'), nullable=False)
    owner = relationship('Owners', back_populates='tasks')

    priority_id = Column(Integer, ForeignKey('priorities.id'), nullable=False)
    priority = relationship('Priorities', back_populates='tasks')

    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    status = relationship('Statuses', back_populates='tasks')

    created_at = Column(DateTime, nullable=False)  # Můžete použít DateTime pro datum a čas
    started_at = Column(DateTime, nullable=True)  # Můžete použít DateTime pro datum a čas
    completed_at = Column(DateTime, nullable=True)  # Můžete použít DateTime pro datum a čas
    due_date = Column(DateTime, nullable=True)  # Můžete použít DateTime pro datum a čas
    duration = Column(Integer, nullable=True, default=0)  # Doba trvání v minutách

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', category='{self.category.name}', client='{self.client.name}', project='{self.project.name}', owner='{self.owner.name}', priority='{self.priority.name}', status='{self.status.name}')>"

Base.metadata.create_all(engine)


def db_init():
    DATABASE_FILE = 'tasks.db'
    DATABASE_URL = f'sqlite:///{DATABASE_FILE}'
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def createCategory_DB(data: TaskCategoryDict):
    session = db_init()
    try:
        newCategory = Categories(
            name=data['name']
        )
        session.add(newCategory)
        session.commit()
    except Exception as e:
        print(f"Error creating task: {e}")
        session.rollback()
    finally:
        session.close()

def createClient_DB(data: ClientDict):
    session = db_init()
    try:
        newClient = Clients(
            name=data['name']
        )
        session.add(newClient)
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
            name=data['name']
        )
        session.add(newProject)
        session.commit()
    except Exception as e:
        print(f"Error creating task: {e}")
        session.rollback()
    finally:
        session.close()

def createOwner_DB(data: OwnerDict):
    session = db_init()
    try:
        newOwner = Owners(
            name=data['name']
        )
        session.add(newOwner)
        session.commit()
    except Exception as e:
        print(f"Error creating task: {e}")
        session.rollback()
    finally:
        session.close()

def createPriority_DB(data: PriorityDict):
    session = db_init()
    try:
        newPriority = Priorities(
            name=data['name']
        )
        session.add(newPriority)
        session.commit()
    except Exception as e:
        print(f"Error creating task: {e}")
        session.rollback()
    finally:
        session.close()

def createStatus_DB(data: StatusDict):
    session = db_init()
    try:
        newStatus = Statuses(
            name=data['name']
        )
        session.add(newStatus)
        session.commit()
    except Exception as e:
        print(f"Error creating task: {e}")
        session.rollback()
    finally:
        session.close()

def createTask_DB(data: TaskDict):
    session = db_init()
    try:
        newTask = Tasks(
            category_id=data['category_id'],
            client_id=data['client_id'],
            project_id=data['project_id'],
            title=data['title'],
            description=data.get('description', ''),
            owner_id=data['owner_id'],
            priority_id=data['priority_id'],
            status_id=data['status_id'],
            created_at=datetime.datetime.now(),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
            due_date=data.get('due_date'),
            duration=data.get('duration')
        )
        session.add(newTask)
        session.commit()
    except Exception as e:
        print(f"Error creating task: {e}")
        session.rollback()
    finally:
        session.close()