# src/aiready/core/process.py
"""Subprocess wrapper with timeout, output capture, and live tee mode."""

from __future__ import annotations

import subprocess
import sys
import threading
from io import StringIO

from aiready.core.models import CommandResult


def run_process(
    cmd: list[str],
    timeout: int = 120,
    cwd: str | None = None,
) -> CommandResult:
    """Run a command and capture stdout/stderr in memory.

    Suitable for short-lived commands that produce small output.
    For long-running installers, use run_process_live() instead.
    """
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


def _reader_thread(pipe, buffer: StringIO, echo_to) -> None:
    """Read lines from a pipe, echo to a stream, and collect in buffer."""
    try:
        for line in iter(pipe.readline, ""):
            if echo_to:
                try:
                    echo_to.write(line)
                    echo_to.flush()
                except Exception:
                    pass
            buffer.write(line)
        pipe.close()
    except Exception:
        pass


def run_process_live(
    cmd: list[str],
    timeout: int = 600,
    cwd: str | None = None,
) -> CommandResult:
    """Run a command with live stdout/stderr output (tee mode).

    Output is printed to the console in real time AND captured for logging.
    Avoids pipe buffer deadlocks by reading stdout/stderr in separate threads.
    Use for long-running installers (Git, Node.js, UV, Claude Code, OpenClaw).
    """
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            bufsize=1,
        )

        stdout_buf = StringIO()
        stderr_buf = StringIO()

        stdout_thread = threading.Thread(
            target=_reader_thread,
            args=(proc.stdout, stdout_buf, sys.stdout),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_reader_thread,
            args=(proc.stderr, stderr_buf, sys.stderr),
            daemon=True,
        )

        stdout_thread.start()
        stderr_thread.start()

        proc.wait(timeout=timeout)
        stdout_thread.join(timeout=5)
        stderr_thread.join(timeout=5)

        stdout_text = stdout_buf.getvalue()[-2000:]
        stderr_text = stderr_buf.getvalue()[-2000:]

        return CommandResult(
            return_code=proc.returncode,
            stdout=stdout_text,
            stderr=stderr_text,
        )
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
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


# Backward compatibility alias
run_process_uncaptured = run_process_live
