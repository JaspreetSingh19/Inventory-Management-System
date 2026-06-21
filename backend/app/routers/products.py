"""
routers/products.py
-------------------
FastAPI router for the ``/products`` resource.

Endpoints
---------
POST   /products          — Create a new product.
GET    /products          — List all products (newest first).
GET    /products/{id}     — Retrieve a single product by primary key.
PUT    /products/{id}     — Partially or fully update an existing product.
DELETE /products/{id}     — Permanently remove a product.

Business rules enforced here:
- SKU must be unique; a 409 Conflict is returned on duplicate.
- Price and quantity validations are handled upstream in :mod:`app.schemas`.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=schemas.ProductOut, status_code=201)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)) -> models.Product:
    """Create a new product in the inventory catalogue.

    Args:
        payload (schemas.ProductCreate): Validated request body containing
            ``name``, ``sku``, ``price``, and ``quantity``.
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        schemas.ProductOut: The newly created product including its assigned
        ``id`` and ``created_at`` timestamp.

    Raises:
        HTTPException(409): If a product with the same SKU already exists.
    """
    product = models.Product(**payload.model_dump())
    db.add(product)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="SKU already exists")
    return product


@router.get("", response_model=list[schemas.ProductOut])
def list_products(db: Session = Depends(get_db)) -> list[models.Product]:
    """Retrieve all products, ordered by creation date descending.

    Args:
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        list[schemas.ProductOut]: All products in the catalogue, newest first.
    """
    return db.query(models.Product).order_by(models.Product.created_at.desc()).all()


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)) -> models.Product:
    """Retrieve a single product by its primary key.

    Args:
        product_id (int): The primary key of the product to retrieve.
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        schemas.ProductOut: The matching product record.

    Raises:
        HTTPException(404): If no product with ``product_id`` exists.
    """
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    payload: schemas.ProductUpdate,
    db: Session = Depends(get_db),
) -> models.Product:
    """Update one or more fields of an existing product.

    Only fields explicitly provided in the request body are modified; omitted
    fields retain their current values (partial-update semantics).

    Args:
        product_id (int): Primary key of the product to update.
        payload (schemas.ProductUpdate): Fields to change.  Any field set to
            ``None`` (or omitted) is left unchanged.
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        schemas.ProductOut: The updated product record.

    Raises:
        HTTPException(404): If no product with ``product_id`` exists.
        HTTPException(409): If the new SKU conflicts with another product.
    """
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="SKU already exists")
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> None:
    """Permanently delete a product from the catalogue.

    Args:
        product_id (int): Primary key of the product to delete.
        db (Session): Database session injected by :func:`app.database.get_db`.

    Returns:
        None: HTTP 204 No Content on success.

    Raises:
        HTTPException(404): If no product with ``product_id`` exists.
    """
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
