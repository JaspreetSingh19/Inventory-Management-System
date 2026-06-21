"""
routers/dashboard.py
--------------------
FastAPI router for the ``/dashboard`` resource.

Endpoints
---------
GET /dashboard/summary — Return aggregate counts and low-stock alerts.

This router is intentionally read-only; it queries existing data without
mutating any state.  All aggregation is performed in a single database round-
trip per request.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

LOW_STOCK_THRESHOLD = 10
"""int: Products with a ``quantity`` strictly below this value are considered
low-stock and included in the dashboard summary alert list."""


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(db: Session = Depends(get_db)) -> schemas.DashboardSummary:
    """Return a high-level summary of system activity for the dashboard UI.

    Executes four lightweight queries against the database:
    1. ``COUNT`` of all products.
    2. ``COUNT`` of all customers.
    3. ``COUNT`` of all orders.
    4. Products whose ``quantity < LOW_STOCK_THRESHOLD``, sorted ascending.

    Args:
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        schemas.DashboardSummary: Aggregate statistics and a list of products
        that are running low on stock (sorted by quantity, lowest first).
    """
    total_products = db.query(models.Product).count()
    total_customers = db.query(models.Customer).count()
    total_orders = db.query(models.Order).count()
    low_stock = (
        db.query(models.Product)
        .filter(models.Product.quantity < LOW_STOCK_THRESHOLD)
        .order_by(models.Product.quantity)
        .all()
    )
    return schemas.DashboardSummary(
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        low_stock_products=low_stock,
    )
