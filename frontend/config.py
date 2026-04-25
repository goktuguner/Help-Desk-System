"""Configuration for the frontend application."""

# Backend API base URL
API_BASE_URL = "http://localhost:8000/api"

# Application settings
APP_TITLE = "HelpDesk Ticketing System"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
MIN_WIDTH = 900
MIN_HEIGHT = 600

# Color palette
COLORS = {
    "primary": ("#4338CA", "#6366F1"),       # Indigo 700 / Indigo 500
    "primary_hover": ("#3730A3", "#4F46E5"), # Indigo 800 / Indigo 600
    "primary_light": ("#818CF8", "#A5B4FC"), # Indigo 400 / Indigo 300
    "secondary": ("#0284C7", "#0EA5E9"),     # Sky 600 / Sky 500
    "success": "#10B981",       # Emerald
    "warning": "#F59E0B",       # Amber
    "danger": "#EF4444",        # Red
    "info": "#6366F1",          # Indigo

    # Status colors
    "status_open": "#F59E0B",
    "status_in_progress": "#3B82F6",
    "status_resolved": "#10B981",
    "status_closed": "#6B7280",

    # Priority colors
    "priority_low": "#6B7280",
    "priority_medium": "#F59E0B",
    "priority_high": "#F97316",
    "priority_critical": "#EF4444",

    # Neutral
    "bg_dark": ("#F1F5F9", "#1E1B2E"),      # Slate 100 / Dark
    "bg_card": ("#FFFFFF", "#2A2740"),      # White / Dark Card
    "bg_hover": ("#E2E8F0", "#353250"),     # Slate 200 / Dark Hover
    "text_primary": ("#0F172A", "#F8FAFC"), # Slate 900 / Light
    "text_secondary": ("#475569", "#94A3B8"), # Slate 600 / Muted Light
    "text_muted": ("#64748B", "#64748B"),     # Slate 500 / Slate 500
    "border": ("#CBD5E1", "#3B3855"),       # Slate 300 / Dark Border
}
