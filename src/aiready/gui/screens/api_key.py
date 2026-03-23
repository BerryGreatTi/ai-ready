"""API key input screen."""
from __future__ import annotations

import webbrowser

import customtkinter as ctk

from aiready.gui.theme import (
    FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_SMALL, PADDING,
    COLOR_SUCCESS, COLOR_ERROR,
)
from aiready.providers.registry import get_provider_by_id


_KEY_PREFIXES: dict[str, str] = {
    "anthropic": "sk-ant-",
    "openai": "sk-",
    "gemini": "AIza",
    "mistral": "",
    "cohere": "",
}


class ApiKeyScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._show_key = False

        provider_id = app.selected_provider or ""
        self._provider = get_provider_by_id(provider_id)
        provider_name = (
            app.i18n.get(self._provider.name_key) if self._provider else provider_id
        )

        # Title
        ctk.CTkLabel(self, text=app.i18n.get("apikey.title"), font=FONT_TITLE).pack(
            pady=(30, 5)
        )

        # Provider name subtitle
        ctk.CTkLabel(self, text=provider_name, font=FONT_SUBTITLE).pack(pady=(0, 10))

        # Prompt
        ctk.CTkLabel(
            self, text=app.i18n.get("apikey.prompt"), font=FONT_BODY,
        ).pack(pady=(0, 15))

        # Key entry + show/hide toggle
        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(fill="x", padx=PADDING, pady=(0, 8))

        self._entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text=app.i18n.get("apikey.paste"),
            show="*",
            font=FONT_BODY,
        )
        self._entry.pack(side="left", fill="x", expand=True)

        self._toggle_btn = ctk.CTkButton(
            entry_frame,
            text=app.i18n.get("apikey.show"),
            width=70,
            font=FONT_SMALL,
            command=self._toggle_show,
        )
        self._toggle_btn.pack(side="left", padx=(8, 0))

        # Paste button
        ctk.CTkButton(
            self,
            text=app.i18n.get("apikey.paste"),
            width=200,
            font=FONT_BODY,
            command=self._paste_from_clipboard,
        ).pack(pady=(0, 8))

        # Get API key link (only if provider has a URL)
        if self._provider and self._provider.api_key_url:
            ctk.CTkButton(
                self,
                text=app.i18n.get("apikey.get_key"),
                font=FONT_SMALL,
                fg_color="transparent",
                text_color="#3498db",
                hover=False,
                command=self._open_api_key_url,
            ).pack(pady=(0, 8))

        # Validate button
        ctk.CTkButton(
            self,
            text=app.i18n.get("apikey.validate"),
            width=200,
            font=FONT_BODY,
            command=self._validate,
        ).pack(pady=(0, 5))

        # Validation result label
        self._validation_label = ctk.CTkLabel(
            self, text="", font=FONT_SMALL,
        )
        self._validation_label.pack(pady=(0, 10))

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

    def _toggle_show(self):
        self._show_key = not self._show_key
        if self._show_key:
            self._entry.configure(show="")
            self._toggle_btn.configure(text=self.app.i18n.get("apikey.hide"))
        else:
            self._entry.configure(show="*")
            self._toggle_btn.configure(text=self.app.i18n.get("apikey.show"))

    def _paste_from_clipboard(self):
        try:
            text = self.clipboard_get()
            self._entry.delete(0, "end")
            self._entry.insert(0, text.strip())
        except Exception:
            pass

    def _open_api_key_url(self):
        if self._provider and self._provider.api_key_url:
            webbrowser.open(self._provider.api_key_url)

    def _validate(self):
        key = self._entry.get().strip()
        if not key:
            self._validation_label.configure(
                text=self.app.i18n.get("apikey.invalid"),
                text_color=COLOR_ERROR,
            )
            self._next_btn.configure(state="disabled")
            return

        provider_id = self.app.selected_provider or ""
        prefix = _KEY_PREFIXES.get(provider_id, "")
        if prefix and not key.startswith(prefix):
            self._validation_label.configure(
                text=self.app.i18n.get("apikey.invalid"),
                text_color=COLOR_ERROR,
            )
            self._next_btn.configure(state="disabled")
            return

        self._validation_label.configure(
            text=self.app.i18n.get("apikey.valid"),
            text_color=COLOR_SUCCESS,
        )
        self.app.api_key = key
        self._next_btn.configure(state="normal")

    def _go_back(self):
        from aiready.gui.screens.provider_select import ProviderSelectScreen
        self.app.show_screen(ProviderSelectScreen)

    def _go_next(self):
        from aiready.gui.screens.onboarding import OnboardingScreen
        self.app.show_screen(OnboardingScreen)
