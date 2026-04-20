# TaskFlow API

A production-grade REST API for task management with JWT authentication, role-based access control, and PostgreSQL persistence.

Built with **FastAPI**, **SQLAlchemy**, and **Alembic** — showcasing clean architecture, proper testing, and containerized deployment.

## Features

- 🔐 **JWT Authentication** — Register, login, token refresh
- 📋 **Full Task CRUD** — Create, read, update, delete with filtering & pagination
- 🛡️ **Role-Based Access Control** — Admin vs User permissions
- 🐘 **PostgreSQL** — Production-grade database with Alembic migrations
- ✅ **Input Validation** — Pydantic schemas for request/response validation
- 📖 **Auto-Generated Docs** — Swagger UI & ReDoc out of the box
- 🧪 **Test Suite** — pytest with async support and test database
- 🐳 **Docker Compose** — One command to run the full stack

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.110+ |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Auth | python-jose (JWT) + passlib (bcrypt) |
| Validation | Pydantic v2 |
| Testing | pytest + httpx |
| Container | Docker + Docker Compose |

## Quick Start

```bash
# Clone and enter the project
git clone https://github.com/sepulchralvoid666/taskflow-api.git
cd taskflow-api

# Start the full stack with Docker
docker compose up --build

# API docs available at:
# Swagger UI → http://localhost:8000/docs
# ReDoc      → http://localhost:8000/redoc
```

## Running Locally (without Docker)

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

## Project Structure

```
taskflow-api/
├── app/
│   ├── api/
│   │   ├── deps.py          # Dependency injection (DB sessions, current user)
│   │   ├── auth.py          # Auth endpoints (register, login, refresh)
│   │   └── tasks.py         # Task endpoints (CRUD + filtering)
│   ├── core/
│   │   ├── config.py        # Settings from environment variables
│   │   ├── security.py      # JWT creation/verification, password hashing
│   │   └── database.py      # Async engine & session factory
│   ├── models/
│   │   ├── user.py          # User SQLAlchemy model
│   │   └── task.py          # Task SQLAlchemy model
│   ├── schemas/
│   │   ├── user.py          # User Pydantic schemas
│   │   └── task.py          # Task Pydantic schemas
│   ├── services/
│   │   ├── auth.py          # Auth business logic
│   │   └── task.py          # Task business logic
│   └── main.py              # FastAPI app factory
├── alembic/
│   ├── env.py               # Alembic config for async
│   └── versions/            # Migration files
├── tests/
│   ├── conftest.py          # Fixtures (test DB, test client, test user)
│   ├── test_auth.py         # Auth endpoint tests
│   └── test_tasks.py        # Task endpoint tests
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## API Overview

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create a new account |
| POST | `/api/v1/auth/login` | Get access + refresh tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks` | List tasks (paginated, filterable) |
| POST | `/api/v1/tasks` | Create a new task |
| GET | `/api/v1/tasks/{id}` | Get a single task |
| PUT | `/api/v1/tasks/{id}` | Update a task |
| DELETE | `/api/v1/tasks/{id}` | Delete a task (owner or admin) |

### Query Parameters for GET /tasks

- `page` — Page number (default: 1)
- `size` — Items per page (default: 20, max: 100)
- `status` — Filter by status (todo, in_progress, done)
- `priority` — Filter by priority (low, medium, high)
- `search` — Search task titles

## License

MIT
