"""Ticket CRUD router with filtering, assignment, and status management."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import joinedload
from sqlmodel import Session, col, select

from app.auth import get_current_user, require_admin
from app.database import get_session
from app.email_service import send_ticket_created_email
from app.models import Category, PriorityEnum, StatusEnum, Ticket, User
from app.schemas import (
    TicketAssign,
    TicketCreate,
    TicketPriorityUpdate,
    TicketRead,
    TicketStatusUpdate,
    TicketUpdate,
)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.get("/", response_model=list[TicketRead])
def list_tickets(
    status_filter: Optional[StatusEnum] = Query(None, alias="status"),
    priority_filter: Optional[PriorityEnum] = Query(None, alias="priority"),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List tickets with optional filtering. Users see only their own; admins see all."""
    query = select(Ticket)

    # Role-based visibility
    if current_user.role != "admin":
        query = query.where(Ticket.creator_id == current_user.id)

    # Filters
    if status_filter:
        query = query.where(Ticket.status == status_filter)
    if priority_filter:
        query = query.where(Ticket.priority == priority_filter)
    if category_id:
        query = query.where(Ticket.category_id == category_id)
    if search:
        query = query.where(
            col(Ticket.title).contains(search) | col(Ticket.description).contains(search)
        )

    query = query.order_by(col(Ticket.created_at).desc())
    query = query.options(
        joinedload(Ticket.category),
        joinedload(Ticket.creator),
        joinedload(Ticket.assignee),
    )
    tickets = session.exec(query).all()
    return tickets


@router.post("/", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(
    body: TicketCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new support ticket."""
    # Validate category exists
    category = session.get(Category, body.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    ticket = Ticket(
        title=body.title,
        description=body.description,
        priority=body.priority,
        category_id=body.category_id,
        creator_id=current_user.id,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    try:
        send_ticket_created_email(current_user, ticket)
    except Exception as e:
        print(f"Ticket created, but email could not be sent: {e}")

    return ticket


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(
    ticket_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get a single ticket by ID."""
    query = (
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(
            joinedload(Ticket.category),
            joinedload(Ticket.creator),
            joinedload(Ticket.assignee),
        )
    )
    ticket = session.exec(query).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Users can only see their own tickets
    if current_user.role != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return ticket


@router.put("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int,
    body: TicketUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update ticket details. Owner can edit title/description; admin can edit all fields."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    update_data = body.model_dump(exclude_unset=True)

    # Validate category if changing
    if "category_id" in update_data:
        category = session.get(Category, update_data["category_id"])
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    for key, value in update_data.items():
        setattr(ticket, key, value)

    ticket.updated_at = datetime.now(timezone.utc)
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Delete a ticket (admin only)."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    session.delete(ticket)
    session.commit()


@router.patch("/{ticket_id}/assign", response_model=TicketRead)
def assign_ticket(
    ticket_id: int,
    body: TicketAssign,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Assign a ticket to a user (admin only)."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if body.assignee_id is not None:
        assignee = session.get(User, body.assignee_id)
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee user not found")

    ticket.assignee_id = body.assignee_id
    ticket.updated_at = datetime.now(timezone.utc)
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketRead)
def update_ticket_status(
    ticket_id: int,
    body: TicketStatusUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Change ticket status (admin only)."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = body.status
    ticket.updated_at = datetime.now(timezone.utc)
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}/priority", response_model=TicketRead)
def update_ticket_priority(
    ticket_id: int,
    body: TicketPriorityUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Change ticket priority (admin only)."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.priority = body.priority
    ticket.updated_at = datetime.now(timezone.utc)
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket
