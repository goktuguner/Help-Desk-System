"""Dashboard view — main screen with ticket list, filters, and quick actions."""

import customtkinter as ctk
from tkinter import messagebox

from config import COLORS
from widgets.ticket_card import TicketCard


class DashboardView(ctk.CTkFrame):
    """Main dashboard with sidebar filters and scrollable ticket list."""

    def __init__(
        self,
        master,
        api_client,
        user_data: dict,
        on_open_ticket,
        on_new_ticket,
        on_open_admin,
        on_logout,
    ):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.api = api_client
        self.user_data = user_data
        self.on_open_ticket = on_open_ticket
        self.on_new_ticket = on_new_ticket
        self.on_open_admin = on_open_admin
        self.on_logout = on_logout

        self.categories: list[dict] = []
        self._build_ui()
        self.load_tickets()

    # ── Build UI ───────────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        self._build_topbar()

        # Content area — sidebar + ticket list
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self._build_sidebar(content)
        self._build_ticket_list(content)

    def _build_topbar(self):
        topbar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        # Logo
        ctk.CTkLabel(
            topbar,
            text="🎫  HelpDesk",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=20)

        # Right side — user info + theme + logout
        right = ctk.CTkFrame(topbar, fg_color="transparent")
        right.pack(side="right", padx=16)

        role_color = COLORS["primary"] if self.user_data["role"] == "admin" else COLORS["text_muted"]
        ctk.CTkLabel(
            right,
            text=f"👤 {self.user_data['username']}",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=(0, 4))

        ctk.CTkLabel(
            right,
            text=f"({self.user_data['role'].upper()})",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=role_color,
        ).pack(side="left", padx=(0, 16))

        # Theme Toggle
        current_theme = ctk.get_appearance_mode()
        self.theme_btn = ctk.CTkButton(
            right,
            text="☀️ Light" if current_theme == "Dark" else "🌙 Dark",
            width=70,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="left", padx=(0, 16))

        ctk.CTkButton(
            right,
            text="Logout",
            width=80,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["danger"],
            hover_color="#DC2626",
            command=self.on_logout,
        ).pack(side="left")

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="🌙 Dark")
        else:
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="☀️ Light")

    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12, width=230)
        sidebar.pack(side="left", fill="y", padx=(0, 12), pady=(12, 0))
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="Filters",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 12))

        # ── Status filter ──────────────────────────────────────────────────
        ctk.CTkLabel(
            sidebar, text="Status", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=16, pady=(4, 2))

        self.status_var = ctk.StringVar(value="All")
        self.status_menu = ctk.CTkOptionMenu(
            sidebar,
            values=["All", "open", "in_progress", "resolved", "closed"],
            variable=self.status_var,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_hover"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            width=196,
            command=lambda _: self.load_tickets(),
        )
        self.status_menu.pack(padx=16, pady=(0, 8))

        # ── Priority filter ────────────────────────────────────────────────
        ctk.CTkLabel(
            sidebar, text="Priority", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=16, pady=(4, 2))

        self.priority_var = ctk.StringVar(value="All")
        self.priority_menu = ctk.CTkOptionMenu(
            sidebar,
            values=["All", "low", "medium", "high", "critical"],
            variable=self.priority_var,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_hover"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            width=196,
            command=lambda _: self.load_tickets(),
        )
        self.priority_menu.pack(padx=16, pady=(0, 8))

        # ── Category filter ────────────────────────────────────────────────
        ctk.CTkLabel(
            sidebar, text="Category", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=16, pady=(4, 2))

        self.category_var = ctk.StringVar(value="All")
        self.category_menu = ctk.CTkOptionMenu(
            sidebar,
            values=["All"],
            variable=self.category_var,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_hover"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            width=196,
            command=lambda _: self.load_tickets(),
        )
        self.category_menu.pack(padx=16, pady=(0, 12))

        # Load categories
        self._load_categories()

        # ── Search ─────────────────────────────────────────────────────────
        ctk.CTkLabel(
            sidebar, text="Search", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=16, pady=(4, 2))

        self.search_entry = ctk.CTkEntry(
            sidebar,
            height=34,
            corner_radius=8,
            placeholder_text="Search tickets...",
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=196,
        )
        self.search_entry.pack(padx=16, pady=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self.load_tickets())

        ctk.CTkButton(
            sidebar,
            text="🔍  Search",
            height=34,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(size=12),
            width=196,
            command=self.load_tickets,
        ).pack(padx=16, pady=(0, 16))

        # ── Separator ─────────────────────────────────────────────────────
        ctk.CTkFrame(sidebar, fg_color=COLORS["border"], height=1).pack(fill="x", padx=16, pady=4)

        # ── Action buttons ─────────────────────────────────────────────────
        ctk.CTkButton(
            sidebar,
            text="➕  New Ticket",
            height=40,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#059669",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=196,
            command=self.on_new_ticket,
        ).pack(padx=16, pady=(16, 8))

        if self.user_data["role"] == "admin":
            ctk.CTkButton(
                sidebar,
                text="⚙️  Admin Panel",
                height=38,
                corner_radius=8,
                fg_color=COLORS["secondary"],
                hover_color="#0284C7",
                font=ctk.CTkFont(size=13),
                width=196,
                command=self.on_open_admin,
            ).pack(padx=16, pady=(0, 16))

    def _build_ticket_list(self, parent):
        list_frame = ctk.CTkFrame(parent, fg_color="transparent")
        list_frame.pack(side="left", fill="both", expand=True, pady=(12, 0))

        # Header
        header = ctk.CTkFrame(list_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        self.ticket_count_label = ctk.CTkLabel(
            header,
            text="Tickets (0)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        self.ticket_count_label.pack(side="left")

        ctk.CTkButton(
            header,
            text="🔄 Refresh",
            width=90,
            height=30,
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            command=self.load_tickets,
        ).pack(side="right")
        
        self.sort_var = ctk.StringVar(value="Newest First")
        self.sort_menu = ctk.CTkOptionMenu(
            header,
            values=["Newest First", "Oldest First", "Priority (High-Low)", "Status"],
            variable=self.sort_var,
            width=160,
            height=30,
            fg_color=COLORS["bg_card"],
            button_color=COLORS["bg_hover"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_hover"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            command=lambda _: self._apply_sorting()
        )
        self.sort_menu.pack(side="right", padx=16)
        
        ctk.CTkLabel(
            header,
            text="Sort By:",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(side="right")

        # Scrollable ticket list
        self.ticket_scroll = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["primary"],
        )
        self.ticket_scroll.pack(fill="both", expand=True)

    # ── Data loading ───────────────────────────────────────────────────────

    def _load_categories(self):
        import threading
        def fetch():
            try:
                cats = self.api.list_categories()
                self.after(0, self._on_categories_loaded, cats)
            except Exception:
                pass
        threading.Thread(target=fetch, daemon=True).start()

    def _on_categories_loaded(self, cats):
        if not self.winfo_exists(): return
        self.categories = cats
        names = ["All"] + [c["name"] for c in self.categories]
        self.category_menu.configure(values=names)

    def load_tickets(self):
        """Fetch tickets from the API with current filters and render them."""
        status = self.status_var.get()
        priority = self.priority_var.get()
        category = self.category_var.get()
        search = self.search_entry.get().strip() if hasattr(self, "search_entry") else ""

        # Map "All" to None
        status = None if status == "All" else status
        priority = None if priority == "All" else priority

        category_id = None
        if category != "All":
            for c in self.categories:
                if c["name"] == category:
                    category_id = c["id"]
                    break

        # Clear existing cards and show loading
        for widget in self.ticket_scroll.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.ticket_scroll,
            text="Loading tickets...",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_muted"],
        ).pack(pady=40)

        import threading
        def fetch():
            try:
                tickets = self.api.list_tickets(
                    status=status,
                    priority=priority,
                    category_id=category_id,
                    search=search or None,
                )
                self.after(0, self._render_tickets, tickets)
            except Exception as e:
                self.after(0, self._on_fetch_error, str(e))
                
        threading.Thread(target=fetch, daemon=True).start()

    def _on_fetch_error(self, err_msg):
        if not self.winfo_exists(): return
        messagebox.showerror("Error", f"Failed to load tickets: {err_msg}")
        self._render_tickets([])

    def _apply_sorting(self):
        if not self.winfo_exists(): return
        if hasattr(self, "current_tickets") and self.current_tickets:
            self._render_tickets(self.current_tickets)

    def _render_tickets(self, tickets):
        if not self.winfo_exists(): return
        self.current_tickets = tickets
        
        for widget in self.ticket_scroll.winfo_children():
            widget.destroy()

        self.ticket_count_label.configure(text=f"Tickets ({len(tickets)})")

        if not tickets:
            ctk.CTkLabel(
                self.ticket_scroll,
                text="No tickets found.",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_muted"],
            ).pack(pady=40)
            return

        # Sort logic
        sort_val = self.sort_var.get()
        if sort_val == "Newest First":
            tickets = sorted(tickets, key=lambda t: t.get("id", 0), reverse=True)
        elif sort_val == "Oldest First":
            tickets = sorted(tickets, key=lambda t: t.get("id", 0))
        elif sort_val == "Priority (High-Low)":
            p_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            tickets = sorted(tickets, key=lambda t: p_map.get(t.get("priority", "low"), 0), reverse=True)
        elif sort_val == "Status":
            s_map = {"open": 4, "in_progress": 3, "resolved": 2, "closed": 1}
            tickets = sorted(tickets, key=lambda t: s_map.get(t.get("status", "closed"), 0), reverse=True)

        for ticket in tickets:
            card = TicketCard(
                self.ticket_scroll,
                ticket=ticket,
                on_click=lambda t: self.on_open_ticket(t),
            )
            card.pack(fill="x", pady=(0, 12))
