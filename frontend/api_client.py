"""HTTP client wrapper for communicating with the FastAPI backend."""

import requests

from config import API_BASE_URL


class APIClient:
    """Thin wrapper around requests that manages the auth token and base URL."""

    def __init__(self):
        self.base_url = API_BASE_URL
        self.token: str | None = None

    # ── Auth header ────────────────────────────────────────────────────────

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ── Generic request helpers ────────────────────────────────────────────

    def _get(self, path: str, params: dict | None = None) -> requests.Response:
        return requests.get(
            f"{self.base_url}{path}", headers=self._headers(), params=params, timeout=10
        )

    def _post(self, path: str, json: dict | None = None) -> requests.Response:
        return requests.post(
            f"{self.base_url}{path}", headers=self._headers(), json=json, timeout=10
        )

    def _put(self, path: str, json: dict | None = None) -> requests.Response:
        return requests.put(
            f"{self.base_url}{path}", headers=self._headers(), json=json, timeout=10
        )

    def _patch(self, path: str, json: dict | None = None) -> requests.Response:
        return requests.patch(
            f"{self.base_url}{path}", headers=self._headers(), json=json, timeout=10
        )

    def _delete(self, path: str) -> requests.Response:
        return requests.delete(f"{self.base_url}{path}", headers=self._headers(), timeout=10)

    # ── Auth ───────────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> dict:
        resp = self._post("/auth/login", {"username": username, "password": password})
        resp.raise_for_status()
        data = resp.json()
        self.token = data["access_token"]
        return data

    def register(self, username: str, email: str, password: str) -> dict:
        resp = self._post(
            "/auth/register",
            {"username": username, "email": email, "password": password},
        )
        resp.raise_for_status()
        return resp.json()

    def get_me(self) -> dict:
        resp = self._get("/auth/me")
        resp.raise_for_status()
        return resp.json()

    def logout(self):
        self.token = None

    # ── Tickets ────────────────────────────────────────────────────────────

    def list_tickets(
        self,
        status: str | None = None,
        priority: str | None = None,
        category_id: int | None = None,
        search: str | None = None,
    ) -> list[dict]:
        params = {}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if category_id:
            params["category_id"] = category_id
        if search:
            params["search"] = search
        resp = self._get("/tickets/", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_ticket(self, ticket_id: int) -> dict:
        resp = self._get(f"/tickets/{ticket_id}")
        resp.raise_for_status()
        return resp.json()

    def create_ticket(self, title: str, description: str, priority: str, category_id: int) -> dict:
        resp = self._post(
            "/tickets/",
            {
                "title": title,
                "description": description,
                "priority": priority,
                "category_id": category_id,
            },
        )
        resp.raise_for_status()
        return resp.json()

    def update_ticket(self, ticket_id: int, data: dict) -> dict:
        resp = self._put(f"/tickets/{ticket_id}", data)
        resp.raise_for_status()
        return resp.json()

    def delete_ticket(self, ticket_id: int):
        resp = self._delete(f"/tickets/{ticket_id}")
        resp.raise_for_status()

    def assign_ticket(self, ticket_id: int, assignee_id: int | None) -> dict:
        resp = self._patch(f"/tickets/{ticket_id}/assign", {"assignee_id": assignee_id})
        resp.raise_for_status()
        return resp.json()

    def update_ticket_status(self, ticket_id: int, status: str) -> dict:
        resp = self._patch(f"/tickets/{ticket_id}/status", {"status": status})
        resp.raise_for_status()
        return resp.json()

    def update_ticket_priority(self, ticket_id: int, priority: str) -> dict:
        resp = self._patch(f"/tickets/{ticket_id}/priority", {"priority": priority})
        resp.raise_for_status()
        return resp.json()

    # ── Comments ───────────────────────────────────────────────────────────

    def list_comments(self, ticket_id: int) -> list[dict]:
        resp = self._get(f"/tickets/{ticket_id}/comments")
        resp.raise_for_status()
        return resp.json()

    def create_comment(self, ticket_id: int, content: str) -> dict:
        resp = self._post(f"/tickets/{ticket_id}/comments", {"content": content})
        resp.raise_for_status()
        return resp.json()

    def delete_comment(self, comment_id: int):
        resp = self._delete(f"/comments/{comment_id}")
        resp.raise_for_status()

    # ── Categories ─────────────────────────────────────────────────────────

    def list_categories(self) -> list[dict]:
        resp = self._get("/categories/")
        resp.raise_for_status()
        return resp.json()

    def create_category(self, name: str, description: str | None = None) -> dict:
        resp = self._post("/categories/", {"name": name, "description": description})
        resp.raise_for_status()
        return resp.json()

    def update_category(self, category_id: int, data: dict) -> dict:
        resp = self._put(f"/categories/{category_id}", data)
        resp.raise_for_status()
        return resp.json()

    def delete_category(self, category_id: int):
        resp = self._delete(f"/categories/{category_id}")
        resp.raise_for_status()

    # ── Users ──────────────────────────────────────────────────────────────

    def list_users(self) -> list[dict]:
        resp = self._get("/users/")
        resp.raise_for_status()
        return resp.json()

    def update_user_role(self, user_id: int, role: str) -> dict:
        resp = self._patch(f"/users/{user_id}/role", {"role": role})
        resp.raise_for_status()
        return resp.json()

    def update_user_active(self, user_id: int, is_active: bool) -> dict:
        resp = self._patch(f"/users/{user_id}/active", {"is_active": is_active})
        resp.raise_for_status()
        return resp.json()
