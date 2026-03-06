from handler.postgres_migration import PostgresMigrationHandler


def run_migrations():

    db_migrators = [
        PostgresMigrationHandler()
    ]

    for migrator in db_migrators:
        migrator.execute()


if __name__ == "__main__":
    run_migrations()
