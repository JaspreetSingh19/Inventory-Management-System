"""
database.py
-----------
Database connectivity layer for the Inventory & Order Management System.

Responsibilities:
- Load the DATABASE_URL from environment variables.
- Create the SQLAlchemy engine and session factory.
- Expose the declarative ``Base`` class that all ORM models inherit from.
- Provide the ``get_db`` dependency used by FastAPI route handlers to obtain
  a scoped database session that is automatically closed after each request.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/inventory")
"""str: Full PostgreSQL connection string.  Read from the ``DATABASE_URL``
environment variable; falls back to a local development default."""

engine = create_engine(DATABASE_URL)
"""sqlalchemy.engine.Engine: Shared SQLAlchemy engine bound to the configured
database.  All sessions are created through this engine."""

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""sessionmaker: Factory that produces new ``Session`` objects.
``autocommit=False`` and ``autoflush=False`` give route handlers explicit
control over when changes are written to the database."""


class Base(DeclarativeBase):
    """Declarative base class inherited by every SQLAlchemy ORM model.

    All table mappings (Product, Customer, Order, OrderItem) extend this class
    so that ``Base.metadata.create_all()`` can discover and create their
    corresponding database tables automatically at application startup.
    """


def get_db():
    """FastAPI dependency that yields a database session per request.

    Opens a new ``SessionLocal`` session, yields it to the route handler, and
    guarantees the session is closed once the response has been sent — even if
    an unhandled exception occurs.

    Yields:
        sqlalchemy.orm.Session: An active database session scoped to the
        current HTTP request.

    Example::

        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
