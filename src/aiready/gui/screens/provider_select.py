"""AI provider selection screen."""
from __future__ import annotations

import customtkinter as ctk

from aiready.gui.theme import FONT_TITLE, FONT_BODY, FONT_SMALL, PADDING
from aiready.providers.registry import get_providers


_TOP_PRIORITY_THRESHOLD = 3


class ProviderSelectScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._var = ctk.StringVar(value="")

        # Title
        ctk.CTkLabel(
            self, text=app.i18n.get("provider.select.title"), font=FONT_TITLE,
        ).pack(pady=(30, 15))

        # Scrollable list of providers
        scroll = ctk.CTkScrollableFrame(self, height=380)
        scroll.pack(fill="x", padx=PADDING, pady=(0, 10))

        providers = get_providers()
        top = [p for p in providers if p.priority <= _TOP_PRIORITY_THRESHOLD]
        rest = [p for p in providers if p.priority > _TOP_PRIORITY_THRESHOLD]

        for provider in top:
            self._add_provider_row(scroll, provider)

        if rest:
            sep = ctk.CTkFrame(scroll, height=1, fg_color="gray")
            sep.pack(fill="x", pady=8)
            for provider in rest:
                self._add_provider_row(scroll, provider)

        # Spacer
        ctk.CTkLabel(self, text="").pack(expand=True)

        # Navigation
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=PADDING, pady=PADDING)

        ctk.CTkButton(
            nav, text=app.i18n.get("button.back"), width=100,
            command=self._go_back,
        ).pack(side="left")

        self._next_btn = ctk.CTkButton(
            nav, text=app.i18n.get("button.next"), width=100,
            command=self._go_next, state="disabled",
        )
        self._next_btn.pack(side="right")

        # Watch selection
        self._var.trace_add("write", self._on_selection_change)

    def _add_provider_row(self, parent, provider):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)

        radio = ctk.CTkRadioButton(
            row,
            text=self.app.i18n.get(provider.name_key),
            variable=self._var,
            value=provider.id,
            font=FONT_BODY,
        )
        radio.pack(side="left")

        if provider.id == "anthropic":
            badge = ctk.CTkLabel(
                row,
                text=self.app.i18n.get("provider.recommended"),
                font=FONT_SMALL,
                text_color="#3498db",
            )
            badge.pack(side="left", padx=(8, 0))
        elif provider.is_local:
            local_label = ctk.CTkLabel(
                row,
                text=self.app.i18n.get("provider.local_no_key"),
                font=FONT_SMALL,
                text_color="gray",
            )
            local_label.pack(side="left", padx=(8, 0))

    def _on_selection_change(self, *_):
        if self._var.get():
            self._next_btn.configure(state="normal")

    def _go_back(self):
        from aiready.gui.screens.tool_select import ToolSelectScreen
        self.app.show_screen(ToolSelectScreen)

    def _go_next(self):
        provider_id = self._var.get()
        if not provider_id:
            return
        self.app.selected_provider = provider_id
        from aiready.providers.registry import get_provider_by_id
        provider = get_provider_by_id(provider_id)
        # Ollama is local - no API key needed, go straight to onboarding
        if provider and provider.is_local:
            from aiready.gui.screens.onboarding import OnboardingScreen
            self.app.show_screen(OnboardingScreen)
        else:
            from aiready.gui.screens.api_key import ApiKeyScreen
            self.app.show_screen(ApiKeyScreen)
