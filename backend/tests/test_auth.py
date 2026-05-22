"""Tests for authentication endpoints."""


def test_register_success(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "newuser", "email": "new@test.com", "password": "pass123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["role"] == "user"


def test_register_duplicate_username(client, normal_user):
    resp = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "other@test.com", "password": "pass123"},
    )
    assert resp.status_code == 400
    assert "already taken" in resp.json()["detail"]


def test_login_success(client, normal_user):
    resp = client.post("/api/auth/login", json={"username": "testuser", "password": "test123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client, normal_user):
    resp = client.post("/api/auth/login", json={"username": "testuser", "password": "wrongpass"})
    assert resp.status_code == 401


def test_get_me(client, user_token):
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"
