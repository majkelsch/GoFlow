from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime

DATABASE_FILE = 'tasks.db'
DATABASE_URL = f'sqlite:///{DATABASE_FILE}'

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Categories(Base):
    __tablename__ = 'categories'  # Název tabulky v databázi

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='category')

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

class Clients(Base):
    __tablename__ = 'clients'  # Název tabulky v databázi

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='client')

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}')>"

class Projects(Base):
    __tablename__ = 'projects'  # Název tabulky v databázi

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='project')

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"

class Owners(Base):
    __tablename__ = 'owners'  # Název tabulky v databázi

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='owner')

    def __repr__(self):
        return f"<Owner(id={self.id}, name='{self.name}')>"

class Priorities(Base):
    __tablename__ = 'priorities'  # Název tabulky v databázi

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='priority')

    def __repr__(self):
        return f"<Priority(id={self.id}, name='{self.name}')>"

class Statuses(Base):
    __tablename__ = 'statuses'  # Název tabulky v databázi

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='status')

    def __repr__(self):
        return f"<Status(id={self.id}, name='{self.name}')>"

class Tasks(Base):
    __tablename__ = 'tasks'  # Název tabulky v databázi

    id = Column(Integer, primary_key=True)
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

Session = sessionmaker(bind=engine)
session = Session()

newCategory = Categories(name='Development')
newClient = Clients(name='Client A')
newProject = Projects(name='Project X')
newOwner = Owners(name='John Doe')
newPriority = Priorities(name='High')
newStatus = Statuses(name='Open')
session.add_all([newCategory, newClient, newProject, newOwner, newPriority, newStatus])
session.commit()

newTask = Tasks(
    category_id=1,
    client_id=1,
    project_id=1,
    title='Implement Feature Y',
    description='Detailed description of the task.',
    owner_id=1,
    priority_id=1,
    status_id=1,
    created_at=datetime.datetime.now(),
    started_at=None,
    completed_at=None,
    due_date=datetime.datetime.now() + datetime.timedelta(days=7),  # Předpokládejme, že úkol má termín za 7 dní
    duration=120
)
session.add(newTask)
session.commit()
session.close()

def db_init():
    DATABASE_FILE = 'tasks.db'
    DATABASE_URL = f'sqlite:///{DATABASE_FILE}'
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session



def createTask_DB(data):
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
        print(f"Task '{data['title']}' created successfully.")
    except Exception as e:
        print(f"Error creating task: {e}")
        session.rollback()
    finally:
        session.close()


createTask_DB({
    'category_id': 1,
    'client_id': 1,
    'project_id': 1,
    'title': 'Test Task',
    'description': 'This is a test task.',
    'owner_id': 1,
    'priority_id': 1,
    'status_id': 1,
    'started_at': None,
    'completed_at': None,
    'due_date': datetime.datetime.now() + datetime.timedelta(days=3),
    'duration': 0
})