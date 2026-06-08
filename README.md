# Help Desk Ticketing System

A full-stack help desk / ticketing system built with **FastAPI** (backend) and **CustomTkinter** (desktop frontend).

## Features

- **User roles**: User and Admin with role-based access control
- **Ticket management**: Create, view, update, delete tickets
- **Status workflow**: Open → In Progress → Resolved → Closed
- **Priority levels**: Low, Medium, High, Critical
- **Category system**: Organize tickets by category
- **Comments**: Add comments to tickets for discussion
- **Filtering & search**: Filter tickets by status, priority, category; search by title/description
- **Admin panel**: User management and category management
- **JWT authentication**: Secure token-based auth

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Database | SQLite |
| ORM | SQLModel |
| Validation | Pydantic |
| Desktop UI | CustomTkinter |
| Auth | JWT (python-jose + bcrypt) |
| Tests | pytest |
| Lint | ruff + black |
| CI | GitHub Actions |
| Container | Docker |

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### 1. Clone the repository

```bash
git clone <repository-url>
cd helpdesk-ticketing-system
```

### 2. Set up virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 4. Start the backend API

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### 5. Seed demo data (optional)

```bash
cd backend
python -m app.seed
```

Demo credentials:
- **Admin**: `admin` / `admin123`
- **User 1**: `user1` / `user123`
- **User 2**: `user2` / `user123`

### 6. Start the frontend

```bash
cd frontend
python app.py
```

## Running with Docker

```bash
# Build and start the backend
docker-compose up --build

# Seed demo data (in another terminal)
docker-compose exec api python -m app.seed
```

The API will be available at `http://localhost:8000`.

Then start the frontend locally:
```bash
cd frontend
python app.py
```
### Mail Testing with Mailpit

When the project is run with Docker, ticket creation notification emails are tested using Mailpit.

After starting Docker Compose, outgoing test emails can be viewed in the browser at:

http://localhost:8025

This allows the project to test email sending locally without depending on an external provider such as Gmail.

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Linting

```bash
ruff check backend/
black --check backend/
```

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/auth/me` | Current user info |

### Tickets
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tickets/` | List tickets (filterable) |
| POST | `/api/tickets/` | Create ticket |
| GET | `/api/tickets/{id}` | Get ticket |
| PUT | `/api/tickets/{id}` | Update ticket |
| DELETE | `/api/tickets/{id}` | Delete ticket (admin) |
| PATCH | `/api/tickets/{id}/assign` | Assign ticket (admin) |
| PATCH | `/api/tickets/{id}/status` | Change status (admin) |
| PATCH | `/api/tickets/{id}/priority` | Change priority (admin) |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tickets/{id}/comments` | List comments |
| POST | `/api/tickets/{id}/comments` | Add comment |
| DELETE | `/api/comments/{id}` | Delete comment |

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | List categories |
| POST | `/api/categories/` | Create (admin) |
| PUT | `/api/categories/{id}` | Update (admin) |
| DELETE | `/api/categories/{id}` | Delete (admin) |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List users (admin) |
| PATCH | `/api/users/{id}/role` | Change role (admin) |
| PATCH | `/api/users/{id}/active` | Toggle active (admin) |

## Demo Scenario

1. Start the backend and seed demo data
2. Open the frontend and log in as `admin` / `admin123`
3. View the dashboard with pre-created tickets
4. Click a ticket to see details and comments
5. Use admin controls to assign, change status/priority
6. Add a comment to the ticket
7. Go to Admin Panel to manage users and categories
8. Log out and log in as `user1` / `user123`
9. Create a new ticket
10. View only your own tickets

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── database.py       # DB engine & session
│   │   ├── models.py         # SQLModel tables
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── auth.py           # JWT auth
│   │   ├── seed.py           # Demo data
│   │   └── routers/          # API route handlers
│   └── tests/                # pytest test suite
├── frontend/
│   ├── app.py                # CustomTkinter entry point
│   ├── api_client.py         # HTTP client
│   ├── config.py             # Settings & colors
│   ├── views/                # UI screens
│   └── widgets/              # Reusable UI components
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
└── pyproject.toml
```

## License

This project is for educational purposes as part of a software engineering course.
