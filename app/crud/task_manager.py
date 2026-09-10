from sqlalchemy.orm import Session

from app.models.task import Todo
from app.schemas.schema import Update_Task


def add(task_data, user_id: int, session: Session):

    task = Todo(
        owner_id=user_id,
        title=task_data["title"],
        completed=task_data["completed"],
        description=task_data["description"],
        status=task_data["status"],
        due_date=task_data["due_date"]
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def view_all(user_id: int, session: Session):

    return session.query(Todo).filter(Todo.owner_id == user_id).all()


def view(task_id: int, user_id: int, session: Session):

    task = session.get(Todo, task_id)
    if task and task.owner_id == user_id:
        return task
    return None


def delete(task_id: int, user_id: int, session: Session):

    task = view(task_id, user_id, session)

    if task:
        session.delete(task)
        session.commit()

    return session.query(Todo).all()


def update(task: Todo, update_data: Update_Task, session: Session):

    data = update_data.model_dump(exclude_unset=True)
    
    for key, value in data.items():
        setattr(task, key, value)
    session.commit()
    session.refresh(task)
    return task

def view_by_status(status: str, user_id: int, session: Session):

    return (
        session.query(Todo)
        .filter(Todo.status == status)
        .filter(Todo.owner_id == user_id)
        .all()
    )