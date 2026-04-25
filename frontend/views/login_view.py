"""Login view — the first screen users see."""

import customtkinter as ctk
from tkinter import messagebox

from config import COLORS, APP_TITLE


class LoginView(ctk.CTkFrame):
    """Login form with username/password fields."""

    def __init__(self, master, api_client, on_login_success, on_show_register):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.api = api_client
        self.on_login_success = on_login_success
        self.on_show_register = on_show_register

        self._build_ui()

    def _build_ui(self):
        # Center container
        center = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=16, width=420)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / Title
        ctk.CTkLabel(
            center,
            text="🎫",
            font=ctk.CTkFont(size=48),
        ).pack(pady=(40, 4))

        ctk.CTkLabel(
            center,
            text=APP_TITLE,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            center,
            text="Sign in to your account",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).pack(pady=(0, 28))

        # Username
        ctk.CTkLabel(
            center,
            text="Username",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(fill="x", padx=40)

        self.username_entry = ctk.CTkEntry(
            center,
            height=40,
            corner_radius=8,
            placeholder_text="Enter your username",
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
        )
        self.username_entry.pack(fill="x", padx=40, pady=(4, 14))

        # Password
        ctk.CTkLabel(
            center,
            text="Password",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(fill="x", padx=40)

        self.password_entry = ctk.CTkEntry(
            center,
            height=40,
            corner_radius=8,
            show="•",
            placeholder_text="Enter your password",
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
        )
        self.password_entry.pack(fill="x", padx=40, pady=(4, 24))
        self.password_entry.bind("<Return>", lambda e: self._do_login())

        # Login button
        self.login_btn = ctk.CTkButton(
            center,
            text="Sign In",
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._do_login,
        )
        self.login_btn.pack(fill="x", padx=40, pady=(0, 14))

        # Register link
        reg_frame = ctk.CTkFrame(center, fg_color="transparent")
        reg_frame.pack(pady=(0, 32))

        ctk.CTkLabel(
            reg_frame,
            text="Don't have an account?",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        ).pack(side="left")

        ctk.CTkButton(
            reg_frame,
            text="Sign Up",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["primary_light"],
            width=60,
            height=28,
            command=self.on_show_register,
        ).pack(side="left", padx=(4, 0))

    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Validation", "Please enter both username and password.")
            return

        try:
            self.api.login(username, password)
            user_data = self.api.get_me()
            self.on_login_success(user_data)
        except Exception as e:
            detail = "Invalid username or password"
            try:
                detail = e.response.json().get("detail", detail)
            except Exception:
                pass
            messagebox.showerror("Login Failed", detail)
