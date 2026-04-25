"""Main application — CustomTkinter entry point with view navigation."""

import customtkinter as ctk

from api_client import APIClient
from config import APP_TITLE, COLORS, MIN_HEIGHT, MIN_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH
from views.admin_panel_view import AdminPanelView
from views.dashboard_view import DashboardView
from views.login_view import LoginView
from views.register_view import RegisterView
from views.ticket_detail_view import TicketDetailView
from views.ticket_form_view import TicketFormView


class HelpDeskApp(ctk.CTk):
    """Root application window that manages view switching."""

    def __init__(self):
        super().__init__()

        # Window config
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.configure(fg_color=COLORS["bg_dark"])

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        # State
        self.api = APIClient()
        self.user_data: dict | None = None
        self.current_view: ctk.CTkFrame | None = None

        # Start with login
        self._show_login()

    # ── View management ────────────────────────────────────────────────────

    def _switch_view(self, new_view: ctk.CTkFrame):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = new_view
        self.current_view.pack(fill="both", expand=True)

    # ── Navigation callbacks ───────────────────────────────────────────────

    def _show_login(self):
        self._switch_view(
            LoginView(
                self,
                api_client=self.api,
                on_login_success=self._on_login_success,
                on_show_register=self._show_register,
            )
        )

    def _show_register(self):
        self._switch_view(
            RegisterView(
                self,
                api_client=self.api,
                on_register_success=self._show_login,
                on_show_login=self._show_login,
            )
        )

    def _on_login_success(self, user_data: dict):
        self.user_data = user_data
        self._show_dashboard()

    def _show_dashboard(self):
        self._switch_view(
            DashboardView(
                self,
                api_client=self.api,
                user_data=self.user_data,
                on_open_ticket=self._show_ticket_detail,
                on_new_ticket=self._show_new_ticket,
                on_open_admin=self._show_admin_panel,
                on_logout=self._logout,
            )
        )

    def _show_ticket_detail(self, ticket: dict):
        self._switch_view(
            TicketDetailView(
                self,
                api_client=self.api,
                user_data=self.user_data,
                ticket=ticket,
                on_back=self._show_dashboard,
            )
        )

    def _show_new_ticket(self):
        self._switch_view(
            TicketFormView(
                self,
                api_client=self.api,
                user_data=self.user_data,
                on_back=self._show_dashboard,
            )
        )

    def _show_admin_panel(self):
        self._switch_view(
            AdminPanelView(
                self,
                api_client=self.api,
                user_data=self.user_data,
                on_back=self._show_dashboard,
            )
        )

    def _logout(self):
        self.api.logout()
        self.user_data = None
        self._show_login()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = HelpDeskApp()
    app.mainloop()
