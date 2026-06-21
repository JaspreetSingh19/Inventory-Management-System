# Inventory & Order Management System

A full-stack application for managing products, customers, and orders with real-time inventory tracking.

**Stack:** FastAPI · PostgreSQL · React · Docker

---

## Project Structure

```
├── backend/       # FastAPI Python API
├── frontend/      # React (Vite) UI
├── docker-compose.yml
└── .env.example
```

---

## Running with Docker (recommended)

Runs all three services (frontend, backend, database) with one command.

**Prerequisites:** Docker + Docker Compose installed.

```bash
# 1. Copy and configure environment variables
cp .env.example .env

# 2. Build and start all services
docker compose up --build
```

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:80           |
| Backend  | http://localhost:8000         |
| API Docs | http://localhost:8000/docs    |

To stop:
```bash
docker compose down
```

---

## Running Locally (without Docker)

### Prerequisites

- Python 3.12+ (via pyenv or system install)
- Node.js 20+
- PostgreSQL running locally

> **pip build errors?** Run `pip install --upgrade pip` inside your venv before
> installing requirements. pip 23.x cannot find pre-built wheels for
> `psycopg2-binary` and `pydantic-core`; pip 24+ resolves this automatically.

---

### Backend

```bash
cd backend

# Create a venv using Python 3.12 (adjust path if not using pyenv)
~/.pyenv/versions/3.12.0/bin/python3.12 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Upgrade pip first (required — older pip fails to find pre-built wheels)
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Copy and configure the .env file
cp ../.env.example ../.env
# Edit DATABASE_URL in .env to match your local PostgreSQL credentials

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API available at **http://localhost:8000** · Docs at **http://localhost:8000/docs**

**Alembic cheatsheet:**
```bash
alembic upgrade head                        # apply all pending migrations
alembic revision --autogenerate -m "msg"   # generate migration from model changes
alembic downgrade -1                        # roll back one migration
alembic current                             # show current DB revision
```

---

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set the backend URL (or create a .env file with this line)
export VITE_API_URL=http://localhost:8000

# Start the dev server
npm run dev
```

App available at **http://localhost:5173**

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

| Variable          | Description                        | Default                  |
|-------------------|------------------------------------|--------------------------|
| `POSTGRES_USER`   | PostgreSQL username                | `inventory_user`         |
| `POSTGRES_PASSWORD` | PostgreSQL password              | `changeme`               |
| `POSTGRES_DB`     | Database name                      | `inventory`              |
| `VITE_API_URL`    | Backend URL used by the frontend   | `http://localhost:8000`  |

---

## API Endpoints

| Method | Endpoint               | Description              |
|--------|------------------------|--------------------------|
| POST   | `/products`            | Create product           |
| GET    | `/products`            | List all products        |
| GET    | `/products/{id}`       | Get product by ID        |
| PUT    | `/products/{id}`       | Update product           |
| DELETE | `/products/{id}`       | Delete product           |
| POST   | `/customers`           | Create customer          |
| GET    | `/customers`           | List all customers       |
| GET    | `/customers/{id}`      | Get customer by ID       |
| DELETE | `/customers/{id}`      | Delete customer          |
| POST   | `/orders`              | Place an order           |
| GET    | `/orders`              | List all orders          |
| GET    | `/orders/{id}`         | Get order by ID          |
| DELETE | `/orders/{id}`         | Cancel order             |
| GET    | `/dashboard/summary`   | Dashboard stats          |
