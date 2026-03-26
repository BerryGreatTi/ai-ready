"""Onboarding screen for OpenClaw automatic onboarding."""
from __future__ import annotations

import threading

import customtkinter as ctk

from aiready.gui.theme import (
    FONT_TITLE, FONT_BODY, FONT_SMALL, PADDING,
    COLOR_SUCCESS, COLOR_ERROR,
)


class OnboardingScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build_automatic()

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

    def _go_back(self):
        from aiready.gui.screens.progress import ProgressScreen
        self.app.show_screen(ProgressScreen)

    def _go_complete(self):
        from aiready.gui.screens.complete import CompleteScreen
        self.app.show_screen(CompleteScreen)
