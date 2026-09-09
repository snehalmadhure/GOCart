"""Database configuration for the single-user GOCart application."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


default_database_url = "sqlite:////tmp/gocart.db" if os.getenv("VERCEL") else "sqlite:///./gocart.db"
DATABASE_URL = os.getenv("GOCART_DATABASE_URL", default_database_url)

# Supabase provides conventional ``postgresql://`` connection URIs. Use
# Psycopg 3 explicitly so Vercel installs its binary wheel instead of needing
# a compiler for psycopg2.
SQLALCHEMY_DATABASE_URL = (
    DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    if DATABASE_URL.startswith("postgresql://")
    else DATABASE_URL
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")
engine_options: dict[str, object] = {"pool_pre_ping": True}

if is_sqlite:
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    # A Vercel instance can serve concurrent requests, while each Supabase
    # pooler connection consumes a limited shared resource. Supabase's
    # transaction-mode PgBouncer cannot retain server-side prepared statements
    # across transactions, so disable Psycopg 3 auto-preparation.
    engine_options.update(
        connect_args={"prepare_threshold": None},
        pool_size=int(os.getenv("GOCART_DATABASE_POOL_SIZE", "1")),
        max_overflow=int(os.getenv("GOCART_DATABASE_MAX_OVERFLOW", "0")),
        pool_recycle=int(os.getenv("GOCART_DATABASE_POOL_RECYCLE", "300")),
    )

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yield a request-scoped database session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
