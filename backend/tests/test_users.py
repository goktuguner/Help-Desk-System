"""Tests for user management endpoints."""


def test_list_users(client, admin_token, normal_user):
    resp = client.get("/api/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_list_users_non_admin_forbidden(client, user_token):
    resp = client.get("/api/users/", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403


def test_change_user_role(client, admin_token, normal_user):
    resp = client.patch(f"/api/users/{normal_user.id}/role",
                        json={"role": "admin"},
                        headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"
