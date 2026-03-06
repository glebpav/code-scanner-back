from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Enum as SQLAlchemyEnum, String, Integer, Date, Boolean, UUID, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from enum import Enum

from shared_lib.db.models.base import PostgresAbstractEntity


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class Role(PostgresAbstractEntity):
    __tablename__ = "user_role"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[UserRole] = mapped_column(SQLAlchemyEnum(UserRole), unique=True, nullable=False)


class User(PostgresAbstractEntity):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    email: Mapped[str] = mapped_column(String(256), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Base information
    first_name: Mapped[Optional[str]] = mapped_column(String(128))
    last_name: Mapped[Optional[str]] = mapped_column(String(128))
    position: Mapped[Optional[str]] = mapped_column(String(128))
    company: Mapped[Optional[str]] = mapped_column(String(128))

    # Foreign keys
    role_id: Mapped[int] = mapped_column(
        ForeignKey("user_role.id"),
        nullable=False
    )

    # Relationships
    role: Mapped["Role"] = relationship()

    def __repr__(self) -> str:
        return f"{self.id} {self.first_name} {self.last_name}"
