"""Admin panel view — user management and category management."""

import customtkinter as ctk
from tkinter import messagebox

from config import COLORS


class AdminPanelView(ctk.CTkFrame):
    def __init__(self, master, api_client, user_data, on_back):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.api = api_client
        self.user_data = user_data
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self):
        topbar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=50)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkButton(topbar, text="← Back to Dashboard", fg_color="transparent",
                       hover_color=COLORS["bg_hover"], text_color=COLORS["text_secondary"],
                       font=ctk.CTkFont(size=13), width=160, command=self.on_back
                       ).pack(side="left", padx=12)
        ctk.CTkLabel(topbar, text="⚙️  Admin Panel", font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(side="left", padx=8)

        # Tab view
        self.tabview = ctk.CTkTabview(self, fg_color=COLORS["bg_card"], corner_radius=12,
            segmented_button_fg_color=COLORS["bg_dark"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_hover"],
            segmented_button_unselected_color=COLORS["bg_dark"],
            segmented_button_unselected_hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"])
        self.tabview.pack(fill="both", expand=True, padx=20, pady=12)

        self.tabview.add("Users")
        self.tabview.add("Categories")

        self._build_users_tab(self.tabview.tab("Users"))
        self._build_categories_tab(self.tabview.tab("Categories"))

    # ── Users Tab ──────────────────────────────────────────────────────────

    def _build_users_tab(self, parent):
        self.users_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["primary"])
        self.users_scroll.pack(fill="both", expand=True, padx=8, pady=8)
        self._load_users()

    def _load_users(self):
        for w in self.users_scroll.winfo_children():
            w.destroy()
            
        ctk.CTkLabel(self.users_scroll, text="Loading users...", text_color=COLORS["text_muted"]).pack(pady=20)

        import threading
        def fetch():
            try:
                users = self.api.list_users()
                self.after(0, self._render_users, users)
            except Exception:
                self.after(0, self._render_users, None)
        threading.Thread(target=fetch, daemon=True).start()

    def _render_users(self, users):
        for w in self.users_scroll.winfo_children():
            w.destroy()

        if users is None:
            ctk.CTkLabel(self.users_scroll, text="Failed to load users.",
                         text_color=COLORS["danger"]).pack(pady=20)
            return

        # Header
        hdr = ctk.CTkFrame(self.users_scroll, fg_color=COLORS["bg_dark"], corner_radius=6, height=36)
        hdr.pack(fill="x", pady=(0, 6))
        hdr.pack_propagate(False)
        for text, w in [("Username", 150), ("Email", 200), ("Role", 100), ("Status", 80), ("Actions", 200)]:
            ctk.CTkLabel(hdr, text=text, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=COLORS["text_muted"], width=w).pack(side="left", padx=4)

        for user in users:
            self._render_user_row(user)

    def _render_user_row(self, user):
        row = ctk.CTkFrame(self.users_scroll, fg_color=COLORS["bg_card"], corner_radius=6, height=40)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)

        ctk.CTkLabel(row, text=user["username"], font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_primary"], width=150, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(row, text=user["email"], font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_secondary"], width=200, anchor="w").pack(side="left", padx=4)

        role_color = COLORS["primary"] if user["role"] == "admin" else COLORS["text_muted"]
        ctk.CTkLabel(row, text=user["role"].upper(), font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=role_color, width=100).pack(side="left", padx=4)

        status_color = COLORS["success"] if user["is_active"] else COLORS["danger"]
        ctk.CTkLabel(row, text="Active" if user["is_active"] else "Inactive",
                     font=ctk.CTkFont(size=11), text_color=status_color, width=80).pack(side="left", padx=4)

        if user["id"] != self.user_data["id"]:
            actions = ctk.CTkFrame(row, fg_color="transparent", width=200)
            actions.pack(side="left", padx=4)
            new_role = "admin" if user["role"] == "user" else "user"
            ctk.CTkButton(actions, text=f"Make {new_role.title()}", width=100, height=28,
                corner_radius=6, font=ctk.CTkFont(size=11), fg_color=COLORS["secondary"],
                hover_color="#0284C7",
                command=lambda uid=user["id"], r=new_role: self._change_role(uid, r)
            ).pack(side="left", padx=(0, 4))

            toggle_text = "Deactivate" if user["is_active"] else "Activate"
            toggle_color = COLORS["danger"] if user["is_active"] else COLORS["success"]
            ctk.CTkButton(actions, text=toggle_text, width=90, height=28, corner_radius=6,
                font=ctk.CTkFont(size=11), fg_color=toggle_color,
                command=lambda uid=user["id"], a=not user["is_active"]: self._toggle_active(uid, a)
            ).pack(side="left")

    def _change_role(self, user_id, new_role):
        import threading
        def update():
            try:
                self.api.update_user_role(user_id, new_role)
                self.after(0, self._load_users)
            except Exception as e:
                self.after(0, lambda err=e: messagebox.showerror("Error", str(err)))
        threading.Thread(target=update, daemon=True).start()

    def _toggle_active(self, user_id, is_active):
        import threading
        def update():
            try:
                self.api.update_user_active(user_id, is_active)
                self.after(0, self._load_users)
            except Exception as e:
                self.after(0, lambda err=e: messagebox.showerror("Error", str(err)))
        threading.Thread(target=update, daemon=True).start()

    # ── Categories Tab ─────────────────────────────────────────────────────

    def _build_categories_tab(self, parent):
        # Add form
        add_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_dark"], corner_radius=8)
        add_frame.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(add_frame, text="Add Category", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=12, pady=(8, 4))

        form_row = ctk.CTkFrame(add_frame, fg_color="transparent")
        form_row.pack(fill="x", padx=12, pady=(0, 10))
        self.cat_name_entry = ctk.CTkEntry(form_row, height=34, width=200, corner_radius=6,
            placeholder_text="Category name", fg_color=COLORS["bg_card"],
            border_color=COLORS["border"], text_color=COLORS["text_primary"])
        self.cat_name_entry.pack(side="left", padx=(0, 8))
        self.cat_desc_entry = ctk.CTkEntry(form_row, height=34, width=280, corner_radius=6,
            placeholder_text="Description (optional)", fg_color=COLORS["bg_card"],
            border_color=COLORS["border"], text_color=COLORS["text_primary"])
        self.cat_desc_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(form_row, text="Add", width=70, height=34, corner_radius=6,
            fg_color=COLORS["success"], hover_color="#059669",
            font=ctk.CTkFont(size=12, weight="bold"), command=self._add_category).pack(side="left")

        self.cats_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["primary"])
        self.cats_scroll.pack(fill="both", expand=True, padx=8, pady=4)
        self._load_categories()

    def _load_categories(self):
        for w in self.cats_scroll.winfo_children():
            w.destroy()
            
        ctk.CTkLabel(self.cats_scroll, text="Loading categories...", text_color=COLORS["text_muted"]).pack(pady=20)

        import threading
        def fetch():
            try:
                categories = self.api.list_categories()
                self.after(0, self._render_categories, categories)
            except Exception:
                self.after(0, self._render_categories, None)
        threading.Thread(target=fetch, daemon=True).start()

    def _render_categories(self, categories):
        for w in self.cats_scroll.winfo_children():
            w.destroy()

        if categories is None:
            ctk.CTkLabel(self.cats_scroll, text="Failed to load.", text_color=COLORS["danger"]).pack(pady=20)
            return

        for cat in categories:
            row = ctk.CTkFrame(self.cats_scroll, fg_color=COLORS["bg_card"], corner_radius=6, height=40)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=cat["name"], font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=COLORS["text_primary"], width=200, anchor="w").pack(side="left", padx=12)
            ctk.CTkLabel(row, text=cat.get("description") or "—", font=ctk.CTkFont(size=12),
                         text_color=COLORS["text_secondary"], anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(row, text="🗑️", width=36, height=28, corner_radius=6,
                fg_color=COLORS["danger"], hover_color="#DC2626",
                command=lambda cid=cat["id"]: self._delete_category(cid)).pack(side="right", padx=12)

    def _add_category(self):
        name = self.cat_name_entry.get().strip()
        desc = self.cat_desc_entry.get().strip() or None
        if not name:
            messagebox.showwarning("Validation", "Category name is required.")
            return
            
        import threading
        def add():
            try:
                self.api.create_category(name, desc)
                self.after(0, self._on_add_success)
            except Exception as e:
                detail = str(e)
                try:
                    detail = e.response.json().get("detail", detail)
                except Exception:
                    pass
                self.after(0, lambda d=detail: messagebox.showerror("Error", d))
        threading.Thread(target=add, daemon=True).start()

    def _on_add_success(self):
        self.cat_name_entry.delete(0, "end")
        self.cat_desc_entry.delete(0, "end")
        self._load_categories()

    def _delete_category(self, category_id):
        if not messagebox.askyesno("Confirm", "Delete this category?"):
            return
            
        import threading
        def delete():
            try:
                self.api.delete_category(category_id)
                self.after(0, self._load_categories)
            except Exception as e:
                detail = str(e)
                try:
                    detail = e.response.json().get("detail", detail)
                except Exception:
                    pass
                self.after(0, lambda d=detail: messagebox.showerror("Error", d))
        threading.Thread(target=delete, daemon=True).start()
