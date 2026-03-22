"""Core data models for AIReady. All models are immutable (frozen dataclass)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


class StepStatus(Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ShellType(Enum):
    BASH = "bash"
    ZSH = "zsh"
    POWERSHELL = "powershell"
    CMD = "cmd"


@dataclass(frozen=True)
class Step:
    id: str
    name_key: str
    action: Callable[[], "StepResult"]
    required: bool


@dataclass(frozen=True)
class StepResult:
    status: StepStatus
    message: Optional[str] = None
    detail: Optional[str] = None

    @property
    def failed(self) -> bool:
        return self.status == StepStatus.FAILED


@dataclass(frozen=True)
class InstallResult:
    success: bool
    failed_step: Optional[Step] = None
    error: Optional[StepResult] = None


@dataclass(frozen=True)
class Prerequisite:
    name: str
    min_version: str
    check_command: str


@dataclass(frozen=True)
class PrereqCheckResult:
    prereq: Prerequisite
    installed: bool
    current_version: Optional[str] = None
    needs_upgrade: bool = False


@dataclass(frozen=True)
class CommandResult:
    return_code: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.return_code == 0


@dataclass(frozen=True)
class OSInfo:
    system: str
    release: str
    version: str
    arch: str


@dataclass(frozen=True)
class CommandInfo:
    path: str
    version: Optional[str] = None
