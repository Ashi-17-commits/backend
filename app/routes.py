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
import os

from fastapi.security import OAuth2PasswordRequestForm
from app.auth import create_access_token
from app.auth import verify_token
from fastapi import Request
from app.rate_limit import limiter
router = APIRouter()



# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    summary="Admin login",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    admin_user = os.getenv("ADMIN_USER")
    admin_pass = os.getenv("ADMIN_PASS")

    if (
        form_data.username != admin_user
        or form_data.password != admin_pass
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(form_data.username)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

# ---------------------------------------------------------------------------
# POST /tickets
# ---------------------------------------------------------------------------

@router.post(
    "/tickets",
    response_model=TicketCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("20/minute")
def create_ticket(
    request: Request,
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
    _: str = Depends(verify_token),
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
    _: str = Depends(verify_token),
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
@router.patch("/tickets/{ticket_id}")
def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
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
@router.delete("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
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
@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
) -> DashboardStats:

    return crud.get_dashboard_stats(db)