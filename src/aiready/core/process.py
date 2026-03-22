# src/aiready/core/process.py
"""Subprocess wrapper with timeout and output capture."""

from __future__ import annotations

import subprocess

from aiready.core.models import CommandResult


def run_process(
    cmd: list[str],
    timeout: int = 120,
    cwd: str | None = None,
) -> CommandResult:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        return CommandResult(
            return_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            return_code=-1,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
        )
    except FileNotFoundError:
        return CommandResult(
            return_code=-1,
            stdout="",
            stderr=f"Command not found: {cmd[0]}",
        )
    except OSError as e:
        return CommandResult(
            return_code=-1,
            stdout="",
            stderr=str(e),
        )
