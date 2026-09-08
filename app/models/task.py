from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

from app.db.database import Base


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    description: Mapped[str | None]

    status: Mapped[str | None] = mapped_column(
        String(50)
    )

    due_date: Mapped[str | None] = mapped_column(
        String(110)
    )