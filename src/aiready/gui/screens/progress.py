"""Installation progress screen."""
from __future__ import annotations

import subprocess
import threading

import customtkinter as ctk

from aiready.core.installer import Installer
from aiready.core.models import Step, StepResult, StepStatus
from aiready.gui.theme import (
    FONT_TITLE, FONT_BODY, FONT_SMALL, PADDING, PADDING_SM,
    COLOR_SUCCESS, COLOR_ERROR, COLOR_RUNNING, COLOR_MUTED,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_CARD_BG,
)
from aiready.tools.claude_code import ClaudeCodeTool
from aiready.tools.openclaw import OpenClawTool


class ProgressScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._step_labels = []
        self._step_statuses = []

        # Create tool
        if app.selected_tool == "claude_code":
            self._tool = ClaudeCodeTool(app.platform, app.i18n, app.logger)
        else:
            self._tool = OpenClawTool(app.platform, app.i18n, app.logger)

        # Get steps for display
        self._steps = self._tool.get_steps(app.platform)

        # Title
        tool_name = self._tool.get_name()
        ctk.CTkLabel(
            self, text=f"{app.i18n.get('progress.title')}",
            font=FONT_TITLE,
        ).pack(pady=(30, 4))

        ctk.CTkLabel(
            self, text=tool_name,
            font=FONT_SMALL, text_color=COLOR_MUTED,
        ).pack(pady=(0, 20))

        # Step list
        step_container = ctk.CTkFrame(
            self, corner_radius=12, fg_color=COLOR_CARD_BG,
        )
        step_container.pack(fill="x", padx=PADDING, pady=(0, 16))

        for i, step in enumerate(self._steps):
            row = ctk.CTkFrame(step_container, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=6)

            status_label = ctk.CTkLabel(
                row, text="○", width=24, font=FONT_BODY, text_color=COLOR_MUTED,
            )
            status_label.pack(side="left")
            self._step_statuses.append(status_label)

            name_label = ctk.CTkLabel(
                row,
                text=app.i18n.get(step.name_key, tool=tool_name),
                font=FONT_BODY, anchor="w",
            )
            name_label.pack(side="left", padx=(8, 0), fill="x", expand=True)
            self._step_labels.append(name_label)

        # Progress bar
        self._progress = ctk.CTkProgressBar(
            self, width=400, height=6, corner_radius=3,
            progress_color=COLOR_PRIMARY,
        )
        self._progress.pack(pady=(4, 6), padx=PADDING)
        self._progress.set(0)

        # Status text
        self._status_text = ctk.CTkLabel(
            self, text="", font=FONT_SMALL, text_color=COLOR_MUTED,
        )
        self._status_text.pack(pady=(0, 8))

        # Error frame (hidden initially)
        self._error_frame = ctk.CTkFrame(self, fg_color="transparent")

        self._error_msg = ctk.CTkLabel(
            self._error_frame, text="", font=FONT_BODY, text_color=COLOR_ERROR,
            wraplength=400,
        )
        self._error_msg.pack(pady=5)

        err_buttons = ctk.CTkFrame(self._error_frame, fg_color="transparent")
        err_buttons.pack(pady=5)

        ctk.CTkButton(
            err_buttons, text=app.i18n.get("button.retry"), width=100, height=36,
            font=FONT_BODY, corner_radius=8,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            command=self._retry,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            err_buttons, text=app.i18n.get("button.view_log"), width=100, height=36,
            font=FONT_BODY, corner_radius=8,
            fg_color="transparent", border_width=1, border_color=COLOR_MUTED,
            text_color=COLOR_MUTED, hover_color=("gray85", "gray25"),
            command=self._view_log,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            err_buttons, text=app.i18n.get("button.exit"), width=100, height=36,
            font=FONT_BODY, corner_radius=8,
            fg_color="transparent", border_width=1, border_color=COLOR_MUTED,
            text_color=COLOR_MUTED, hover_color=("gray85", "gray25"),
            command=self.app.destroy,
        ).pack(side="left", padx=5)

        # Start installation
        self._start_install()

    def _start_install(self):
        self._error_frame.pack_forget()
        installer = Installer(
            platform=self.app.platform,
            tool=self._tool,
            i18n=self.app.i18n,
            logger=self.app.logger,
        )
        thread = threading.Thread(target=self._run_install, args=(installer,), daemon=True)
        thread.start()

    def _run_install(self, installer: Installer):
        result = installer.run(on_progress=self._on_progress_thread)
        self.app.after(0, lambda: self._on_complete(result))

    def _on_progress_thread(self, index: int, step: Step, result: StepResult):
        self.app.after(0, lambda: self._update_ui(index, step, result))

    def _update_ui(self, index: int, step: Step, result: StepResult):
        total = len(self._steps)
        if result.status == StepStatus.RUNNING:
            self._step_statuses[index].configure(text="●", text_color=COLOR_RUNNING)
            self._status_text.configure(text=self.app.i18n.get(step.name_key, tool=self._tool.get_name()))
            self._progress.set(index / total)
        elif result.status == StepStatus.SUCCESS:
            self._step_statuses[index].configure(text="✓", text_color=COLOR_SUCCESS)
            self._progress.set((index + 1) / total)
        elif result.status == StepStatus.FAILED:
            self._step_statuses[index].configure(text="✗", text_color=COLOR_ERROR)
        elif result.status == StepStatus.SKIPPED:
            self._step_statuses[index].configure(text="–", text_color=COLOR_MUTED)

    def _on_complete(self, result):
        if result.success:
            self._progress.set(1.0)
            self._status_text.configure(text="")
            from aiready.gui.screens.complete import CompleteScreen
            self.app.show_screen(CompleteScreen)
        else:
            self._error_msg.configure(text=result.error.message if result.error else "Unknown error")
            self._error_frame.pack(pady=10)

    def _retry(self):
        for lbl in self._step_statuses:
            lbl.configure(text="○", text_color=COLOR_MUTED)
        self._progress.set(0)
        self._start_install()

    def _view_log(self):
        log_path = self.app.logger.path
        if log_path.exists():
            import sys
            if sys.platform == "win32":
                import os
                os.startfile(str(log_path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(log_path)])
            else:
                subprocess.Popen(["xdg-open", str(log_path)])
