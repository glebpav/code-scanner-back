"""create update_version and update_version_file tables

Revision ID: c8d4e2c1f901
Revises: b2104def5631
Create Date: 2026-03-07 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c8d4e2c1f901"
down_revision: Union[str, None] = "b2104def5631"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "update_version",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), sa.Identity(start=1), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("version_number", name="uq_update_version_version_number"),
    )
    op.create_index(
        "ix_update_version_version_number",
        "update_version",
        ["version_number"],
        unique=True,
    )

    op.create_table(
        "update_version_file",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("update_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("s3_key", sa.String(length=1024), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["update_version_id"],
            ["update_version.id"],
            name="fk_update_version_file_update_version_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "update_version_id",
            "position",
            name="uq_update_version_file_position",
        ),
        sa.UniqueConstraint(
            "update_version_id",
            "s3_key",
            name="uq_update_version_file_s3_key",
        ),
    )
    op.create_index(
        "ix_update_version_file_update_version_id",
        "update_version_file",
        ["update_version_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_update_version_file_update_version_id", table_name="update_version_file")
    op.drop_table("update_version_file")

    op.drop_index("ix_update_version_version_number", table_name="update_version")
    op.drop_table("update_version")