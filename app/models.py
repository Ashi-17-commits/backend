"""
SQLAlchemy ORM models.

Defines the Ticket table that stores escalated support requests
received from the n8n workflow when AI confidence is insufficient.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Ticket(Base):
    """
    Support ticket created when the n8n workflow escalates a query
    to human support (confidence below threshold).
    """

    __tablename__ = "tickets"

    # Primary key – auto-incrementing integer
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Customer information
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_query: Mapped[str] = mapped_column(String(2000), nullable=False)

    # Classification fields from the n8n AI pipeline
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(50), nullable=False)

    # Ticket lifecycle – defaults to "Open" on creation
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Open")

    # Automatically set to current UTC timestamp on insert
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Ticket id={self.id} customer={self.customer_name!r} "
            f"status={self.status!r} priority={self.priority!r}>"
        )
