"""
routers/orders.py
-----------------
FastAPI router for the ``/orders`` resource.

Endpoints
---------
POST   /orders          — Place a new order.
GET    /orders          — List all orders with customer and item details.
GET    /orders/{id}     — Retrieve a single order by primary key.
DELETE /orders/{id}     — Cancel an order and restore inventory stock.

Business rules enforced here:
- The referenced customer must exist.
- Every referenced product must exist.
- Each product must have sufficient stock to satisfy the requested quantity;
  a 422 Unprocessable Entity is returned otherwise.
- ``total_amount`` is calculated server-side; it is never accepted from the
  client.
- Stock is decremented atomically within the same transaction as order creation.
- Cancelling an order (DELETE) restores the reserved stock for each line item.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/orders", tags=["orders"])


def _load_order(db: Session, order_id: int) -> models.Order:
    """Fetch an order by ID with all related data eagerly loaded.

    Uses ``joinedload`` to retrieve the customer and all order items (with
    their associated products) in a minimal number of SQL queries, avoiding
    the N+1 query problem.

    Args:
        db (Session): Active database session.
        order_id (int): Primary key of the order to load.

    Returns:
        models.Order: The fully populated order ORM instance.

    Raises:
        HTTPException(404): If no order with ``order_id`` exists.
    """
    order = (
        db.query(models.Order)
        .options(
            joinedload(models.Order.customer),
            joinedload(models.Order.items).joinedload(models.OrderItem.product),
        )
        .filter(models.Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=schemas.OrderOut, status_code=201)
def create_order(payload: schemas.OrderCreate, db: Session = Depends(get_db)) -> models.Order:
    """Place a new order and decrement product stock.

    Processing steps (all within a single transaction):
    1. Validate that the customer exists.
    2. For each line item: validate the product exists and has sufficient stock.
    3. Calculate ``total_amount`` as the sum of ``unit_price × quantity``.
    4. Persist the ``Order`` and flush to obtain its primary key.
    5. Persist each ``OrderItem``, snapshotting the current product price.
    6. Decrement ``product.quantity`` by the ordered amount.
    7. Commit the transaction and return the fully loaded order.

    Args:
        payload (schemas.OrderCreate): Validated request body containing
            ``customer_id`` and a non-empty list of ``items``.
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        schemas.OrderOut: The created order with nested customer and item details.

    Raises:
        HTTPException(404): If the customer or any referenced product does not exist.
        HTTPException(422): If any product has insufficient stock to fulfil the
            requested quantity.
    """
    customer = db.get(models.Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    total = 0
    items_to_create = []

    for item_in in payload.items:
        product = db.get(models.Product, item_in.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_in.product_id} not found")
        if product.quantity < item_in.quantity:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Insufficient stock for '{product.name}': "
                    f"available {product.quantity}, requested {item_in.quantity}"
                ),
            )
        total += float(product.price) * item_in.quantity
        items_to_create.append((product, item_in.quantity, float(product.price)))

    order = models.Order(customer_id=payload.customer_id, total_amount=round(total, 2))
    db.add(order)
    db.flush()  # Obtain order.id without committing yet.

    for product, qty, unit_price in items_to_create:
        db.add(
            models.OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                unit_price=unit_price,
            )
        )
        product.quantity -= qty  # Atomic stock decrement within the same transaction.

    db.commit()
    return _load_order(db, order.id)


@router.get("", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db)) -> list[models.Order]:
    """Retrieve all orders with customer and line-item details, newest first.

    Uses eager loading (``joinedload``) to avoid N+1 queries when serialising
    nested relationships.

    Args:
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        list[schemas.OrderOut]: All orders, each with embedded customer and
        item information.
    """
    return (
        db.query(models.Order)
        .options(
            joinedload(models.Order.customer),
            joinedload(models.Order.items).joinedload(models.OrderItem.product),
        )
        .order_by(models.Order.created_at.desc())
        .all()
    )


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)) -> models.Order:
    """Retrieve a single order by its primary key.

    Args:
        order_id (int): The primary key of the order to retrieve.
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        schemas.OrderOut: The matching order with nested customer and item details.

    Raises:
        HTTPException(404): If no order with ``order_id`` exists.
    """
    return _load_order(db, order_id)


@router.delete("/{order_id}", status_code=204)
def cancel_order(order_id: int, db: Session = Depends(get_db)) -> None:
    """Cancel an order and restore the reserved inventory stock.

    For each line item in the order, the ordered quantity is added back to
    the corresponding product's ``quantity`` field before the order is deleted.
    Both the stock restoration and the deletion occur in a single transaction.

    Args:
        order_id (int): Primary key of the order to cancel.
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        None: HTTP 204 No Content on success.

    Raises:
        HTTPException(404): If no order with ``order_id`` exists.
    """
    order = _load_order(db, order_id)
    for item in order.items:
        item.product.quantity += item.quantity  # Restore stock for each line item.
    db.delete(order)
    db.commit()
