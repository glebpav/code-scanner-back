FROM python:3.9-slim
WORKDIR /app

COPY app/identity-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/shared_lib/ /app/app/shared_lib/
WORKDIR /app/app/shared_lib
RUN pip install -e .
WORKDIR /app

COPY app/identity-service/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]