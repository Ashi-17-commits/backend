"""
API route definitions.

All ticket and dashboard endpoints are registered here and
included in the main FastAPI application via app.main.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import (
    DashboardStats,
    ErrorResponse,
    TicketCreate,
    TicketCreateResponse,
    TicketResponse,
    TicketUpdate,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /tickets – called by n8n when AI confidence is below threshold
# ---------------------------------------------------------------------------

@router.post(
    "/tickets",
    response_model=TicketCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
    summary="Create a new support ticket",
    description=(
        "Creates a ticket when the n8n workflow escalates a customer query "
        "to human support. Called from the FALSE branch of the confidence IF node."
    ),
)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
) -> TicketCreateResponse:
    ticket = crud.create_ticket(db, ticket_in)
    return TicketCreateResponse(
        success=True,
        ticket_id=ticket.id,
        message="Ticket created successfully",
    )


# ---------------------------------------------------------------------------
# GET /tickets – list all tickets
# ---------------------------------------------------------------------------

@router.get(
    "/tickets",
    response_model=List[TicketResponse],
    summary="List all tickets",
    description="Returns all support tickets ordered by creation date (newest first).",
)
def list_tickets(db: Session = Depends(get_db)) -> List[TicketResponse]:
    return crud.get_tickets(db)


# ---------------------------------------------------------------------------
# GET /tickets/{id} – retrieve a single ticket
# ---------------------------------------------------------------------------

@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    responses={404: {"model": ErrorResponse, "description": "Ticket not found"}},
    summary="Get a ticket by ID",
)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)) -> TicketResponse:
    ticket = crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found",
        )
    return ticket


# ---------------------------------------------------------------------------
# PATCH /tickets/{id} – update status and/or priority
# ---------------------------------------------------------------------------

@router.patch(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Ticket not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
    summary="Update ticket status or priority",
)
def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    db: Session = Depends(get_db),
) -> TicketResponse:
    if not ticket_in.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field (status or priority) must be provided",
        )

    ticket = crud.update_ticket(db, ticket_id, ticket_in)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found",
        )
    return ticket


# ---------------------------------------------------------------------------
# DELETE /tickets/{id} – remove a ticket
# ---------------------------------------------------------------------------

@router.delete(
    "/tickets/{ticket_id}",
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Ticket not found"}},
    summary="Delete a ticket",
)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)) -> dict:
    deleted = crud.delete_ticket(db, ticket_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found",
        )
    return {"success": True, "message": f"Ticket {ticket_id} deleted successfully"}


# ---------------------------------------------------------------------------
# GET /dashboard – aggregated support metrics
# ---------------------------------------------------------------------------

@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Dashboard statistics",
    description=(
        "Returns aggregate ticket metrics: totals, open/resolved counts, "
        "high-priority count, and average AI confidence score."
    ),
)
def dashboard(db: Session = Depends(get_db)) -> DashboardStats:
    return crud.get_dashboard_stats(db)
