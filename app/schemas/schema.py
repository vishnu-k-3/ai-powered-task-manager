from datetime import date
from pydantic import BaseModel, ConfigDict

class Task(BaseModel):
    title: str
    completed: bool = False
    description: str
    status: str
    due_date: date | None = None

class Update_Task(BaseModel):
    title: str | None = None
    completed: bool | None = None
    description: str | None = None
    status: str | None = None
    due_date: date | None = None

class Task_Response(BaseModel):
    id:int
    title: str
    completed: bool = False
    description: str | None = None
    status: str | None = None
    due_date: date | None = None

    model_config = ConfigDict(from_attributes=True)
