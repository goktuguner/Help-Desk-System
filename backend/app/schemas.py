"""Pydantic schemas for API request / response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models import PriorityEnum, RoleEnum, StatusEnum


# ── Auth ───────────────────────────────────────────────────────────────────────


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── User ───────────────────────────────────────────────────────────────────────


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    role: RoleEnum
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    role: RoleEnum


class UserActiveUpdate(BaseModel):
    is_active: bool


# ── Category ───────────────────────────────────────────────────────────────────


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: Optional[str] = Field(default=None, max_length=255)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    description: Optional[str] = Field(default=None, max_length=255)


class CategoryRead(BaseModel):
    id: int
    name: str
    description: Optional[str]

    model_config = {"from_attributes": True}


# ── Ticket ─────────────────────────────────────────────────────────────────────


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    priority: PriorityEnum = PriorityEnum.medium
    category_id: int


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, min_length=1)
    priority: Optional[PriorityEnum] = None
    category_id: Optional[int] = None


class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    status: StatusEnum
    priority: PriorityEnum
    category_id: int
    category: Optional[CategoryRead] = None
    creator_id: int
    creator: Optional[UserRead] = None
    assignee_id: Optional[int] = None
    assignee: Optional[UserRead] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketAssign(BaseModel):
    assignee_id: Optional[int] = None


class TicketStatusUpdate(BaseModel):
    status: StatusEnum


class TicketPriorityUpdate(BaseModel):
    priority: PriorityEnum


# ── Comment ────────────────────────────────────────────────────────────────────


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)


class CommentRead(BaseModel):
    id: int
    content: str
    ticket_id: int
    author_id: int
    author: Optional[UserRead] = None
    created_at: datetime

    model_config = {"from_attributes": True}
