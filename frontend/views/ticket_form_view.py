"""Ticket creation / edit form view."""

import customtkinter as ctk
from tkinter import messagebox

from config import COLORS


class TicketFormView(ctk.CTkFrame):
    def __init__(self, master, api_client, user_data, on_back, ticket=None):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.api = api_client
        self.user_data = user_data
        self.on_back = on_back
        self.ticket = ticket
        self.categories = []
        self._build_ui()

    def _build_ui(self):
        is_edit = self.ticket is not None
        title_text = "Edit Ticket" if is_edit else "Create New Ticket"

        topbar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=50)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkButton(topbar, text="← Back", fg_color="transparent",
                       hover_color=COLORS["bg_hover"], text_color=COLORS["text_secondary"],
                       font=ctk.CTkFont(size=13), width=80, command=self.on_back).pack(side="left", padx=12)
        ctk.CTkLabel(topbar, text=title_text, font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(side="left", padx=8)

        center = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=14, width=560)
        center.pack(pady=40)
        ctk.CTkLabel(center, text="🎫  " + title_text, font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(pady=(28, 20))

        ctk.CTkLabel(center, text="Title *", font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", padx=36)
        self.title_entry = ctk.CTkEntry(center, height=40, corner_radius=8,
            placeholder_text="Brief summary of the issue", fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"], text_color=COLORS["text_primary"], width=480)
        self.title_entry.pack(padx=36, pady=(4, 12))
        if is_edit:
            self.title_entry.insert(0, self.ticket["title"])

        ctk.CTkLabel(center, text="Description *", font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", padx=36)
        self.desc_textbox = ctk.CTkTextbox(center, height=120, corner_radius=8,
            fg_color=COLORS["bg_dark"], border_color=COLORS["border"], border_width=1,
            text_color=COLORS["text_primary"], font=ctk.CTkFont(size=13), width=480)
        self.desc_textbox.pack(padx=36, pady=(4, 12))
        if is_edit:
            self.desc_textbox.insert("1.0", self.ticket["description"])

        ctk.CTkLabel(center, text="Category *", font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", padx=36)
        self.category_var = ctk.StringVar(value="Select category")
        self.category_menu = ctk.CTkOptionMenu(center, values=["Loading..."],
            variable=self.category_var, width=480, fg_color=COLORS["bg_dark"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["bg_card"], dropdown_hover_color=COLORS["bg_hover"],
            dropdown_text_color=COLORS["text_primary"], text_color=COLORS["text_primary"])
        self.category_menu.pack(padx=36, pady=(4, 12))
        self._load_categories()

        ctk.CTkLabel(center, text="Priority", font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", padx=36)
        default_priority = self.ticket["priority"] if is_edit else "medium"
        self.priority_var = ctk.StringVar(value=default_priority)
        ctk.CTkOptionMenu(center, values=["low", "medium", "high", "critical"],
            variable=self.priority_var, width=480, fg_color=COLORS["bg_dark"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["bg_card"], dropdown_hover_color=COLORS["bg_hover"],
            dropdown_text_color=COLORS["text_primary"], text_color=COLORS["text_primary"]
        ).pack(padx=36, pady=(4, 20))

        btn_row = ctk.CTkFrame(center, fg_color="transparent")
        btn_row.pack(pady=(0, 28))
        ctk.CTkButton(btn_row, text="Cancel", width=120, height=40, corner_radius=8,
            fg_color=COLORS["bg_dark"], hover_color=COLORS["bg_hover"], border_width=1,
            border_color=COLORS["border"], text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(size=13), command=self.on_back).pack(side="left", padx=(0, 12))
        ctk.CTkButton(btn_row, text="Update Ticket" if is_edit else "Create Ticket",
            width=180, height=40, corner_radius=8, fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"], font=ctk.CTkFont(size=14, weight="bold"),
            command=self._submit).pack(side="left")

    def _load_categories(self):
        try:
            self.categories = self.api.list_categories()
            names = [c["name"] for c in self.categories]
            self.category_menu.configure(values=names if names else ["No categories"])
            if self.ticket and self.ticket.get("category"):
                self.category_var.set(self.ticket["category"]["name"])
            elif names:
                self.category_var.set(names[0])
        except Exception:
            self.category_menu.configure(values=["Error loading"])

    def _submit(self):
        title = self.title_entry.get().strip()
        description = self.desc_textbox.get("1.0", "end").strip()
        priority = self.priority_var.get()
        category_name = self.category_var.get()
        if not title:
            messagebox.showwarning("Validation", "Title is required.")
            return
        if not description:
            messagebox.showwarning("Validation", "Description is required.")
            return
        category_id = None
        for c in self.categories:
            if c["name"] == category_name:
                category_id = c["id"]
                break
        if not category_id:
            messagebox.showwarning("Validation", "Please select a valid category.")
            return
        try:
            if self.ticket:
                self.api.update_ticket(self.ticket["id"],
                    {"title": title, "description": description,
                     "priority": priority, "category_id": category_id})
                messagebox.showinfo("Success", "Ticket updated!")
            else:
                self.api.create_ticket(title, description, priority, category_id)
                messagebox.showinfo("Success", "Ticket created!")
            self.on_back()
        except Exception as e:
            detail = str(e)
            try:
                detail = e.response.json().get("detail", detail)
            except Exception:
                pass
            messagebox.showerror("Error", detail)
