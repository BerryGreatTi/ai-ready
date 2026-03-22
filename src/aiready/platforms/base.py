# src/aiready/platforms/base.py
"""Abstract base class for platform-specific operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from aiready.core.models import (
    CommandInfo, CommandResult, InstallResult, OSInfo,
    PrereqCheckResult, Prerequisite, ShellType,
)


class UnsupportedPlatformError(Exception):
    pass


class Platform(ABC):
    @abstractmethod
    def get_os_info(self) -> OSInfo: ...

    @abstractmethod
    def check_command(self, command: str) -> Optional[CommandInfo]: ...

    @abstractmethod
    def install_prerequisite(self, prereq: Prerequisite) -> InstallResult: ...

    @abstractmethod
    def verify_prerequisite(self, prereq: Prerequisite) -> PrereqCheckResult: ...

    @abstractmethod
    def add_to_path(self, path: Path) -> bool: ...

    @abstractmethod
    def request_elevation(self, reason_key: str) -> bool: ...

    @abstractmethod
    def run_command(self, cmd: list[str], elevated: bool = False) -> CommandResult: ...

    @abstractmethod
    def get_temp_dir(self) -> Path: ...

    @abstractmethod
    def open_browser(self, url: str) -> bool: ...

    @abstractmethod
    def get_shell_type(self) -> ShellType: ...
