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
    "primary": "#6366F1",       # Indigo
    "primary_hover": "#4F46E5",
    "primary_light": "#A5B4FC",
    "secondary": "#0EA5E9",     # Sky blue
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
    "bg_dark": "#1E1B2E",
    "bg_card": "#2A2740",
    "bg_hover": "#353250",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "border": "#3B3855",
}
