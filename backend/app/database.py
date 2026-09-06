"""Database configuration for the single-user GOCart application."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


default_database_url = "sqlite:////tmp/gocart.db" if os.getenv("VERCEL") else "sqlite:///./gocart.db"
DATABASE_URL = os.getenv("GOCART_DATABASE_URL", default_database_url)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


sqlite_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=sqlite_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yield a request-scoped database session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
