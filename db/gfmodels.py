from .gflog import Base

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Date, Float, func, text, Boolean, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped, mapped_column, DeclarativeMeta
from sqlalchemy.schema import Computed
from sqlalchemy.inspection import inspect
import datetime
from typing import TypedDict, Optional
from datetime import timedelta



class SerializableMixin:
    def to_dict(self, include_relationships=False, max_depth=1, _depth=0):
        result = {}
        mapper = inspect(self).mapper

        # Columns
        for c in mapper.column_attrs:
            result[c.key] = getattr(self, c.key)

        # Relationships
        if include_relationships and _depth < max_depth:
            for rel in mapper.relationships:
                value = getattr(self, rel.key)

                if value is None:
                    result[rel.key] = None
                elif rel.uselist:
                    result[rel.key] = [
                        v.to_dict(include_relationships=True, max_depth=max_depth, _depth=_depth+1)
                        for v in value
                    ]
                else:
                    result[rel.key] = value.to_dict(include_relationships=True, max_depth=max_depth, _depth=_depth+1)

        return result
    









# Association Table
clients_projects_association = Table(
    'clients_projects',
    Base.metadata,
    Column('client_id', Integer, ForeignKey('clients.id'), primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True)
)



########## Timetrackers ##########

class Timetrackers(Base, SerializableMixin):
    __tablename__ = 'timetrackers'

    id = Column(Integer, primary_key=True, autoincrement=True)

    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    task = relationship('Tasks', back_populates='timetrackers')

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship('Employees', back_populates='timetrackers')

    start = Column(DateTime, nullable=True)
    end: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)

########## Employees ##########

class Employees(Base, SerializableMixin):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    full_name = Column(String, Computed(text("first_name || ' ' || last_name"), persisted=True), nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    position_id = Column(Integer, ForeignKey('employeePositions.id'), nullable=False)
    position = relationship('EmployeePositions', back_populates='employees')

    tasks = relationship('Tasks', back_populates='employee')
    timetrackers = relationship('Timetrackers', back_populates='employee')

class EmployeePositions(Base, SerializableMixin): # FINE
    __tablename__ = 'employeePositions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    employees = relationship('Employees', back_populates='position')

########## Clients ##########

class Clients(Base, SerializableMixin):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    full_name = Column(String, Computed(text("first_name || ' ' || last_name"), persisted=True), nullable=False)


    emails = relationship("ClientsEmails", back_populates="client", cascade="all, delete-orphan")
    tasks = relationship("Tasks", back_populates="client")

    projects = relationship(
        'Projects',
        secondary=clients_projects_association,
        back_populates='clients'
    )


class ClientsEmails(Base, SerializableMixin): # FINE
    __tablename__ = 'clientsEmails'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    email = Column(String)
    client = relationship("Clients", back_populates="emails")
    
########## TASKS ##########

class Tasks(Base, SerializableMixin):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    support_id = Column(String, nullable=False, unique=True)

    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship('Clients', back_populates='tasks')

    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    project = relationship('Projects', back_populates='tasks')

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship('Employees', back_populates=('tasks'))

    priority_id = Column(Integer, ForeignKey('taskPriorities.id'), nullable=False)
    priority = relationship('TaskPriorities', back_populates='tasks')

    status_id = Column(Integer, ForeignKey('taskStatuses.id'), nullable=False)
    status = relationship('TaskStatuses', back_populates='tasks')


    hidden : Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    
    # Another status but to determine whether to hide the task from view or not and other


    arrived = Column(DateTime, nullable=True)
    due = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True, default=0)
    started = Column(DateTime, nullable=True)
    finished = Column(DateTime, nullable=True)

    email_id = Column(Integer, ForeignKey('emails.id'), nullable=True)
    email = relationship('Emails', back_populates='task', uselist=False)

    timetrackers = relationship('Timetrackers', back_populates='task')

    

    def __repr__(self):
        return (f"<Task(id={self.id}, support_id='{self.support_id}', client='{self.client}', "
                f"project='{self.project}', title='{self.title}', employee='{self.employee}', "
                f"priority='{self.priority}', status='{self.status}', arrived={self.arrived}, "
                f"duration={self.duration}, started={self.started}, finished={self.finished})>")
    
class TaskPriorities(Base, SerializableMixin): # FINE
    __tablename__ = 'taskPriorities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='priority')

class TaskStatuses(Base, SerializableMixin): # FINE
    __tablename__ = 'taskStatuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String, nullable=False)

    tasks = relationship('Tasks', back_populates='status')

########## EMAILS ##########

class Emails(Base, SerializableMixin): # FINE
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, autoincrement=True)

    email_id = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    content = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)

    task = relationship('Tasks', back_populates='email', uselist=False)

########## PROJECTS ##########

class ProjectsStatuses(Base, SerializableMixin): # FINE
    __tablename__ = 'projectsStatuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    projects = relationship('Projects', back_populates='status')    

class Projects(Base, SerializableMixin): # REVISIT
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)

    status_id = Column(Integer, ForeignKey('projectsStatuses.id'), nullable=False)
    status = relationship('ProjectsStatuses', back_populates='projects')

    clients = relationship(
        'Clients',
        secondary=clients_projects_association,
        back_populates='projects'
    )

    tasks = relationship('Tasks', back_populates='project')


