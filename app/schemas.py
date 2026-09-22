"""
Pydantic schemas for request validation and response serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Ticket schemas
# ---------------------------------------------------------------------------

class TicketCreate(BaseModel):
    """Payload sent by n8n when escalating a query to human support."""

    customer_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["John Doe"],
    )

    customer_query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=["How do I reset my password?"],
    )

    priority: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["High"],
    )

    confidence: float = Field(
        ...,
        ge=0,
        le=100,
        examples=[42.5],
    )

    sentiment: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["Negative"],
    )

    # Telegram identifiers used for idempotency
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["123456789"],
    )

    message_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["987"],
    )


class TicketUpdate(BaseModel):
    """Partial update – only status and priority are mutable."""

    status: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        examples=["Resolved"],
    )

    priority: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        examples=["Low"],
    )

    model_config = ConfigDict(extra="forbid")


class TicketResponse(BaseModel):
    """Full ticket representation."""

    id: int
    customer_name: str
    customer_query: str
    priority: str
    confidence: float
    sentiment: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketCreateResponse(BaseModel):
    """Response returned after creating or reusing a ticket."""

    success: bool = True
    ticket_id: int
    message: str = "Ticket created successfully"


# ---------------------------------------------------------------------------
# Failed request schemas
# ---------------------------------------------------------------------------

class FailedRequestCreate(BaseModel):
    """Payload used to store a failed request for later review."""

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    payload: dict

    error: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class FailedRequestResponse(BaseModel):
    """Response returned after storing a failed request."""

    success: bool = True
    failed_request_id: int
    status: str


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class DashboardStats(BaseModel):
    """Aggregated metrics for the support dashboard."""

    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    high_priority: int
    average_confidence: float


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standard error envelope."""

    detail: str