"""
routers/customers.py
--------------------
FastAPI router for the ``/customers`` resource.

Endpoints
---------
POST   /customers          — Register a new customer.
GET    /customers          — List all customers (newest first).
GET    /customers/{id}     — Retrieve a single customer by primary key.
DELETE /customers/{id}     — Remove a customer record.

Business rules enforced here:
- Email address must be unique system-wide; a 409 Conflict is returned on
  duplicate.
- Email format validation is handled upstream in :mod:`app.schemas` via
  Pydantic's ``EmailStr`` type.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=schemas.CustomerOut, status_code=201)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)) -> models.Customer:
    """Register a new customer.

    Args:
        payload (schemas.CustomerCreate): Validated request body containing
            ``full_name``, ``email``, and ``phone``.
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        schemas.CustomerOut: The newly created customer record including its
        assigned ``id`` and ``created_at`` timestamp.

    Raises:
        HTTPException(409): If a customer with the same email already exists.
    """
    customer = models.Customer(**payload.model_dump())
    db.add(customer)
    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    return customer


@router.get("", response_model=list[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db)) -> list[models.Customer]:
    """Retrieve all customers, ordered by registration date descending.

    Args:
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        list[schemas.CustomerOut]: All registered customers, newest first.
    """
    return db.query(models.Customer).order_by(models.Customer.created_at.desc()).all()


@router.get("/{customer_id}", response_model=schemas.CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)) -> models.Customer:
    """Retrieve a single customer by their primary key.

    Args:
        customer_id (int): The primary key of the customer to retrieve.
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        schemas.CustomerOut: The matching customer record.

    Raises:
        HTTPException(404): If no customer with ``customer_id`` exists.
    """
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)) -> None:
    """Permanently delete a customer record.

    Args:
        customer_id (int): Primary key of the customer to remove.
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        None: HTTP 204 No Content on success.

    Raises:
        HTTPException(404): If no customer with ``customer_id`` exists.
    """
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
