
# Code Scanner Backend

Backend services for the **Code Scanner system**.

This repository contains the backend infrastructure responsible for authentication, update distribution, and version management for the Code Scanner client application.

The backend exposes APIs used by clients to securely authenticate, retrieve scanner updates, and manage version releases.

---

# Architecture Overview

The repository is organized as a **multi-service backend** with shared libraries and database migration tools.

Main components:

- **identity-service** – Handles authentication, token validation, and user identity management.
- **updates-service** – Manages scanner update versions, archives, and distribution.
- **shared_lib** – Common utilities, shared schemas, and reusable components.
- **db_migrator** – Database schema migrations and initialization utilities.

---

# Features

- JWT-based authentication
- Secure token validation
- Update version management
- Update archive distribution
- Feature flag configuration support
- PostgreSQL database integration
- Alembic database migrations
- Modular microservice architecture
- Docker support for containerized deployment

---

# Tech Stack

Core technologies used in this project:

- **Python**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **Alembic**
- **PyJWT**
- **Docker**
- **Pydantic**

---

# Repository Structure

```
app/
 ├── identity-service/      # Authentication and token management service
 ├── updates-service/       # Scanner update management service
 ├── shared_lib/            # Shared utilities and common code
 └── db_migrator/           # Database migrations and initialization

json-sample/                # Example configuration and metadata files
tests/                      # Backend tests
.github/workflows/          # CI/CD pipelines
```

---

# Prerequisites

Before running the project, make sure you have:

- Python **3.10+**
- PostgreSQL
- Docker (optional but recommended)
- pip or poetry

---

# Environment Variables

Typical environment variables required by services:

```
DATABASE_URL=postgresql://user:password@localhost:5432/code_scanner
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=60
```

---

# Installation

Clone the repository:

```
git clone <repository-url>
cd code-scanner-backend
```

Install dependencies:

```
pip install -r requirements.txt
```

---

# Database Setup

Run database migrations:

```
python app/db_migrator/run_migrations.py
```

This will:

- create required tables
- apply Alembic migrations
- initialize base data

---

# Running the Services

Example of running a service locally:

```
cd app/identity-service
uvicorn main:app --reload --port 8000
```

Updates service:

```
cd app/updates-service
uvicorn main:app --reload --port 8001
```

---

# API Documentation

Once a service is running, interactive API documentation is available at:

```
http://localhost:8000/docs
```

FastAPI automatically generates:

- Swagger UI
- OpenAPI specification

---

# Docker Deployment

Build and run services using Docker:

```
docker build -t code-scanner-backend .
docker run -p 8000:8000 code-scanner-backend
```

For production setups, use Docker Compose or Kubernetes.

---

# Configuration Samples

The `json-sample/` directory contains example configuration files such as:

- app configuration
- feature flags
- release information

These can be used as templates for environment-specific configurations.

---

# Testing

Run tests using:

```
pytest
```

Tests are located in the `tests/` directory.

---

# CI/CD

GitHub Actions workflows are configured in:

```
.github/workflows/
```

These workflows can be used to:

- run tests
- build containers
- deploy to staging environments

---

# Security Notes

- Store secrets using environment variables or a secrets manager
- Never commit credentials to the repository
- Rotate JWT secrets periodically
- Restrict database access in production
