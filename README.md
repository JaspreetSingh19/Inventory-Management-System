# Inventory & Order Management System

A full-stack application for managing products, customers, and orders with real-time inventory tracking.

**Stack:** FastAPI · PostgreSQL · SQLAlchemy · Alembic · React 19 · Vite · Tailwind CSS · Docker

---

## Live Demo

| Service | URL |
|---------|-----|
| Frontend | https://inventory-management-system-pi-olive.vercel.app |
| Backend API | https://inventory-management-system-production-4409.up.railway.app |
| API Docs (Swagger) | https://inventory-management-system-production-4409.up.railway.app/docs |

---

## Docker Hub

```bash
docker pull jaspreetsingh19/inventory-backend:latest
```

Image: [hub.docker.com/r/jaspreetsingh19/inventory-backend](https://hub.docker.com/r/jaspreetsingh19/inventory-backend)

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, routes
│   │   ├── database.py      # SQLAlchemy engine & session
│   │   ├── models.py        # ORM models (Product, Customer, Order, OrderItem)
│   │   ├── schemas.py       # Pydantic v2 request/response schemas
│   │   └── routers/         # products, customers, orders, dashboard
│   ├── tests/               # pytest suite (76 tests, ~99% coverage)
│   ├── alembic/             # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/           # Dashboard, Products, Customers, Orders
│   │   ├── components/      # Navbar, Modal, ConfirmDialog
│   │   └── api/             # Axios API clients
│   └── Dockerfile
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

- Python 3.12+
- Node.js 20+
- PostgreSQL running locally

---

### Backend

```bash
cd backend

# Create and activate a virtual environment
python3.12 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Upgrade pip first (required for pre-built wheels)
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Copy and configure the .env file
cp ../.env.example ../.env
# Edit DATABASE_URL to match your local PostgreSQL credentials

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API: **http://localhost:8000** · Docs: **http://localhost:8000/docs**

---

### Frontend

```bash
cd frontend

npm install

# Start the dev server (set backend URL in .env or export below)
export VITE_API_URL=http://localhost:8000
npm run dev
```

App: **http://localhost:5173**

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest --cov=app --cov-report=term-missing
```

76 tests · ~99% coverage · PostgreSQL-backed (no mocks)

---

## Environment Variables

Copy `.env.example` to `.env`:

| Variable            | Description                      | Default                  |
|---------------------|----------------------------------|--------------------------|
| `DATABASE_URL`      | Full PostgreSQL connection string | postgresql://...         |
| `POSTGRES_USER`     | PostgreSQL username               | `inventory_user`         |
| `POSTGRES_PASSWORD` | PostgreSQL password               | `changeme`               |
| `POSTGRES_DB`       | Database name                     | `inventory`              |
| `VITE_API_URL`      | Backend URL used by the frontend  | `http://localhost:8000`  |

---

## API Endpoints

| Method | Endpoint             | Description            |
|--------|----------------------|------------------------|
| GET    | `/health`            | Health check           |
| POST   | `/products`          | Create product         |
| GET    | `/products`          | List all products      |
| GET    | `/products/{id}`     | Get product by ID      |
| PUT    | `/products/{id}`     | Update product         |
| DELETE | `/products/{id}`     | Delete product         |
| POST   | `/customers`         | Create customer        |
| GET    | `/customers`         | List all customers     |
| GET    | `/customers/{id}`    | Get customer by ID     |
| DELETE | `/customers/{id}`    | Delete customer        |
| POST   | `/orders`            | Place an order         |
| GET    | `/orders`            | List all orders        |
| GET    | `/orders/{id}`       | Get order by ID        |
| DELETE | `/orders/{id}`       | Cancel order           |
| GET    | `/dashboard/summary` | Dashboard stats        |

---

## Alembic Cheatsheet

```bash
alembic upgrade head                       # apply all pending migrations
alembic revision --autogenerate -m "msg"  # generate migration from model changes
alembic downgrade -1                       # roll back one migration
alembic current                            # show current revision
```
