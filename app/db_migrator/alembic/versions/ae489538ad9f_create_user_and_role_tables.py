from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "ae489538ad9f"
down_revision = None
branch_labels = None
depends_on = None

user_role_enum = postgresql.ENUM("ADMIN", "USER", name="userrole")


def upgrade() -> None:
    op.create_table(
        "user_role",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", user_role_enum, nullable=False),
        sa.UniqueConstraint("name", name="uq_user_role_name"),
    )

    op.create_table(
        "user",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=256), nullable=False),
        sa.Column("hashed_password", sa.String(length=256), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column("last_name", sa.String(length=128), nullable=True),
        sa.Column("position", sa.String(length=128), nullable=True),
        sa.Column("company", sa.String(length=128), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["user_role.id"], name="fk_user_role_id"),
    )

    op.create_index("ix_user_email", "user", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_user_email", table_name="user")
    op.drop_table("user")
    op.drop_table("user_role")