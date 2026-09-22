"""
API route definitions.
"""

from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import (
    DashboardStats,
    ErrorResponse,
    FailedRequestCreate,
    FailedRequestResponse,
    TicketCreate,
    TicketCreateResponse,
    TicketResponse,
    TicketUpdate,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /tickets
# ---------------------------------------------------------------------------

@router.post(
    "/tickets",
    response_model=TicketCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
    },
    summary="Create a new support ticket",
)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
) -> TicketCreateResponse:

    ticket = crud.create_ticket(
        db,
        ticket_in,
    )

    return TicketCreateResponse(
        success=True,
        ticket_id=ticket.id,
        message="Ticket created successfully",
    )


# ---------------------------------------------------------------------------
# POST /failed-requests
# ---------------------------------------------------------------------------

@router.post(
    "/failed-requests",
    response_model=FailedRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Store a failed request for review",
)
def create_failed_request(
    request_in: FailedRequestCreate,
    db: Session = Depends(get_db),
) -> FailedRequestResponse:

    failed_request = crud.create_failed_request(
        db=db,
        user_id=request_in.user_id,
        payload=request_in.payload,
        error=request_in.error,
    )

    return FailedRequestResponse(
        success=True,
        failed_request_id=failed_request.id,
        status=failed_request.status,
    )


# ---------------------------------------------------------------------------
# GET /tickets
# ---------------------------------------------------------------------------

@router.get(
    "/tickets",
    response_model=List[TicketResponse],
    summary="List all tickets",
)
def list_tickets(
    db: Session = Depends(get_db),
) -> List[TicketResponse]:

    return crud.get_tickets(db)


# ---------------------------------------------------------------------------
# GET /tickets/{id}
# ---------------------------------------------------------------------------

@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Ticket not found",
        }
    },
    summary="Get a ticket by ID",
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> TicketResponse:

    ticket = crud.get_ticket(
        db,
        ticket_id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found",
        )

    return ticket


# ---------------------------------------------------------------------------
# PATCH /tickets/{id}
# ---------------------------------------------------------------------------

@router.patch(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Ticket not found",
        },
        422: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
    },
    summary="Update ticket status or priority",
)
def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    db: Session = Depends(get_db),
) -> TicketResponse:

    if not ticket_in.model_dump(
        exclude_unset=True
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "At least one field "
                "(status or priority) must be provided"
            ),
        )

    ticket = crud.update_ticket(
        db,
        ticket_id,
        ticket_in,
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found",
        )

    return ticket


# ---------------------------------------------------------------------------
# DELETE /tickets/{id}
# ---------------------------------------------------------------------------

@router.delete(
    "/tickets/{ticket_id}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Ticket not found",
        }
    },
    summary="Delete a ticket",
)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> dict:

    deleted = crud.delete_ticket(
        db,
        ticket_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found",
        )

    return {
        "success": True,
        "message": (
            f"Ticket {ticket_id} deleted successfully"
        ),
    }


# ---------------------------------------------------------------------------
# GET /dashboard
# ---------------------------------------------------------------------------

@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Dashboard statistics",
)
def dashboard(
    db: Session = Depends(get_db),
) -> DashboardStats:

    return crud.get_dashboard_stats(db)