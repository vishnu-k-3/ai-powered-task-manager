from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.crud.task_manager import (
    add,
    view,
    view_all,
    delete,
    update,
    view_by_status
)

from app.crud.user_manager import (
    create,
    get_user_by_email
)

from app.schemas.schema import Task, Update_Task
from app.schemas.user import UserCreate, UserLogin

from app.core.security import (
    create_access_token,
    verify_password
)

from app.core.auth import get_current_user


app = FastAPI()


# ---- task section ----

@app.get("/tasks")
def task_list(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    return view_all(current_user.id, db)


@app.get("/tasks/{task_id}")
def task(
    task_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = view(task_id, current_user.id, db)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )
    return task


@app.post("/tasks")
def task_add(
    task: Task,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_dict = task.model_dump()

    return add(task_dict, current_user.id, db)


@app.delete("/tasks/{task_id}")
def task_delete(
    task_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = view(task_id, current_user.id, db)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )
    delete(task_id, current_user.id, db)

    return view_all(current_user.id, db)


@app.patch("/tasks/{task_id}")
def task_update(
    task_id: int,
    updated_task: Update_Task,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = view(task_id, current_user.id, db)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )
    return update(task, updated_task, db)

@app.get("/tasks/status/{status}")
def tasks_by_status(
    status: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if status not in ["pending", "in_progress", "completed"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )
    return view_by_status(status, current_user.id, db)


# ---- user section ----

@app.post("/register")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = get_user_by_email(user.email, db)

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )
    return create(user, db)


@app.post("/login")
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = get_user_by_email(
        user_data.email,
        db
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }