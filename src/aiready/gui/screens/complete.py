"""Installation complete screen."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

import customtkinter as ctk

from aiready.gui.theme import (
    FONT_TITLE, FONT_BODY, FONT_SMALL, FONT_CODE, PADDING,
    COLOR_SUCCESS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_MUTED,
    COLOR_CARD_BG,
)


_TOOL_CONFIGS: dict[str, tuple[str, str]] = {
    # tool_id: (binary_name, launch_args)
    "claude_code": ("claude", ""),
    "openclaw": ("openclaw", "onboard"),
}


def _resolve_command(tool_id: str) -> str:
    """Resolve the tool command to an absolute path with args.

    The GUI process has an updated PATH (from _refresh_path calls during
    install), but a newly opened terminal inherits the system PATH which
    may not include the install directory yet. Using the absolute path
    ensures the command works regardless of the new terminal's PATH.
    """
    binary, args = _TOOL_CONFIGS.get(tool_id, (tool_id, ""))
    absolute = shutil.which(binary)
    base = f'"{absolute}"' if absolute else binary
    return f"{base} {args}".strip()


def _display_command(tool_id: str) -> str:
    """Return the user-facing command string (without absolute path)."""
    binary, args = _TOOL_CONFIGS.get(tool_id, (tool_id, ""))
    return f"{binary} {args}".strip()


def _launch_in_terminal(command: str) -> bool:
    """Open a new terminal window and run the given command inside it."""
    try:
        if sys.platform == "win32":
            subprocess.Popen([
                "powershell", "-NoExit", "-Command", f"& {command}",
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
        self._launch_command = _resolve_command(tool_id)
        self._display_command = _display_command(tool_id)

        # Center content
        self.pack_propagate(False)
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.40, anchor="center")

        # Success icon
        ctk.CTkLabel(
            center, text="✓", font=("", 56, "bold"), text_color=COLOR_SUCCESS,
        ).pack(pady=(0, 12))

        # Title
        ctk.CTkLabel(
            center, text=app.i18n.get("complete.title"), font=FONT_TITLE,
        ).pack(pady=(0, 8))

        # Success message
        ctk.CTkLabel(
            center,
            text=app.i18n.get("complete.success", tool=self._display_command),
            font=FONT_BODY, text_color=COLOR_MUTED,
            wraplength=380,
        ).pack(pady=(0, 28))

        # Command box
        cmd_box = ctk.CTkFrame(center, corner_radius=10, fg_color=COLOR_CARD_BG)
        cmd_box.pack(pady=(0, 8))

        inner = ctk.CTkFrame(cmd_box, fg_color="transparent")
        inner.pack(padx=16, pady=10)

        ctk.CTkLabel(
            inner, text=self._display_command, font=FONT_CODE,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            inner,
            text=app.i18n.get("complete.copy"),
            width=60, height=28,
            font=FONT_SMALL, corner_radius=6,
            fg_color="transparent", border_width=1, border_color=COLOR_MUTED,
            text_color=COLOR_MUTED, hover_color=("gray85", "gray25"),
            command=lambda: self._copy_to_clipboard(self._display_command),
        ).pack(side="left")

        # Notice
        ctk.CTkLabel(
            center,
            text=app.i18n.get("complete.new_terminal_notice"),
            font=FONT_SMALL, text_color=COLOR_MUTED,
            wraplength=380,
        ).pack(pady=(0, 28))

        # Action buttons
        ctk.CTkButton(
            center,
            text=app.i18n.get("complete.launch_tool", tool=self._display_command),
            width=260, height=44,
            font=FONT_BODY, corner_radius=10,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            command=self._launch_tool,
        ).pack(pady=(0, 10))

        ctk.CTkButton(
            center,
            text=app.i18n.get("complete.exit"),
            width=260, height=40,
            font=FONT_BODY, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=COLOR_MUTED,
            text_color=COLOR_MUTED, hover_color=("gray85", "gray25"),
            command=app.destroy,
        ).pack()

        # Auto-launch (once only)
        self.after(500, self._auto_launch)

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _auto_launch(self):
        if not self._launched:
            self._launched = _launch_in_terminal(self._launch_command)

    def _launch_tool(self):
        _launch_in_terminal(self._launch_command)
