"""Ticket card widget for the dashboard list."""

import customtkinter as ctk
from datetime import datetime

from config import COLORS
from widgets.status_badge import StatusBadge


class TicketCard(ctk.CTkFrame):
    """A card-style frame that displays a single ticket summary."""

    def __init__(self, master, ticket: dict, on_click=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            cursor="hand2",
            **kwargs,
        )
        self.ticket = ticket
        self.on_click = on_click

        self.bind("<Button-1>", self._handle_click)

        # ── Row 1: Title + Priority ────────────────────────────────────────
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", padx=14, pady=(12, 4))
        row1.bind("<Button-1>", self._handle_click)

        title_label = ctk.CTkLabel(
            row1,
            text=f"#{ticket['id']}  {ticket['title']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        title_label.pack(side="left", fill="x", expand=True)
        title_label.bind("<Button-1>", self._handle_click)

        StatusBadge(row1, "priority", ticket["priority"]).pack(side="right", padx=(8, 0))

        # ── Row 2: Status + Category + Date ────────────────────────────────
        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.pack(fill="x", padx=14, pady=(0, 10))
        row2.bind("<Button-1>", self._handle_click)

        StatusBadge(row2, "status", ticket["status"]).pack(side="left")

        category_name = ticket.get("category", {}).get("name", "—") if ticket.get("category") else "—"
        ctk.CTkLabel(
            row2,
            text=f"📁 {category_name}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(10, 0))

        # Creator
        creator_name = ticket.get("creator", {}).get("username", "—") if ticket.get("creator") else "—"
        ctk.CTkLabel(
            row2,
            text=f"👤 {creator_name}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(10, 0))

        # Assignee
        assignee_name = "Unassigned"
        if ticket.get("assignee"):
            assignee_name = ticket["assignee"].get("username", "Unassigned")
        ctk.CTkLabel(
            row2,
            text=f"🔧 {assignee_name}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=(10, 0))

        # Date
        created = ticket.get("created_at", "")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                created = dt.strftime("%b %d, %Y")
            except Exception:
                pass
        ctk.CTkLabel(
            row2,
            text=created,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        ).pack(side="right")

    def _handle_click(self, event=None):
        if self.on_click:
            self.on_click(self.ticket)

    # Hover effect
    def _on_enter(self, event=None):
        self.configure(fg_color=COLORS["bg_hover"])

    def _on_leave(self, event=None):
        self.configure(fg_color=COLORS["bg_card"])
