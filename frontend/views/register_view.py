"""Register view — new user sign-up form."""

import customtkinter as ctk
from tkinter import messagebox

from config import COLORS, APP_TITLE


class RegisterView(ctk.CTkFrame):
    """Registration form with username, email, password fields."""

    def __init__(self, master, api_client, on_register_success, on_show_login):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.api = api_client
        self.on_register_success = on_register_success
        self.on_show_login = on_show_login

        self._build_ui()

    def _build_ui(self):
        center = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=16, width=420)
        center.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            center, text="📝", font=ctk.CTkFont(size=48),
        ).pack(pady=(36, 4))

        ctk.CTkLabel(
            center,
            text="Create Account",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            center,
            text="Sign up to start submitting tickets",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(pady=(0, 24))

        # Username
        ctk.CTkLabel(
            center, text="Username", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"], anchor="w",
        ).pack(fill="x", padx=40)
        self.username_entry = ctk.CTkEntry(
            center, height=38, corner_radius=8,
            placeholder_text="Choose a username",
            fg_color=COLORS["bg_dark"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
        )
        self.username_entry.pack(fill="x", padx=40, pady=(4, 10))

        # Email
        ctk.CTkLabel(
            center, text="Email", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"], anchor="w",
        ).pack(fill="x", padx=40)
        self.email_entry = ctk.CTkEntry(
            center, height=38, corner_radius=8,
            placeholder_text="your@email.com",
            fg_color=COLORS["bg_dark"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
        )
        self.email_entry.pack(fill="x", padx=40, pady=(4, 10))

        # Password
        ctk.CTkLabel(
            center, text="Password", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"], anchor="w",
        ).pack(fill="x", padx=40)
        self.password_entry = ctk.CTkEntry(
            center, height=38, corner_radius=8, show="•",
            placeholder_text="Minimum 6 characters",
            fg_color=COLORS["bg_dark"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
        )
        self.password_entry.pack(fill="x", padx=40, pady=(4, 22))
        self.password_entry.bind("<Return>", lambda e: self._do_register())

        # Register button
        ctk.CTkButton(
            center,
            text="Create Account",
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#059669",
            command=self._do_register,
        ).pack(fill="x", padx=40, pady=(0, 14))

        # Back to login
        back_frame = ctk.CTkFrame(center, fg_color="transparent")
        back_frame.pack(pady=(0, 28))

        ctk.CTkLabel(
            back_frame, text="Already have an account?",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
        ).pack(side="left")

        ctk.CTkButton(
            back_frame, text="Sign In", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent", hover_color=COLORS["bg_hover"],
            text_color=COLORS["primary_light"], width=60, height=28,
            command=self.on_show_login,
        ).pack(side="left", padx=(4, 0))

    def _do_register(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not email or not password:
            messagebox.showwarning("Validation", "All fields are required.")
            return
        if len(password) < 6:
            messagebox.showwarning("Validation", "Password must be at least 6 characters.")
            return

        try:
            self.api.register(username, email, password)
            messagebox.showinfo("Success", "Account created! You can now sign in.")
            self.on_register_success()
        except Exception as e:
            detail = "Registration failed"
            try:
                detail = e.response.json().get("detail", detail)
            except Exception:
                pass
            messagebox.showerror("Error", detail)
