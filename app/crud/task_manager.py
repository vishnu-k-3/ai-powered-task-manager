from sqlalchemy.orm import Session

from app.models.task import Todo


def add(task_data, session: Session):

    task = Todo(
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


def view_all(session: Session):

    return session.query(Todo).all()


def view(task_id: int, session: Session):

    return session.get(Todo, task_id)


def delete(task_id: int, session: Session):

    task = session.get(Todo, task_id)

    if task:
        session.delete(task)
        session.commit()

    return session.query(Todo).all()


def update(task_id: int, update_task, session: Session):

    task = session.get(Todo, task_id)

    if task:
        task.title = update_task.title
        task.completed = update_task.completed
        task.description = update_task.description
        task.status= update_task.status
        task.due_date= update_task.due_date

        session.commit()
        session.refresh(task)

    return task

def view_by_status(status: str, session: Session):

    return (
        session.query(Todo)
        .filter(Todo.status == status)
        .all()
    )