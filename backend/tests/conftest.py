"""
tests/conftest.py
-----------------
Shared pytest fixtures for the backend test suite.

Strategy
--------
- Uses a dedicated **PostgreSQL** test database (``inventory_test``) — same
  engine as production, so CHECK constraints, server defaults, and Numeric
  precision are all exercised exactly as they are in production.
- Tables are created once per session and truncated (with RESTART IDENTITY)
  after every test, giving each test a clean slate without reconnecting.
- The ``TRUNCATE … CASCADE`` approach is used instead of savepoints because
  PostgreSQL aborts the entire transaction on an error (e.g. IntegrityError),
  which destroys any open savepoint before teardown can roll back to it.
- The FastAPI ``get_db`` dependency is overridden once (session-scope) so all
  route handlers share the same engine throughout the test run.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.main import app
from app.database import Base, get_db

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv("DATABASE_URL", "").replace("/inventory", "/inventory_test"),
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tables that need to be wiped between tests, in dependency order.
_TABLES = ["order_items", "orders", "customers", "products"]


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all ORM tables once for the entire test session, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db():
    """Truncate all tables and reset sequences after every test.

    ``RESTART IDENTITY`` resets serial primary key sequences so IDs start from
    1 in every test, making assertions on IDs predictable.
    ``CASCADE`` handles foreign-key order automatically.
    """
    yield
    with engine.connect() as conn:
        tables = ", ".join(_TABLES)
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
        conn.commit()


@pytest.fixture()
def db():
    """Yield a database session for a single test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    """Return a FastAPI TestClient wired to the test database session."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Reusable payloads ─────────────────────────────────────────────────────────

@pytest.fixture()
def product_payload():
    """Valid product creation payload."""
    return {"name": "Widget A", "sku": "WGT-001", "price": 9.99, "quantity": 100}


@pytest.fixture()
def customer_payload():
    """Valid customer creation payload."""
    return {"full_name": "Jane Doe", "email": "jane@example.com", "phone": "555-1234"}


@pytest.fixture()
def created_product(client, product_payload):
    """A product that has already been created via the API."""
    resp = client.post("/products", json=product_payload)
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture()
def created_customer(client, customer_payload):
    """A customer that has already been created via the API."""
    resp = client.post("/customers", json=customer_payload)
    assert resp.status_code == 201
    return resp.json()
