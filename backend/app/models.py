"""SQLModel database table definitions for the Help Desk system."""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


# ── Enums ──────────────────────────────────────────────────────────────────────


class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"


class StatusEnum(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class PriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


# ── Helpers ────────────────────────────────────────────────────────────────────


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Models ─────────────────────────────────────────────────────────────────────


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    email: str = Field(index=True, unique=True, max_length=120)
    hashed_password: str
    role: RoleEnum = Field(default=RoleEnum.user)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=_utcnow)

    # relationships
    created_tickets: list["Ticket"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "Ticket.creator_id"},
    )
    assigned_tickets: list["Ticket"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "Ticket.assignee_id"},
    )
    comments: list["Comment"] = Relationship(back_populates="author")


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=80)
    description: Optional[str] = Field(default=None, max_length=255)

    tickets: list["Ticket"] = Relationship(back_populates="category")


class Ticket(SQLModel, table=True):
    __tablename__ = "tickets"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str
    status: StatusEnum = Field(default=StatusEnum.open)
    priority: PriorityEnum = Field(default=PriorityEnum.medium)

    category_id: int = Field(foreign_key="categories.id")
    creator_id: int = Field(foreign_key="users.id")
    assignee_id: Optional[int] = Field(default=None, foreign_key="users.id")

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    # relationships
    category: Optional[Category] = Relationship(back_populates="tickets")
    creator: Optional[User] = Relationship(
        back_populates="created_tickets",
        sa_relationship_kwargs={"foreign_keys": "[Ticket.creator_id]"},
    )
    assignee: Optional[User] = Relationship(
        back_populates="assigned_tickets",
        sa_relationship_kwargs={"foreign_keys": "[Ticket.assignee_id]"},
    )
    comments: list["Comment"] = Relationship(back_populates="ticket")


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    ticket_id: int = Field(foreign_key="tickets.id")
    author_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=_utcnow)

    # relationships
    ticket: Optional[Ticket] = Relationship(back_populates="comments")
    author: Optional[User] = Relationship(back_populates="comments")
