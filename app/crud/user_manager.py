from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password
from app.schemas.user import UserResponse


def create(user_data, session: Session):

    hashed_password = hash_password(user_data.password)

    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserResponse.model_validate(user)


def get_user_by_email(email: str, session: Session):

    user = (
        session.query(User)
        .filter(User.email == email)
        .first()
    )

    return user


def get_user_by_id(user_id: int, session: Session):

    user = (
        session.query(User)
        .filter(User.id == user_id)
        .first()
    )

    return user