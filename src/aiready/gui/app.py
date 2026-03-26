"""Main AIReady application window."""
from __future__ import annotations

import customtkinter as ctk
from aiready.gui.theme import WINDOW_WIDTH, WINDOW_HEIGHT
from aiready.i18n.strings import I18n
from aiready.core.logger import InstallLogger
from aiready.platforms.base import Platform


class AIReadyApp(ctk.CTk):
    def __init__(self, platform: Platform, i18n: I18n, preset_tool: str | None = None):
        super().__init__()
        self.platform = platform
        self.i18n = i18n
        self.logger = InstallLogger()
        self.preset_tool = preset_tool
        self.selected_tool = None
        self._current_screen = None

        # Window setup
        self.title("AIReady")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        ctk.set_appearance_mode("system")

        # Container for screens
        self._container = ctk.CTkFrame(self, fg_color="transparent")
        self._container.pack(fill="both", expand=True)

        # Start
        from aiready.gui.screens.language_select import LanguageSelectScreen
        self.show_screen(LanguageSelectScreen)

    def show_screen(self, screen_class, **kwargs):
        if self._current_screen:
            self._current_screen.destroy()
        self._current_screen = screen_class(self._container, app=self, **kwargs)
        self._current_screen.pack(fill="both", expand=True)
