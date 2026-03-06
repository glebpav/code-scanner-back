import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool

from alembic import context

from shared_lib.db.models.base import PostgresAbstractEntity
from shared_lib.db.models.user import User, UserRole, Role


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = PostgresAbstractEntity.metadata


def run_migrations_offline() -> None:

    context.configure(
        url=os.environ['DB_URL'],
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:

    connectable = create_engine(os.environ['DB_URL'])

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
