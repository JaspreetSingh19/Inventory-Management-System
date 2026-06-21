"""
app
---
Root package for the Inventory & Order Management API.

Sub-modules
-----------
database    — SQLAlchemy engine, session factory, and declarative base.
models      — ORM table mappings (Product, Customer, Order, OrderItem).
schemas     — Pydantic request/response schemas and validators.
routers     — FastAPI route handlers grouped by resource domain.
main        — Application factory: middleware, router registration, startup.
"""
