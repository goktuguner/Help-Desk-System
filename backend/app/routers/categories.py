"""Category CRUD router (admin-managed, readable by all authenticated users)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_user, require_admin
from app.database import get_session
from app.models import Category, Ticket, User
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List all categories."""
    categories = session.exec(select(Category).order_by(Category.name)).all()
    return categories


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    body: CategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Create a new category (admin only)."""
    existing = session.exec(select(Category).where(Category.name == body.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")

    category = Category(name=body.name, description=body.description)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    body: CategoryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Update a category (admin only)."""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = body.model_dump(exclude_unset=True)

    # Check name uniqueness if changing name
    if "name" in update_data:
        existing = session.exec(
            select(Category).where(
                Category.name == update_data["name"], Category.id != category_id
            )
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")

    for key, value in update_data.items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Delete a category (admin only). Fails if tickets reference it."""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Prevent deletion if tickets use this category
    ticket_count = len(
        session.exec(select(Ticket).where(Ticket.category_id == category_id)).all()
    )
    if ticket_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete: {ticket_count} ticket(s) use this category",
        )

    session.delete(category)
    session.commit()
