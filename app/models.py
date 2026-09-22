"""
SQLAlchemy ORM models.

Defines support tickets and failed requests that need manual review.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Ticket(Base):
    """
    Support ticket created when the n8n workflow escalates a query
    to human support.
    """

    __tablename__ = "tickets"

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Prevent duplicate ticket creation
    idempotency_key: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    # Customer information
    customer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    customer_query: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    # AI classification
    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    sentiment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Ticket lifecycle
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Open",
    )

    # Creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Ticket id={self.id} "
            f"customer={self.customer_name!r} "
            f"status={self.status!r} "
            f"priority={self.priority!r}>"
        )


class FailedRequest(Base):
    """
    Stores requests that could not be processed successfully
    and require manual review.
    """

    __tablename__ = "failed_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Telegram/user identifier
    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Original request payload stored as JSON string
    payload: Mapped[str] = mapped_column(
        String(5000),
        nullable=False,
    )

    # Error message
    error: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    # Review lifecycle
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="needs_review",
    )

    # Creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<FailedRequest id={self.id} "
            f"user_id={self.user_id!r} "
            f"status={self.status!r}>"
        )