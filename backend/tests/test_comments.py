"""Tests for comment endpoints."""


def test_create_comment(client, user_token, category):
    ticket = client.post("/api/tickets/", json={
        "title": "T", "description": "D", "category_id": category.id,
    }, headers={"Authorization": f"Bearer {user_token}"}).json()

    resp = client.post(f"/api/tickets/{ticket['id']}/comments",
                       json={"content": "A test comment"},
                       headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 201
    assert resp.json()["content"] == "A test comment"


def test_list_comments(client, user_token, category):
    ticket = client.post("/api/tickets/", json={
        "title": "T", "description": "D", "category_id": category.id,
    }, headers={"Authorization": f"Bearer {user_token}"}).json()

    client.post(f"/api/tickets/{ticket['id']}/comments",
                json={"content": "C1"},
                headers={"Authorization": f"Bearer {user_token}"})

    resp = client.get(f"/api/tickets/{ticket['id']}/comments",
                      headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_comment_on_closed_ticket(client, user_token, admin_token, category):
    ticket = client.post("/api/tickets/", json={
        "title": "T", "description": "D", "category_id": category.id,
    }, headers={"Authorization": f"Bearer {user_token}"}).json()

    # Close the ticket
    client.patch(f"/api/tickets/{ticket['id']}/status",
                 json={"status": "closed"},
                 headers={"Authorization": f"Bearer {admin_token}"})

    resp = client.post(f"/api/tickets/{ticket['id']}/comments",
                       json={"content": "Should fail"},
                       headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 400
