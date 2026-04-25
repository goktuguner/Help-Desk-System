"""Shared test fixtures for pytest."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.auth import hash_password
from app.database import get_session
from app.main import app
from app.models import Category, User


@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a TestClient with overridden DB session."""

    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session) -> User:
    """Create an admin user in the test DB."""
    user = User(
        username="admin",
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        role="admin",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="normal_user")
def normal_user_fixture(session: Session) -> User:
    """Create a normal user in the test DB."""
    user = User(
        username="testuser",
        email="test@test.com",
        hashed_password=hash_password("test123"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="category")
def category_fixture(session: Session) -> Category:
    """Create a test category."""
    cat = Category(name="Bug Report", description="Software bugs")
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@pytest.fixture(name="admin_token")
def admin_token_fixture(client: TestClient, admin_user: User) -> str:
    """Get a JWT token for the admin user."""
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    return resp.json()["access_token"]


@pytest.fixture(name="user_token")
def user_token_fixture(client: TestClient, normal_user: User) -> str:
    """Get a JWT token for the normal user."""
    resp = client.post("/api/auth/login", json={"username": "testuser", "password": "test123"})
    return resp.json()["access_token"]
