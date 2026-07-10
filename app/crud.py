"""
CRUD operations for the Ticket model.

All database interactions go through this module – route handlers
never touch the ORM session directly beyond calling these functions.
"""

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Ticket
from app.schemas import DashboardStats, TicketCreate, TicketUpdate


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_ticket(db: Session, ticket_in: TicketCreate) -> Ticket:
    """Persist a new ticket and return the created ORM instance."""
    ticket = Ticket(
        customer_name=ticket_in.customer_name,
        customer_query=ticket_in.customer_query,
        priority=ticket_in.priority,
        confidence=ticket_in.confidence,
        sentiment=ticket_in.sentiment,
        status="Open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def get_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
    """Return a single ticket by primary key, or None if not found."""
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def get_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
    """Return all tickets ordered by most recent first."""
    return (
        db.query(Ticket)
        .order_by(Ticket.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_ticket(
    db: Session, ticket_id: int, ticket_in: TicketUpdate
) -> Optional[Ticket]:
    """
    Apply a partial update to status and/or priority.
    Returns the updated ticket, or None if the ticket does not exist.
    """
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        return None

    update_data = ticket_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)
    return ticket


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_ticket(db: Session, ticket_id: int) -> bool:
    """
    Delete a ticket by ID.
    Returns True if deleted, False if the ticket was not found.
    """
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        return False

    db.delete(ticket)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Dashboard aggregations
# ---------------------------------------------------------------------------

def get_dashboard_stats(db: Session) -> DashboardStats:
    """
    Compute aggregate statistics for the support dashboard.

    Uses SQLAlchemy aggregate functions – no raw SQL.
    """
    total = db.query(func.count(Ticket.id)).scalar() or 0

    open_count = (
        db.query(func.count(Ticket.id))
        .filter(func.lower(Ticket.status) == "open")
        .scalar()
        or 0
    )

    resolved_count = (
        db.query(func.count(Ticket.id))
        .filter(func.lower(Ticket.status) == "resolved")
        .scalar()
        or 0
    )

    high_priority_count = (
        db.query(func.count(Ticket.id))
        .filter(func.lower(Ticket.priority) == "high")
        .scalar()
        or 0
    )

    avg_confidence = db.query(func.avg(Ticket.confidence)).scalar()

    return DashboardStats(
        total_tickets=total,
        open_tickets=open_count,
        resolved_tickets=resolved_count,
        high_priority=high_priority_count,
        average_confidence=round(float(avg_confidence), 1) if avg_confidence else 0.0,
    )
