"""Tool selection screen."""
from __future__ import annotations

import customtkinter as ctk
from aiready.gui.theme import (
    FONT_TITLE, FONT_BODY, FONT_SMALL, PADDING, PADDING_SM, CARD_HEIGHT,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_CARD_BG, COLOR_CARD_BORDER,
    COLOR_CARD_SELECTED, COLOR_MUTED,
)


class ToolSelectScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._selected = None
        self._cards = {}

        # Title
        ctk.CTkLabel(
            self, text=app.i18n.get("tool.select.title"),
            font=FONT_TITLE,
        ).pack(pady=(28, 18))

        # Cards
        for tool_id in ("claude_code", "openclaw"):
            card = self._make_card(tool_id)
            card.pack(fill="x", padx=PADDING, pady=6)
            self._cards[tool_id] = card

        # Spacer
        ctk.CTkLabel(self, text="").pack(expand=True)

        # Navigation
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=PADDING, pady=PADDING)

        ctk.CTkButton(
            nav, text=app.i18n.get("button.back"), width=100, height=40,
            font=FONT_BODY, corner_radius=8,
            fg_color="transparent", border_width=1, border_color=COLOR_MUTED,
            text_color=COLOR_MUTED, hover_color=("gray85", "gray25"),
            command=self._go_back,
        ).pack(side="left")

        self._next_btn = ctk.CTkButton(
            nav, text=app.i18n.get("button.next"), width=100, height=40,
            font=FONT_BODY, corner_radius=8,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            command=self._go_next, state="disabled",
        )
        self._next_btn.pack(side="right")

    def _make_card(self, tool_id: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            self, height=CARD_HEIGHT, corner_radius=12,
            fg_color=COLOR_CARD_BG, border_width=1, border_color=COLOR_CARD_BORDER,
        )
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=14)

        ctk.CTkLabel(
            inner, text=self.app.i18n.get(f"tool.{tool_id}.name"),
            font=("Segoe UI", 15, "bold"), anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner, text=self.app.i18n.get(f"tool.{tool_id}.desc"),
            font=FONT_BODY, anchor="w", text_color=COLOR_MUTED,
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            inner, text=self.app.i18n.get(f"tool.{tool_id}.note"),
            font=FONT_SMALL, anchor="w", text_color=COLOR_MUTED,
        ).pack(anchor="w")

        # Click binding on card and all children
        card.bind("<Button-1>", lambda e, tid=tool_id: self._select_tool(tid))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, tid=tool_id: self._select_tool(tid))
            for grandchild in child.winfo_children():
                grandchild.bind("<Button-1>", lambda e, tid=tool_id: self._select_tool(tid))

        return card

    def _select_tool(self, tool_id: str):
        self._selected = tool_id
        self._next_btn.configure(state="normal")
        for tid, card in self._cards.items():
            if tid == tool_id:
                card.configure(border_width=2, border_color=COLOR_CARD_SELECTED)
            else:
                card.configure(border_width=1, border_color=COLOR_CARD_BORDER)

    def _go_back(self):
        from aiready.gui.screens.language_select import LanguageSelectScreen
        self.app.show_screen(LanguageSelectScreen)

    def _go_next(self):
        if self._selected:
            self.app.selected_tool = self._selected
            from aiready.gui.screens.progress import ProgressScreen
            self.app.show_screen(ProgressScreen)
