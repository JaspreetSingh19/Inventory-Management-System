"""
schemas.py
----------
Pydantic v2 request/response schemas for the Inventory & Order Management API.

Each resource (Product, Customer, Order) has a family of schemas that serve
distinct lifecycle roles:

- ``*Base``   — shared fields and validators used by both input and output.
- ``*Create`` — request body for POST endpoints; inherits from Base.
- ``*Update`` — request body for PUT endpoints; all fields are optional.
- ``*Out``    — response model returned to API callers; includes DB-assigned
                fields (id, created_at) and ORM-mapped relationships.

Validators defined here run *before* data reaches the database, giving early,
readable error messages to the caller.
"""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


# ── Product ───────────────────────────────────────────────────────────────────

class ProductBase(BaseModel):
    """Shared product fields used by both create and update schemas.

    Attributes:
        name (str): Human-readable product name.
        sku (str): Unique stock-keeping unit code.
        price (Decimal): Selling price; must be >= 0.
        quantity (int): Units currently in stock; must be >= 0.
    """

    name: str
    sku: str
    price: Decimal
    quantity: int

    @field_validator("price")
    @classmethod
    def price_non_negative(cls, v: Decimal) -> Decimal:
        """Reject negative price values before they reach the database.

        Args:
            v (Decimal): The incoming price value.

        Returns:
            Decimal: The validated price unchanged.

        Raises:
            ValueError: If ``v`` is less than zero.
        """
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v: int) -> int:
        """Reject negative quantity values before they reach the database.

        Args:
            v (int): The incoming quantity value.

        Returns:
            int: The validated quantity unchanged.

        Raises:
            ValueError: If ``v`` is less than zero.
        """
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v


class ProductCreate(ProductBase):
    """Request body schema for ``POST /products``.

    Inherits all fields and validators from :class:`ProductBase`.
    No additional fields are required for creation.
    """


class ProductUpdate(BaseModel):
    """Request body schema for ``PUT /products/{id}``.

    All fields are optional so that callers can perform partial updates
    (PATCH-like semantics through a PUT endpoint).

    Attributes:
        name (str | None): New product name, or ``None`` to leave unchanged.
        sku (str | None): New SKU, or ``None`` to leave unchanged.
        price (Decimal | None): New price, or ``None`` to leave unchanged.
        quantity (int | None): New stock quantity, or ``None`` to leave unchanged.
    """

    name: str | None = None
    sku: str | None = None
    price: Decimal | None = None
    quantity: int | None = None

    @field_validator("price")
    @classmethod
    def price_non_negative(cls, v: Decimal | None) -> Decimal | None:
        """Reject negative price values when a price update is provided.

        Args:
            v (Decimal | None): The incoming price, or ``None`` if not updating.

        Returns:
            Decimal | None: The validated value unchanged.

        Raises:
            ValueError: If ``v`` is not ``None`` and is less than zero.
        """
        if v is not None and v < 0:
            raise ValueError("Price cannot be negative")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v: int | None) -> int | None:
        """Reject negative quantity values when a quantity update is provided.

        Args:
            v (int | None): The incoming quantity, or ``None`` if not updating.

        Returns:
            int | None: The validated value unchanged.

        Raises:
            ValueError: If ``v`` is not ``None`` and is less than zero.
        """
        if v is not None and v < 0:
            raise ValueError("Quantity cannot be negative")
        return v


class ProductOut(ProductBase):
    """Response schema returned by all product endpoints.

    Extends :class:`ProductBase` with database-assigned fields.
    ``from_attributes=True`` allows Pydantic to read values directly from
    SQLAlchemy ORM model instances.

    Attributes:
        id (int): Database-assigned primary key.
        created_at (datetime): UTC timestamp of record creation.
        updated_at (datetime): UTC timestamp of the last modification;
            equals ``created_at`` until the first PUT request.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


# ── Customer ──────────────────────────────────────────────────────────────────

class CustomerBase(BaseModel):
    """Shared customer fields used by both create and output schemas.

    Attributes:
        full_name (str): Customer's full name.
        email (EmailStr): Validated email address; must be unique system-wide.
        phone (str): Contact phone number.
    """

    full_name: str
    email: EmailStr
    phone: str


class CustomerCreate(CustomerBase):
    """Request body schema for ``POST /customers``.

    Inherits all fields and validators from :class:`CustomerBase`.
    No additional fields are required for creation.
    """


class CustomerOut(CustomerBase):
    """Response schema returned by all customer endpoints.

    Extends :class:`CustomerBase` with database-assigned fields.

    Attributes:
        id (int): Database-assigned primary key.
        created_at (datetime): UTC timestamp of record creation.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ── Order ─────────────────────────────────────────────────────────────────────

class OrderItemIn(BaseModel):
    """A single line-item within an order creation request.

    Attributes:
        product_id (int): ID of the product being ordered.
        quantity (int): Number of units to order; must be > 0.
    """

    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        """Ensure at least one unit is requested per line item.

        Args:
            v (int): The requested quantity.

        Returns:
            int: The validated quantity unchanged.

        Raises:
            ValueError: If ``v`` is zero or negative.
        """
        if v <= 0:
            raise ValueError("Order item quantity must be positive")
        return v


class OrderItemOut(BaseModel):
    """Response schema for a single order line item.

    Includes the nested product details so callers receive a fully populated
    response without a second request.

    Attributes:
        id (int): Line-item primary key.
        product_id (int): Foreign key to the product.
        quantity (int): Units ordered.
        unit_price (Decimal): Price per unit captured at order creation time.
        product (ProductOut): Full product details at the time of serialisation.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    product: ProductOut


class OrderCreate(BaseModel):
    """Request body schema for ``POST /orders``.

    Attributes:
        customer_id (int): ID of the customer placing the order.
        items (list[OrderItemIn]): One or more line items; must not be empty.
    """

    customer_id: int
    items: list[OrderItemIn]

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: list[OrderItemIn]) -> list[OrderItemIn]:
        """Ensure the order contains at least one line item.

        Args:
            v (list[OrderItemIn]): The list of requested items.

        Returns:
            list[OrderItemIn]: The validated list unchanged.

        Raises:
            ValueError: If the list is empty.
        """
        if not v:
            raise ValueError("Order must have at least one item")
        return v


class OrderOut(BaseModel):
    """Response schema returned by all order endpoints.

    Includes nested customer and line-item details for a self-contained
    representation of the order.

    Attributes:
        id (int): Database-assigned order primary key.
        customer_id (int): Foreign key to the customer.
        total_amount (Decimal): Backend-calculated sum of all line items.
        created_at (datetime): UTC timestamp of order creation.
        customer (CustomerOut): Full customer details.
        items (list[OrderItemOut]): All line items with product details.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    total_amount: Decimal
    created_at: datetime
    customer: CustomerOut
    items: list[OrderItemOut]


# ── Dashboard ─────────────────────────────────────────────────────────────────

class LowStockProduct(BaseModel):
    """A compact product representation used in the low-stock dashboard list.

    Only the fields relevant to stock monitoring are included to keep the
    dashboard response payload small.

    Attributes:
        id (int): Product primary key.
        name (str): Product name.
        sku (str): Product SKU code.
        quantity (int): Current units in stock (will be < LOW_STOCK_THRESHOLD).
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    sku: str
    quantity: int


class DashboardSummary(BaseModel):
    """Response schema for ``GET /dashboard/summary``.

    Provides a high-level snapshot of system activity for the dashboard UI.

    Attributes:
        total_products (int): Count of all products in the catalogue.
        total_customers (int): Count of all registered customers.
        total_orders (int): Count of all orders ever placed.
        low_stock_products (list[LowStockProduct]): Products whose current
            stock quantity is below the configured low-stock threshold,
            sorted by quantity ascending.
    """

    total_products: int
    total_customers: int
    total_orders: int
    low_stock_products: list[LowStockProduct]
