"""
main.py
-------
Application entry point for the Inventory & Order Management API.

Responsibilities:
- Instantiate the FastAPI application with metadata (title, version).
- Run ``Base.metadata.create_all`` at startup to create any missing database
  tables automatically (development convenience; use Alembic for production
  migrations).
- Register the CORS middleware so the React frontend (served on a different
  origin) can communicate with this API.
- Mount all domain routers under their respective URL prefixes.
- Expose a ``/health`` endpoint for container health checks and uptime monitors.

Usage::

    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import products, customers, orders, dashboard

# Create all tables that do not yet exist in the database.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventory & Order Management API",
    version="1.0.0",
    description=(
        "REST API for managing products, customers, orders, and inventory "
        "for the Inventory & Order Management System."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    """Health-check endpoint.

    Used by Docker Compose ``healthcheck``, load balancers, and uptime
    monitors to verify the API process is running and accepting requests.

    Returns:
        dict: ``{"status": "ok"}`` when the service is healthy.
    """
    return {"status": "ok"}
