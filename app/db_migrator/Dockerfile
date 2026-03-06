FROM python:3.12

WORKDIR /app

COPY app/db_migrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем shared_lib
COPY app/shared_lib/ /app/app/shared_lib/
WORKDIR /app/app/shared_lib
RUN pip install -e .
WORKDIR /app

COPY app/db_migrator/alembic.ini .
COPY app/db_migrator/alembic alembic

COPY app/db_migrator db_migrator

ENV PYTHONPATH=/app

CMD ["sh", "-c", "python db_migrator/run_migrations.py && tail -f /dev/null"]