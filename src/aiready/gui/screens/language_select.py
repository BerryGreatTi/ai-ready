"""Language selection screen."""
from __future__ import annotations

import customtkinter as ctk
from aiready.gui.theme import (
    FONT_HERO, FONT_SUBTITLE, FONT_BODY, PADDING,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_MUTED,
)


class LanguageSelectScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Center content vertically
        self.pack_propagate(False)
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.40, anchor="center")

        # Brand
        ctk.CTkLabel(
            center, text="AIReady", font=FONT_HERO, text_color=COLOR_PRIMARY,
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            center, text="AI Tool Setup Helper",
            font=FONT_SUBTITLE, text_color=COLOR_MUTED,
        ).pack(pady=(0, 36))

        # Language prompt
        ctk.CTkLabel(
            center,
            text="Select your language / \uc5b8\uc5b4\ub97c \uc120\ud0dd\ud558\uc138\uc694",
            font=FONT_BODY, text_color=COLOR_MUTED,
        ).pack(pady=(0, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(center, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(
            btn_frame, text="\ud55c\uad6d\uc5b4", width=190, height=48,
            font=FONT_BODY, corner_radius=10,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            command=lambda: self._select("ko"),
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame, text="English", width=190, height=48,
            font=FONT_BODY, corner_radius=10,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            command=lambda: self._select("en"),
        ).pack(side="left", padx=8)

    def _select(self, lang: str):
        self.app.i18n.set_language(lang)
        if self.app.preset_tool:
            self.app.selected_tool = self.app.preset_tool
            from aiready.gui.screens.progress import ProgressScreen
            self.app.show_screen(ProgressScreen)
        else:
            from aiready.gui.screens.tool_select import ToolSelectScreen
            self.app.show_screen(ToolSelectScreen)
