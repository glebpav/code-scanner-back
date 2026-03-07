from datetime import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, Identity, Integer, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared_lib.db.models.base import PostgresAbstractEntity


class UpdateVersion(PostgresAbstractEntity):
    __tablename__ = "update_version"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    version_number: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        unique=True,
        index=True,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    files: Mapped[list["UpdateVersionFile"]] = relationship(
        "UpdateVersionFile",
        back_populates="update_version",
        cascade="all, delete-orphan",
        order_by="UpdateVersionFile.position",
    )

    def __repr__(self) -> str:
        return f"UpdateVersion(version_number={self.version_number})"


class UpdateVersionFile(PostgresAbstractEntity):
    __tablename__ = "update_version_file"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    update_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("update_version.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    s3_key: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    update_version: Mapped["UpdateVersion"] = relationship(
        "UpdateVersion",
        back_populates="files",
    )

    def __repr__(self) -> str:
        return f"UpdateVersionFile({self.s3_key})"