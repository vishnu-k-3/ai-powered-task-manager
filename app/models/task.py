from datetime import date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Date, ForeignKey

from app.db.database import Base


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id")
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

    due_date: Mapped[date | None] = mapped_column(
        Date
    )