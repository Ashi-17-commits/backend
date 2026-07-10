"""
Pydantic schemas for request validation and response serialization.

Separates the API contract from the ORM layer so that internal
database changes do not leak into the public API surface.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Ticket schemas
# ---------------------------------------------------------------------------

class TicketCreate(BaseModel):
    """Payload sent by n8n when escalating a query to human support."""

    customer_name: str = Field(..., min_length=1, max_length=255, examples=["John Doe"])
    customer_query: str = Field(
        ..., min_length=1, max_length=2000, examples=["How do I reset my password?"]
    )
    priority: str = Field(..., min_length=1, max_length=50, examples=["High"])
    confidence: float = Field(..., ge=0, le=100, examples=[42.5])
    sentiment: str = Field(..., min_length=1, max_length=50, examples=["Negative"])


class TicketUpdate(BaseModel):
    """Partial update – only status and priority are mutable via PATCH."""

    status: Optional[str] = Field(None, min_length=1, max_length=50, examples=["Resolved"])
    priority: Optional[str] = Field(None, min_length=1, max_length=50, examples=["Low"])

    model_config = ConfigDict(extra="forbid")


class TicketResponse(BaseModel):
    """Full ticket representation returned by GET endpoints."""

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
    """Response returned after successfully creating a ticket."""

    success: bool = True
    ticket_id: int
    message: str = "Ticket created successfully"


# ---------------------------------------------------------------------------
# Dashboard schema
# ---------------------------------------------------------------------------

class DashboardStats(BaseModel):
    """Aggregated metrics for the support dashboard."""

    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    high_priority: int
    average_confidence: float


# ---------------------------------------------------------------------------
# Generic error schema (used in OpenAPI documentation)
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standard error envelope returned on failure."""

    detail: str
