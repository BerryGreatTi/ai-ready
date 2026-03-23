"""Installation complete screen."""
from __future__ import annotations

import sys

import customtkinter as ctk

from aiready.gui.theme import (
    FONT_TITLE, FONT_BODY, FONT_SMALL, FONT_CODE, PADDING, COLOR_SUCCESS,
)


_TOOL_COMMANDS: dict[str, str] = {
    "claude_code": "claude",
    "openclaw": "openclaw",
}


class CompleteScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        tool_id = app.selected_tool or ""
        command = _TOOL_COMMANDS.get(tool_id, tool_id)

        # Spacer
        ctk.CTkLabel(self, text="").pack(pady=30)

        # Success checkmark
        ctk.CTkLabel(
            self, text="✓", font=("", 64, "bold"), text_color=COLOR_SUCCESS,
        ).pack(pady=(0, 10))

        # Title
        ctk.CTkLabel(
            self, text=app.i18n.get("complete.title"), font=FONT_TITLE,
        ).pack(pady=(0, 10))

        # Success message
        tool_name = command
        ctk.CTkLabel(
            self,
            text=app.i18n.get("complete.success", tool=tool_name),
            font=FONT_BODY,
            wraplength=400,
        ).pack(pady=(0, 20))

        # Command hint
        ctk.CTkLabel(
            self, text=app.i18n.get("complete.command_hint"), font=FONT_BODY,
        ).pack(pady=(0, 5))

        # Command box + copy button
        cmd_frame = ctk.CTkFrame(self, fg_color="transparent")
        cmd_frame.pack(pady=(0, 10))

        self._cmd_label = ctk.CTkLabel(
            cmd_frame, text=command, font=FONT_CODE, corner_radius=6,
        )
        self._cmd_label.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            cmd_frame,
            text=app.i18n.get("complete.copy"),
            width=80,
            font=FONT_SMALL,
            command=lambda: self._copy_to_clipboard(command),
        ).pack(side="left")

        # New terminal notice
        ctk.CTkLabel(
            self,
            text=app.i18n.get("complete.new_terminal_notice"),
            font=FONT_SMALL,
            text_color="gray",
            wraplength=400,
        ).pack(pady=(0, 15))

        # Spacer
        ctk.CTkLabel(self, text="").pack(expand=True)

        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(padx=PADDING, pady=PADDING)

        ctk.CTkButton(
            btn_frame,
            text=app.i18n.get("complete.open_terminal"),
            width=160,
            font=FONT_BODY,
            command=self._open_terminal,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame,
            text=app.i18n.get("complete.exit"),
            width=100,
            font=FONT_BODY,
            command=app.destroy,
        ).pack(side="left", padx=8)

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _open_terminal(self):
        import subprocess
        if sys.platform == "win32":
            subprocess.Popen(["cmd.exe"])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Terminal"])
        else:
            # Try common Linux terminals
            for terminal in ("gnome-terminal", "xterm", "konsole", "xfce4-terminal"):
                try:
                    subprocess.Popen([terminal])
                    return
                except FileNotFoundError:
                    continue
