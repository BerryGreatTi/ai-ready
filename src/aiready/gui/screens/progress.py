"""Installation progress screen."""
from __future__ import annotations

import subprocess
import threading

import customtkinter as ctk

from aiready.core.installer import Installer
from aiready.core.models import Step, StepResult, StepStatus
from aiready.gui.theme import (
    FONT_TITLE, FONT_BODY, FONT_SMALL, PADDING,
    COLOR_SUCCESS, COLOR_ERROR, COLOR_RUNNING,
)
from aiready.tools.claude_code import ClaudeCodeTool
from aiready.tools.openclaw import OpenClawTool


class ProgressScreen(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._step_labels = []
        self._step_statuses = []
        self._failed = False
        self._failed_step_index = -1

        # Create tool
        if app.selected_tool == "claude_code":
            self._tool = ClaudeCodeTool(app.platform, app.i18n, app.logger)
        else:
            self._tool = OpenClawTool(app.platform, app.i18n, app.logger)

        # Get steps for display
        self._steps = self._tool.get_steps(app.platform)
        total = len(self._steps)

        # Title
        tool_name = self._tool.get_name()
        ctk.CTkLabel(
            self, text=f"{app.i18n.get('progress.title')} - {tool_name}",
            font=FONT_TITLE,
        ).pack(pady=(20, 15))

        # Step list (scrollable if many steps)
        self._step_frame = ctk.CTkScrollableFrame(self, height=300)
        self._step_frame.pack(fill="x", padx=PADDING, pady=(0, 10))

        for i, step in enumerate(self._steps):
            row = ctk.CTkFrame(self._step_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            status_label = ctk.CTkLabel(row, text="○", width=30, font=FONT_BODY)
            status_label.pack(side="left")
            self._step_statuses.append(status_label)

            name_label = ctk.CTkLabel(
                row, text=app.i18n.get(step.name_key, tool=self._tool.get_name()), font=FONT_BODY, anchor="w",
            )
            name_label.pack(side="left", fill="x", expand=True)
            self._step_labels.append(name_label)

        # Progress bar
        self._progress = ctk.CTkProgressBar(self, width=400)
        self._progress.pack(pady=(10, 5), padx=PADDING)
        self._progress.set(0)

        # Status text
        self._status_text = ctk.CTkLabel(
            self, text="", font=FONT_SMALL, text_color="gray",
        )
        self._status_text.pack(pady=(0, 10))

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
            err_buttons, text=app.i18n.get("button.retry"), width=100,
            command=self._retry,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            err_buttons, text=app.i18n.get("button.view_log"), width=100,
            command=self._view_log,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            err_buttons, text=app.i18n.get("button.exit"), width=100,
            command=self.app.destroy,
        ).pack(side="left", padx=5)

        # Start installation
        self._start_install()

    def _start_install(self):
        self._failed = False
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
            self._failed = True
            self._failed_step_index = index
        elif result.status == StepStatus.SKIPPED:
            self._step_statuses[index].configure(text="–", text_color="gray")

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
        # Reset UI
        for lbl in self._step_statuses:
            lbl.configure(text="○", text_color="gray")
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
