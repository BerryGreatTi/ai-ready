"""Installation complete screen."""
from __future__ import annotations

import shutil
import subprocess
import sys

import customtkinter as ctk

from aiready.gui.theme import (
    FONT_TITLE, FONT_BODY, FONT_SMALL, FONT_CODE, PADDING, COLOR_SUCCESS,
)


_TOOL_COMMANDS: dict[str, str] = {
    "claude_code": "claude",
    "openclaw": "openclaw",
}


def _launch_in_terminal(command: str) -> bool:
    """Open a new terminal window and run the given command inside it."""
    try:
        if sys.platform == "win32":
            subprocess.Popen([
                "powershell", "-NoExit", "-Command", command,
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif sys.platform == "darwin":
            escaped = command.replace('\\', '\\\\').replace('"', '\\"')
            apple_script = (
                f'tell application "Terminal"\n'
                f'  do script "{escaped}"\n'
                f'  activate\n'
                f'end tell'
            )
            subprocess.Popen(["osascript", "-e", apple_script])
        else:
            _launch_in_linux_terminal(command)
        return True
    except Exception:
        return False


def _launch_in_linux_terminal(command: str) -> None:
    """Try common Linux terminal emulators with a command."""
    terminals = [
        ("gnome-terminal", ["gnome-terminal", "--", "bash", "-c", f"{command}; exec bash"]),
        ("konsole", ["konsole", "-e", "bash", "-c", f"{command}; exec bash"]),
        ("xfce4-terminal", ["xfce4-terminal", "-e", f"bash -c '{command}; exec bash'"]),
        ("xterm", ["xterm", "-e", f"bash -c '{command}; exec bash'"]),
    ]
    for name, cmd in terminals:
        if shutil.which(name) is None:
            continue
        try:
            subprocess.Popen(cmd)
            return
        except FileNotFoundError:
            continue


class CompleteScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._launched = False

        tool_id = app.selected_tool or ""
        self._command = _TOOL_COMMANDS.get(tool_id, tool_id)

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
        ctk.CTkLabel(
            self,
            text=app.i18n.get("complete.success", tool=self._command),
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
            cmd_frame, text=self._command, font=FONT_CODE, corner_radius=6,
        )
        self._cmd_label.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            cmd_frame,
            text=app.i18n.get("complete.copy"),
            width=80,
            font=FONT_SMALL,
            command=lambda: self._copy_to_clipboard(self._command),
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
            text=app.i18n.get("complete.launch_tool", tool=self._command),
            width=200,
            font=FONT_BODY,
            command=self._launch_tool,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame,
            text=app.i18n.get("complete.exit"),
            width=100,
            font=FONT_BODY,
            command=app.destroy,
        ).pack(side="left", padx=8)

        # Auto-launch
        self.after(500, self._launch_tool)

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _launch_tool(self):
        if self._launched:
            return
        self._launched = _launch_in_terminal(self._command)
