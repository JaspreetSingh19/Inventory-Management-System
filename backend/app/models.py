"""
models.py
---------
SQLAlchemy ORM models for the Inventory & Order Management System.

Each class maps directly to a PostgreSQL table and defines:
- Column declarations with types, constraints, and defaults.
- Relationships to other models for eager/lazy loading.
- Database-level CHECK constraints for critical business invariants.

Tables
------
- products      — catalogue of items that can be sold.
- customers     — registered buyers.
- orders        — a purchase event tied to one customer.
- order_items   — individual line items within an order (join table).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint, event
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    """ORM model representing a product in the inventory catalogue.

    Attributes:
        id (int): Auto-incremented primary key.
        name (str): Human-readable product name (max 255 chars).
        sku (str): Stock Keeping Unit — must be unique across all products.
        price (Decimal): Unit selling price with up to 10 digits and 2
            decimal places.  Must be >= 0 (enforced by DB constraint).
        quantity (int): Current units available in stock.  Must be >= 0
            (enforced by DB constraint).  Decremented on order creation and
            restored on order cancellation.
        created_at (datetime): UTC timestamp set automatically on insert.
        updated_at (datetime): UTC timestamp updated automatically on every
            PUT request via the ``before_update`` SQLAlchemy event listener.
        order_items (list[OrderItem]): Back-reference to all ``OrderItem``
            rows that reference this product.

    Table:
        products

    Constraints:
        ck_product_quantity_non_negative — quantity >= 0
        ck_product_price_non_negative    — price >= 0
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_product_quantity_non_negative"),
        CheckConstraint("price >= 0", name="ck_product_price_non_negative"),
    )

    order_items = relationship("OrderItem", back_populates="product")


@event.listens_for(Product, "before_update")
def _set_product_updated_at(mapper, connection, target):
    """SQLAlchemy event hook that refreshes ``updated_at`` before every UPDATE.

    Fires automatically whenever a ``Product`` row is flushed with changes,
    ensuring ``updated_at`` always reflects the last modification time without
    requiring the caller to set it manually.

    Args:
        mapper: The ORM mapper for the ``Product`` class (unused).
        connection: The raw DBAPI connection being used (unused).
        target (Product): The product instance about to be updated.
    """
    target.updated_at = datetime.utcnow()


class Customer(Base):
    """ORM model representing a registered customer.

    Attributes:
        id (int): Auto-incremented primary key.
        full_name (str): Customer's full name (max 255 chars).
        email (str): Unique email address used to identify the customer.
        phone (str): Contact phone number (max 50 chars).
        created_at (datetime): UTC timestamp set automatically on insert.
        orders (list[Order]): All orders placed by this customer.

    Table:
        customers

    Constraints:
        Unique index on ``email`` — enforced at the DB level.
    """

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    """ORM model representing a customer purchase order.

    An order groups one or more ``OrderItem`` rows under a single transaction.
    The ``total_amount`` is always calculated by the backend at creation time
    and never accepted from the client.

    Attributes:
        id (int): Auto-incremented primary key.
        customer_id (int): Foreign key referencing ``customers.id``.
        total_amount (Decimal): Sum of (unit_price × quantity) for all line
            items, rounded to 2 decimal places.
        created_at (datetime): UTC timestamp set automatically on insert.
        customer (Customer): The customer who placed this order.
        items (list[OrderItem]): Line items belonging to this order.
            Cascades delete so that cancelling an order removes its items.

    Table:
        orders
    """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """ORM model representing a single line item within an order.

    Captures the product reference, quantity ordered, and the unit price
    *at the time of the order* so that subsequent product price changes do
    not alter historical order totals.

    Attributes:
        id (int): Auto-incremented primary key.
        order_id (int): Foreign key referencing ``orders.id``.
        product_id (int): Foreign key referencing ``products.id``.
        quantity (int): Number of units ordered for this line item.
        unit_price (Decimal): Price per unit snapshotted from
            ``Product.price`` at order creation time.
        order (Order): The parent order that owns this item.
        product (Product): The product being ordered.

    Table:
        order_items
    """

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
