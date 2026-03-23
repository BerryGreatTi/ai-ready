"""Onboarding screen handling both Claude Code (guided) and OpenClaw (automatic)."""
from __future__ import annotations

import subprocess
import threading

import customtkinter as ctk

from aiready.gui.theme import (
    FONT_TITLE, FONT_BODY, FONT_SMALL, PADDING,
    COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING,
)


class OnboardingScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        if app.selected_tool == "claude_code":
            self._build_guided()
        else:
            self._build_automatic()

    # --- Claude Code: Guided onboarding ---

    def _build_guided(self):
        # Title
        ctk.CTkLabel(
            self, text=self.app.i18n.get("auth.title"), font=FONT_TITLE,
        ).pack(pady=(30, 15))

        # Subscription warning
        warning_frame = ctk.CTkFrame(self, corner_radius=8, fg_color="#4a3a00")
        warning_frame.pack(fill="x", padx=PADDING, pady=(0, 15))
        ctk.CTkLabel(
            warning_frame,
            text=self.app.i18n.get("auth.subscription_warning"),
            font=FONT_SMALL,
            text_color=COLOR_WARNING,
            wraplength=400,
        ).pack(padx=12, pady=8)

        # Numbered steps
        steps_frame = ctk.CTkFrame(self, fg_color="transparent")
        steps_frame.pack(fill="x", padx=PADDING, pady=(0, 15))

        for i, key in enumerate(("auth.step1", "auth.step2", "auth.step3"), start=1):
            row = ctk.CTkFrame(steps_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"{i}.", width=25, font=FONT_BODY).pack(side="left")
            ctk.CTkLabel(
                row, text=self.app.i18n.get(key), font=FONT_BODY, anchor="w",
            ).pack(side="left", fill="x", expand=True)

        # Open Browser button
        ctk.CTkButton(
            self,
            text=self.app.i18n.get("auth.open_browser"),
            width=200,
            font=FONT_BODY,
            command=self._open_browser,
        ).pack(pady=(0, 10))

        # Verify authentication button
        self._verify_result = ctk.CTkLabel(self, text="", font=FONT_SMALL)
        self._verify_result.pack(pady=(0, 5))

        ctk.CTkButton(
            self,
            text=self.app.i18n.get("auth.verify"),
            width=200,
            font=FONT_BODY,
            command=self._verify_auth,
        ).pack(pady=(0, 10))

        # Spacer
        ctk.CTkLabel(self, text="").pack(expand=True)

        # Navigation
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=PADDING, pady=PADDING)

        ctk.CTkButton(
            nav, text=self.app.i18n.get("button.back"), width=100,
            command=self._go_back,
        ).pack(side="left")

        self._next_btn = ctk.CTkButton(
            nav, text=self.app.i18n.get("button.next"), width=100,
            command=self._go_complete, state="disabled",
        )
        self._next_btn.pack(side="right")

    def _open_browser(self):
        self.app.platform.open_browser("https://claude.ai/login")

    def _verify_auth(self):
        self._verify_result.configure(
            text="Checking...", text_color="gray",
        )
        self.update_idletasks()
        result = self.app.platform.run_command(["claude", "--version"])
        if result.succeeded:
            self._verify_result.configure(
                text=self.app.i18n.get("apikey.valid"), text_color=COLOR_SUCCESS,
            )
            self._next_btn.configure(state="normal")
        else:
            self._verify_result.configure(
                text=self.app.i18n.get("error.verification_failed"),
                text_color=COLOR_ERROR,
            )

    def _go_back(self):
        from aiready.gui.screens.progress import ProgressScreen
        self.app.show_screen(ProgressScreen)

    def _go_complete(self):
        from aiready.gui.screens.complete import CompleteScreen
        self.app.show_screen(CompleteScreen)

    # --- OpenClaw: Automatic onboarding ---

    def _build_automatic(self):
        # Title
        ctk.CTkLabel(
            self, text=self.app.i18n.get("step.run_onboarding"), font=FONT_TITLE,
        ).pack(pady=(30, 20))

        # Status label
        self._auto_status = ctk.CTkLabel(
            self,
            text=self.app.i18n.get("progress.status.running"),
            font=FONT_BODY,
            text_color="gray",
        )
        self._auto_status.pack(pady=(0, 10))

        # Progress bar (indeterminate-style)
        self._auto_progress = ctk.CTkProgressBar(self, width=400, mode="indeterminate")
        self._auto_progress.pack(pady=(0, 10), padx=PADDING)
        self._auto_progress.start()

        # Error area (hidden initially)
        self._auto_error = ctk.CTkLabel(
            self, text="", font=FONT_SMALL, text_color=COLOR_ERROR, wraplength=400,
        )
        self._auto_error.pack(pady=(0, 5))

        # Spacer
        ctk.CTkLabel(self, text="").pack(expand=True)

        # Navigation (back only; next appears on completion)
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=PADDING, pady=PADDING)

        ctk.CTkButton(
            nav, text=self.app.i18n.get("button.back"), width=100,
            command=self._go_back,
        ).pack(side="left")

        self._auto_next = ctk.CTkButton(
            nav, text=self.app.i18n.get("button.next"), width=100,
            command=self._go_complete, state="disabled",
        )
        self._auto_next.pack(side="right")

        # Start background onboarding
        thread = threading.Thread(target=self._run_automatic, daemon=True)
        thread.start()

    def _run_automatic(self):
        result = self.app.platform.run_command(
            ["openclaw", "onboard", "--install-daemon"],
        )
        self.app.after(0, lambda: self._on_automatic_done(result))

    def _on_automatic_done(self, result):
        self._auto_progress.stop()
        if result.succeeded:
            self._auto_status.configure(
                text=self.app.i18n.get("progress.status.done"),
                text_color=COLOR_SUCCESS,
            )
            self._auto_next.configure(state="normal")
        else:
            self._auto_status.configure(
                text=self.app.i18n.get("progress.status.failed"),
                text_color=COLOR_ERROR,
            )
            self._auto_error.configure(
                text=result.stderr or self.app.i18n.get("error.verification_failed"),
            )
