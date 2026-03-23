"""Tool selection screen."""
from __future__ import annotations

import customtkinter as ctk
from aiready.gui.theme import FONT_TITLE, FONT_BODY, FONT_SMALL, PADDING, CARD_HEIGHT


class ToolSelectScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._selected = None
        self._cards = {}

        # Title
        ctk.CTkLabel(self, text=app.i18n.get("tool.select.title"), font=FONT_TITLE).pack(pady=(30, 20))

        # Cards
        for tool_id in ("claude_code", "openclaw"):
            card = self._make_card(tool_id)
            card.pack(fill="x", padx=PADDING, pady=8)
            self._cards[tool_id] = card

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

    def _make_card(self, tool_id: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(self, height=CARD_HEIGHT, corner_radius=10)
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(
            inner, text=self.app.i18n.get(f"tool.{tool_id}.name"),
            font=("", 16, "bold"), anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner, text=self.app.i18n.get(f"tool.{tool_id}.desc"),
            font=FONT_BODY, anchor="w", text_color="gray",
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner, text=self.app.i18n.get(f"tool.{tool_id}.note"),
            font=FONT_SMALL, anchor="w", text_color="gray",
        ).pack(anchor="w")

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
                card.configure(border_width=2, border_color="#3498db")
            else:
                card.configure(border_width=0)

    def _go_back(self):
        from aiready.gui.screens.language_select import LanguageSelectScreen
        self.app.show_screen(LanguageSelectScreen)

    def _go_next(self):
        if self._selected:
            self.app.selected_tool = self._selected
            from aiready.gui.screens.progress import ProgressScreen
            self.app.show_screen(ProgressScreen)
