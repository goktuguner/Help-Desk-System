"""User management router (admin only)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import require_admin
from app.database import get_session
from app.models import User
from app.schemas import UserActiveUpdate, UserRead, UserRoleUpdate

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """List all users (admin only)."""
    users = session.exec(select(User).order_by(User.created_at)).all()
    return users


@router.patch("/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: int,
    body: UserRoleUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Change a user's role (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    user.role = body.role
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}/active", response_model=UserRead)
def update_user_active(
    user_id: int,
    body: UserActiveUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Activate or deactivate a user (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    user.is_active = body.is_active
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
