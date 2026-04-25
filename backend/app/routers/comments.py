"""Comment CRUD router for ticket discussions."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, col, select
from sqlalchemy.orm import joinedload

from app.auth import get_current_user
from app.database import get_session
from app.models import Comment, StatusEnum, Ticket, User
from app.schemas import CommentCreate, CommentRead

router = APIRouter(prefix="/api", tags=["Comments"])


@router.get("/tickets/{ticket_id}/comments", response_model=list[CommentRead])
def list_comments(
    ticket_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List all comments for a ticket."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Users can only see comments on their own tickets
    if current_user.role != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    comments = session.exec(
        select(Comment)
        .where(Comment.ticket_id == ticket_id)
        .options(joinedload(Comment.author))
        .order_by(col(Comment.created_at).asc())
    ).all()
    return comments


@router.post(
    "/tickets/{ticket_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    ticket_id: int,
    body: CommentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Add a comment to a ticket."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Cannot comment on closed tickets
    if ticket.status == StatusEnum.closed:
        raise HTTPException(status_code=400, detail="Cannot comment on a closed ticket")

    # Users can only comment on their own tickets
    if current_user.role != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    comment = Comment(
        content=body.content,
        ticket_id=ticket_id,
        author_id=current_user.id,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment. Only the author or admin can delete."""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if current_user.role != "admin" and comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    session.delete(comment)
    session.commit()
