import os
import subprocess

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from data_initializer import DataInitializer
from handler.migration_handler import MigrationHandler


class PostgresMigrationHandler(MigrationHandler):

    def __init__(self):
        super().__init__(
            migrator_name="Postgres Migration Handler"
        )

    def _make_migration(self):

        # print("Migration generation")
        # subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Auto-generated schema"], check=True)

        subprocess.run(["alembic", "upgrade", "head"], check=True)

        try:

            print("Data insertion")
            engine = create_engine(os.environ["DB_URL"])
            with Session(engine) as session:
                DataInitializer.seed_all(session)
            print("All migrations applied and data inserted")

        except Exception as e:
            print(e)
