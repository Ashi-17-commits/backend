"""
CRUD operations for Ticket and FailedRequest models.
"""

import hashlib
import json
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import FailedRequest, Ticket
from app.schemas import (
    DashboardStats,
    TicketCreate,
    TicketUpdate,
)


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

def make_idempotency_key(
    user_id: str,
    message_id: str,
) -> str:
    """
    Generate a deterministic SHA-256 idempotency key
    from Telegram user_id and message_id.
    """

    raw = f"{user_id}-{message_id}"

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------------------------
# Ticket Create
# ---------------------------------------------------------------------------

def create_ticket(
    db: Session,
    ticket_in: TicketCreate,
) -> Ticket:
    """
    Create a ticket only if this Telegram message
    has not already been processed.
    """

    # 1. Generate deterministic key
    idempotency_key = make_idempotency_key(
        ticket_in.user_id,
        ticket_in.message_id,
    )

    # 2. Check whether this request was already processed
    existing_ticket = (
        db.query(Ticket)
        .filter(
            Ticket.idempotency_key == idempotency_key
        )
        .first()
    )

    # 3. Duplicate request → return existing ticket
    if existing_ticket:
        return existing_ticket

    # 4. Create new ticket
    ticket = Ticket(
        idempotency_key=idempotency_key,
        customer_name=ticket_in.customer_name,
        customer_query=ticket_in.customer_query,
        priority=ticket_in.priority,
        confidence=ticket_in.confidence,
        sentiment=ticket_in.sentiment,
        status="Open",
    )

    # 5. Save
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


# ---------------------------------------------------------------------------
# Ticket Read
# ---------------------------------------------------------------------------

def get_ticket(
    db: Session,
    ticket_id: int,
) -> Optional[Ticket]:
    """Return one ticket by ID."""

    return (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )


def get_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[Ticket]:
    """Return all tickets, newest first."""

    return (
        db.query(Ticket)
        .order_by(Ticket.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ---------------------------------------------------------------------------
# Ticket Update
# ---------------------------------------------------------------------------

def update_ticket(
    db: Session,
    ticket_id: int,
    ticket_in: TicketUpdate,
) -> Optional[Ticket]:
    """Update ticket status and/or priority."""

    ticket = get_ticket(db, ticket_id)

    if ticket is None:
        return None

    update_data = ticket_in.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)

    return ticket


# ---------------------------------------------------------------------------
# Ticket Delete
# ---------------------------------------------------------------------------

def delete_ticket(
    db: Session,
    ticket_id: int,
) -> bool:
    """Delete ticket by ID."""

    ticket = get_ticket(db, ticket_id)

    if ticket is None:
        return False

    db.delete(ticket)
    db.commit()

    return True


# ---------------------------------------------------------------------------
# Failed Requests
# ---------------------------------------------------------------------------

def create_failed_request(
    db: Session,
    user_id: str,
    payload: dict,
    error: str,
) -> FailedRequest:
    """
    Store a failed request for manual review.
    """

    failed_request = FailedRequest(
        user_id=user_id,
        payload=json.dumps(payload),
        error=error,
        status="needs_review",
    )

    db.add(failed_request)
    db.commit()
    db.refresh(failed_request)

    return failed_request


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def get_dashboard_stats(
    db: Session,
) -> DashboardStats:
    """Compute aggregate dashboard statistics."""

    total = (
        db.query(func.count(Ticket.id))
        .scalar()
        or 0
    )

    open_count = (
        db.query(func.count(Ticket.id))
        .filter(
            func.lower(Ticket.status) == "open"
        )
        .scalar()
        or 0
    )

    resolved_count = (
        db.query(func.count(Ticket.id))
        .filter(
            func.lower(Ticket.status) == "resolved"
        )
        .scalar()
        or 0
    )

    high_priority_count = (
        db.query(func.count(Ticket.id))
        .filter(
            func.lower(Ticket.priority) == "high"
        )
        .scalar()
        or 0
    )

    avg_confidence = (
        db.query(func.avg(Ticket.confidence))
        .scalar()
    )

    return DashboardStats(
        total_tickets=total,
        open_tickets=open_count,
        resolved_tickets=resolved_count,
        high_priority=high_priority_count,
        average_confidence=(
            round(float(avg_confidence), 1)
            if avg_confidence
            else 0.0
        ),
    )