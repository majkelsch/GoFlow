
from typing import TypedDict, Optional
import datetime



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

class EmployeeDict(TypedDict):
    first_name: str
    last_name: str
    email: str
    phone: str
    position: str

class ProjectStatusDict(TypedDict):
    name: str