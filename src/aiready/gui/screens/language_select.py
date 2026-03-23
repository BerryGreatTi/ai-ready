"""Language selection screen."""
from __future__ import annotations

import customtkinter as ctk
from aiready.gui.theme import FONT_TITLE, FONT_SUBTITLE, FONT_BODY, PADDING, BUTTON_HEIGHT


class LanguageSelectScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Spacer
        ctk.CTkLabel(self, text="").pack(pady=60)

        # Title
        ctk.CTkLabel(self, text="AIReady", font=FONT_TITLE).pack(pady=(0, 10))

        # Subtitle (always bilingual)
        ctk.CTkLabel(
            self,
            text="Select your language / 언어를 선택하세요",
            font=FONT_SUBTITLE,
        ).pack(pady=(0, 40))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame, text="한국어", width=180, height=50,
            font=FONT_BODY, command=lambda: self._select("ko"),
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="English", width=180, height=50,
            font=FONT_BODY, command=lambda: self._select("en"),
        ).pack(side="left", padx=10)

    def _select(self, lang: str):
        self.app.i18n.set_language(lang)
        if self.app.preset_tool:
            self.app.selected_tool = self.app.preset_tool
            from aiready.gui.screens.progress import ProgressScreen
            self.app.show_screen(ProgressScreen)
        else:
            from aiready.gui.screens.tool_select import ToolSelectScreen
            self.app.show_screen(ToolSelectScreen)
