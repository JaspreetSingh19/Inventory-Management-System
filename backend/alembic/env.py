"""
alembic/env.py
--------------
Alembic migration environment configuration.

Wires up:
- DATABASE_URL from the project .env file (via python-dotenv).
- SQLAlchemy metadata from all ORM models so autogenerate can detect
  schema differences automatically.
"""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Load .env so DATABASE_URL is available without being hardcoded here.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
# Also try the backend-level .env if present.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.models import Base  # noqa: E402 — import after load_dotenv

config = context.config

# Override sqlalchemy.url from environment so alembic.ini never contains
# credentials.
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# All ORM models are registered on Base.metadata via their class definitions.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection required).

    Emits raw SQL to stdout so it can be reviewed or applied manually.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to the live database)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
