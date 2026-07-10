"""
Database engine and session management.

Uses SQLAlchemy ORM with SQLite.  The engine is created once at
import time; sessions are yielded per-request via FastAPI dependency
injection (see get_db below).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL

# check_same_thread=False is required for SQLite when used with FastAPI's
# multi-threaded request handling.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


def get_db():
    """
    FastAPI dependency that yields a database session and ensures
    it is closed after the request completes, even on error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables defined in models.py if they do not exist."""
    # Import here to avoid circular imports at module load time.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
