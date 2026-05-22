"""Tests for category endpoints."""


def test_create_category(client, admin_token):
    resp = client.post(
        "/api/categories/",
        json={
            "name": "Network",
            "description": "Network issues",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Network"


def test_list_categories(client, user_token, category):
    resp = client.get("/api/categories/", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_create_category_user_forbidden(client, user_token):
    resp = client.post(
        "/api/categories/", json={"name": "Test"}, headers={"Authorization": f"Bearer {user_token}"}
    )
    assert resp.status_code == 403


def test_delete_category_with_tickets(client, admin_token, user_token, category):
    # Create a ticket using this category
    client.post(
        "/api/tickets/",
        json={
            "title": "T",
            "description": "D",
            "category_id": category.id,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    resp = client.delete(
        f"/api/categories/{category.id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 400
    assert "Cannot delete" in resp.json()["detail"]
