"""Reusable status badge widget for tickets."""

import customtkinter as ctk

from config import COLORS

STATUS_LABELS = {
    "open": "Open",
    "in_progress": "In Progress",
    "resolved": "Resolved",
    "closed": "Closed",
}

PRIORITY_LABELS = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "critical": "Critical",
}


class StatusBadge(ctk.CTkLabel):
    """A colored label that renders status or priority as a badge."""

    def __init__(self, master, badge_type: str, value: str, **kwargs):
        if badge_type == "status":
            text = STATUS_LABELS.get(value, value)
            color = COLORS.get(f"status_{value}", COLORS["text_muted"])
        elif badge_type == "priority":
            text = PRIORITY_LABELS.get(value, value)
            color = COLORS.get(f"priority_{value}", COLORS["text_muted"])
        else:
            text = value
            color = COLORS["text_muted"]

        super().__init__(
            master,
            text=f"  {text}  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=color,
            text_color="#FFFFFF",
            corner_radius=6,
            height=24,
            **kwargs,
        )
