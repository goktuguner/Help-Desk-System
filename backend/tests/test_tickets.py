"""Tests for ticket endpoints."""


def test_create_ticket(client, user_token, category):
    resp = client.post(
        "/api/tickets/",
        json={
            "title": "Test ticket",
            "description": "A test issue",
            "priority": "high",
            "category_id": category.id,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Test ticket"
    assert resp.json()["status"] == "open"


def test_list_tickets(client, user_token, category):
    # Create a ticket first
    client.post(
        "/api/tickets/",
        json={
            "title": "T1",
            "description": "Desc",
            "category_id": category.id,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    resp = client.get("/api/tickets/", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_ticket(client, user_token, category):
    create = client.post(
        "/api/tickets/",
        json={
            "title": "T2",
            "description": "Desc",
            "category_id": category.id,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    tid = create.json()["id"]

    resp = client.get(f"/api/tickets/{tid}", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    assert resp.json()["id"] == tid


def test_filter_tickets_by_status(client, user_token, category):
    client.post(
        "/api/tickets/",
        json={
            "title": "Open",
            "description": "D",
            "category_id": category.id,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    resp = client.get(
        "/api/tickets/?status=open", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert resp.status_code == 200
    for t in resp.json():
        assert t["status"] == "open"


def test_update_ticket_status(client, admin_token, user_token, category):
    create = client.post(
        "/api/tickets/",
        json={
            "title": "T3",
            "description": "D",
            "category_id": category.id,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    tid = create.json()["id"]

    resp = client.patch(
        f"/api/tickets/{tid}/status",
        json={"status": "in_progress"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


def test_assign_ticket(client, admin_token, user_token, category, admin_user):
    create = client.post(
        "/api/tickets/",
        json={
            "title": "T4",
            "description": "D",
            "category_id": category.id,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    tid = create.json()["id"]

    resp = client.patch(
        f"/api/tickets/{tid}/assign",
        json={"assignee_id": admin_user.id},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["assignee_id"] == admin_user.id


def test_delete_ticket_admin(client, admin_token, user_token, category):
    create = client.post(
        "/api/tickets/",
        json={
            "title": "T5",
            "description": "D",
            "category_id": category.id,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    tid = create.json()["id"]

    resp = client.delete(f"/api/tickets/{tid}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 204


def test_delete_ticket_user_forbidden(client, user_token, category):
    create = client.post(
        "/api/tickets/",
        json={
            "title": "T6",
            "description": "D",
            "category_id": category.id,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    tid = create.json()["id"]

    resp = client.delete(f"/api/tickets/{tid}", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403
