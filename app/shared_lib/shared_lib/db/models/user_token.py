from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.orm import Mapped

from shared_lib.db.models.base import PostgresAbstractEntity


class UserToken(PostgresAbstractEntity):
    __tablename__ = "user_token"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )


    def __repr__(self) -> str:
        return f"Token({self.id}) active={self.is_active}"