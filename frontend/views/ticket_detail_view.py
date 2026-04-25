"""Ticket detail view — shows ticket info, comments, and admin controls."""

import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

from config import COLORS
from widgets.status_badge import StatusBadge


class TicketDetailView(ctk.CTkFrame):
    """Full-page ticket detail with comments and admin management controls."""

    def __init__(self, master, api_client, user_data: dict, ticket: dict, on_back):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.api = api_client
        self.user_data = user_data
        self.ticket = ticket
        self.on_back = on_back

        self._build_ui()
        self._load_comments()

    def _build_ui(self):
        # ── Top bar ────────────────────────────────────────────────────────
        topbar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=50)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkButton(
            topbar,
            text="← Back to Dashboard",
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(size=13),
            width=160,
            command=self.on_back,
        ).pack(side="left", padx=12)

        ctk.CTkLabel(
            topbar,
            text=f"Ticket #{self.ticket['id']}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=8)

        # ── Main scrollable content ────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["primary"],
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=12)

        # ── Ticket info card ───────────────────────────────────────────────
        info_card = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12)
        info_card.pack(fill="x", pady=(0, 12))

        # Title
        ctk.CTkLabel(
            info_card,
            text=self.ticket["title"],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
            wraplength=700,
            anchor="w",
            justify="left",
        ).pack(anchor="w", padx=20, pady=(18, 8))

        # Badges row
        badge_row = ctk.CTkFrame(info_card, fg_color="transparent")
        badge_row.pack(anchor="w", padx=20, pady=(0, 8))

        StatusBadge(badge_row, "status", self.ticket["status"]).pack(side="left", padx=(0, 6))
        StatusBadge(badge_row, "priority", self.ticket["priority"]).pack(side="left", padx=(0, 6))

        category_name = "—"
        if self.ticket.get("category"):
            category_name = self.ticket["category"].get("name", "—")
        ctk.CTkLabel(
            badge_row,
            text=f"📁 {category_name}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(8, 0))

        # Description
        ctk.CTkLabel(
            info_card,
            text=self.ticket["description"],
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
            wraplength=700,
            anchor="w",
            justify="left",
        ).pack(anchor="w", padx=20, pady=(4, 12))

        # Meta info row
        meta_row = ctk.CTkFrame(info_card, fg_color="transparent")
        meta_row.pack(fill="x", padx=20, pady=(0, 16))

        creator = self.ticket.get("creator", {}).get("username", "—") if self.ticket.get("creator") else "—"
        assignee = "Unassigned"
        if self.ticket.get("assignee"):
            assignee = self.ticket["assignee"].get("username", "Unassigned")

        created = self.ticket.get("created_at", "")
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            created = dt.strftime("%b %d, %Y %H:%M")
        except Exception:
            pass

        for label_text in [
            f"👤 Created by: {creator}",
            f"🔧 Assigned to: {assignee}",
            f"📅 Created: {created}",
        ]:
            ctk.CTkLabel(
                meta_row,
                text=label_text,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_muted"],
            ).pack(side="left", padx=(0, 20))

        # ── Admin controls ─────────────────────────────────────────────────
        if self.user_data["role"] == "admin":
            self._build_admin_controls(scroll)

        # ── Comments section ───────────────────────────────────────────────
        ctk.CTkLabel(
            scroll,
            text="💬 Comments",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(8, 8))

        self.comments_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.comments_frame.pack(fill="x", pady=(0, 12))

        # ── Add comment ────────────────────────────────────────────────────
        if self.ticket["status"] != "closed":
            add_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=10)
            add_frame.pack(fill="x", pady=(0, 16))

            ctk.CTkLabel(
                add_frame,
                text="Add a comment",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"],
            ).pack(anchor="w", padx=16, pady=(12, 4))

            self.comment_textbox = ctk.CTkTextbox(
                add_frame,
                height=80,
                corner_radius=8,
                fg_color=COLORS["bg_dark"],
                border_color=COLORS["border"],
                border_width=1,
                text_color=COLORS["text_primary"],
                font=ctk.CTkFont(size=13),
            )
            self.comment_textbox.pack(fill="x", padx=16, pady=(0, 8))

            ctk.CTkButton(
                add_frame,
                text="Post Comment",
                height=34,
                corner_radius=8,
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                font=ctk.CTkFont(size=12, weight="bold"),
                command=self._post_comment,
            ).pack(anchor="e", padx=16, pady=(0, 12))

    def _build_admin_controls(self, parent):
        ctrl_card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=10)
        ctrl_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            ctrl_card,
            text="⚙️  Admin Controls",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["primary_light"],
        ).pack(anchor="w", padx=16, pady=(12, 8))

        controls_row = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        controls_row.pack(fill="x", padx=16, pady=(0, 14))

        # Status
        ctk.CTkLabel(
            controls_row, text="Status:", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")
        self.status_var = ctk.StringVar(value=self.ticket["status"])
        ctk.CTkOptionMenu(
            controls_row,
            values=["open", "in_progress", "resolved", "closed"],
            variable=self.status_var,
            width=130,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_hover"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=(4, 16))

        # Priority
        ctk.CTkLabel(
            controls_row, text="Priority:", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")
        self.priority_var = ctk.StringVar(value=self.ticket["priority"])
        ctk.CTkOptionMenu(
            controls_row,
            values=["low", "medium", "high", "critical"],
            variable=self.priority_var,
            width=120,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_hover"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=(4, 16))

        # Assign
        ctk.CTkLabel(
            controls_row, text="Assign to:", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")

        self.users_list: list[dict] = []
        self.assignee_var = ctk.StringVar(value="Unassigned")
        if self.ticket.get("assignee"):
            self.assignee_var.set(self.ticket["assignee"]["username"])

        self.assignee_menu = ctk.CTkOptionMenu(
            controls_row,
            values=["Unassigned"],
            variable=self.assignee_var,
            width=130,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_hover"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
        )
        self.assignee_menu.pack(side="left", padx=(4, 16))

        # Load users for assignment dropdown
        import threading
        def fetch_users():
            try:
                users = self.api.list_users()
                self.after(0, self._on_users_loaded, users)
            except Exception:
                pass
        threading.Thread(target=fetch_users, daemon=True).start()

        # Save button (renamed to Apply Changes)
        ctk.CTkButton(
            controls_row,
            text="✅ Apply Changes",
            height=32,
            width=120,
            corner_radius=6,
            fg_color=COLORS["success"],
            hover_color="#059669",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._save_admin_changes,
        ).pack(side="left", padx=(10, 0))

    def _on_users_loaded(self, users):
        if not self.winfo_exists(): return
        self.users_list = users
        names = ["Unassigned"] + [u["username"] for u in self.users_list]
        self.assignee_menu.configure(values=names)

    # ── Actions ────────────────────────────────────────────────────────────

    def _save_admin_changes(self):
        tid = self.ticket["id"]
        
        # Update status
        new_status = self.status_var.get()
        # Update priority
        new_priority = self.priority_var.get()
        # Update assignee
        assignee_name = self.assignee_var.get()
        new_assignee_id = None
        if assignee_name != "Unassigned":
            for u in self.users_list:
                if u["username"] == assignee_name:
                    new_assignee_id = u["id"]
                    break

        import threading
        def save():
            try:
                if new_status != self.ticket["status"]:
                    self.api.update_ticket_status(tid, new_status)

                if new_priority != self.ticket["priority"]:
                    self.api.update_ticket_priority(tid, new_priority)

                current_assignee_id = self.ticket.get("assignee_id")
                if new_assignee_id != current_assignee_id:
                    self.api.assign_ticket(tid, new_assignee_id)

                # Refresh ticket data
                updated_ticket = self.api.get_ticket(tid)
                self.after(0, self._on_save_success, updated_ticket)
            except Exception as e:
                detail = str(e)
                try:
                    detail = e.response.json().get("detail", detail)
                except Exception:
                    pass
                self.after(0, lambda d=detail: messagebox.showerror("Error", d))
                
        threading.Thread(target=save, daemon=True).start()

    def _on_save_success(self, updated_ticket):
        if not self.winfo_exists(): return
        messagebox.showinfo("Success", "Ticket updated successfully!")
        self.ticket = updated_ticket
        # Re-render the UI so the status badge and other elements update immediately
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
        self._load_comments()

    def _load_comments(self):
        for widget in self.comments_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.comments_frame,
            text="Loading comments...",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"],
        ).pack(pady=8)

        import threading
        def fetch():
            try:
                comments = self.api.list_comments(self.ticket["id"])
            except Exception:
                comments = []
            self.after(0, self._render_comments_list, comments)
            
        threading.Thread(target=fetch, daemon=True).start()

    def _render_comments_list(self, comments):
        if not self.winfo_exists(): return
        for widget in self.comments_frame.winfo_children():
            widget.destroy()

        if not comments:
            ctk.CTkLabel(
                self.comments_frame,
                text="No comments yet.",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_muted"],
            ).pack(pady=8)
            return

        for comment in comments:
            self._render_comment(comment)

    def _render_comment(self, comment: dict):
        card = ctk.CTkFrame(
            self.comments_frame, fg_color=COLORS["bg_card"], corner_radius=8
        )
        card.pack(fill="x", pady=(0, 6))

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(10, 2))

        author = comment.get("author", {}).get("username", "Unknown") if comment.get("author") else "Unknown"
        ctk.CTkLabel(
            header,
            text=f"👤 {author}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["primary_light"],
        ).pack(side="left")

        created = comment.get("created_at", "")
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            created = dt.strftime("%b %d, %Y %H:%M")
        except Exception:
            pass
        ctk.CTkLabel(
            header,
            text=created,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        ).pack(side="right")

        ctk.CTkLabel(
            card,
            text=comment["content"],
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
            wraplength=650,
            anchor="w",
            justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 10))

    def _post_comment(self):
        content = self.comment_textbox.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("Validation", "Comment cannot be empty.")
            return

        import threading
        def post():
            try:
                self.api.create_comment(self.ticket["id"], content)
                self.after(0, self._on_post_success)
            except Exception as e:
                detail = str(e)
                try:
                    detail = e.response.json().get("detail", detail)
                except Exception:
                    pass
                self.after(0, lambda d=detail: messagebox.showerror("Error", d))
                
        threading.Thread(target=post, daemon=True).start()

    def _on_post_success(self):
        if not self.winfo_exists(): return
        self.comment_textbox.delete("1.0", "end")
        self._load_comments()
