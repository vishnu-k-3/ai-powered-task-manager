from pydantic import BaseModel

class Task(BaseModel):
    title: str
    completed: bool = False
    description: str
    status: str
    due_date: str

class Update_Task(BaseModel):
    title: str
    completed: bool = False
    description: str
    status: str
    due_date: str