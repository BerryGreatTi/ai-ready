# src/aiready/core/process.py
"""Subprocess wrapper with timeout and output capture."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

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
            stdin=subprocess.DEVNULL,
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


def run_process_uncaptured(
    cmd: list[str],
    timeout: int = 600,
    cwd: str | None = None,
) -> CommandResult:
    """Run a command without capturing output (avoids pipe buffer deadlocks).

    Use for long-running installers that produce lots of output.
    Stdout/stderr are written to temp files and read after completion.
    """
    tmp_dir = Path(tempfile.gettempdir()) / "aiready"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    stdout_file = tmp_dir / "proc_stdout.log"
    stderr_file = tmp_dir / "proc_stderr.log"
    try:
        with open(stdout_file, "w") as out, open(stderr_file, "w") as err:
            result = subprocess.run(
                cmd,
                stdout=out,
                stderr=err,
                timeout=timeout,
                cwd=cwd,
                stdin=subprocess.DEVNULL,
            )
        stdout_text = stdout_file.read_text(encoding="utf-8", errors="replace")[-2000:]
        stderr_text = stderr_file.read_text(encoding="utf-8", errors="replace")[-2000:]
        return CommandResult(
            return_code=result.returncode,
            stdout=stdout_text,
            stderr=stderr_text,
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
