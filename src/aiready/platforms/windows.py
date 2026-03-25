# src/aiready/platforms/windows.py
"""Windows platform implementation."""

from __future__ import annotations

import os
import platform as platform_module
import shutil
import tempfile
import webbrowser
from pathlib import Path
from typing import Optional

from aiready.core.models import (
    CommandInfo,
    CommandResult,
    InstallResult,
    OSInfo,
    PrereqCheckResult,
    Prerequisite,
    ShellType,
    StepResult,
    StepStatus,
)
from aiready.core.process import run_process
from aiready.core.version import version_gte
from aiready.platforms.base import Platform

# Known fallback paths for common tools on Windows (static paths only)
_KNOWN_PATHS: dict[str, list[str]] = {
    "git": [r"C:\Program Files\Git\cmd\git.exe"],
    "node": [r"C:\Program Files\nodejs\node.exe"],
    "uv": [],  # dynamic path added at runtime via USERPROFILE
}

# Node.js MSI download URL (LTS)
_NODEJS_MSI_URL = "https://nodejs.org/dist/latest-v20.x/node-v20.11.1-x64.msi"

# Git installer download URL
_GIT_EXE_URL = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"


class WindowsPlatform(Platform):
    """Platform implementation for Windows operating systems."""

    # ------------------------------------------------------------------
    # get_os_info
    # ------------------------------------------------------------------

    def get_os_info(self) -> OSInfo:
        return OSInfo(
            system=platform_module.system(),
            release=platform_module.release(),
            version=platform_module.version(),
            arch=platform_module.machine(),
        )

    # ------------------------------------------------------------------
    # check_command
    # ------------------------------------------------------------------

    def check_command(self, command: str) -> Optional[CommandInfo]:
        # Try shutil.which first
        path = shutil.which(command)

        # Fall back to known paths if not found
        if path is None:
            path = self._find_known_path(command)

        if path is None:
            return None

        result = run_process([path, "--version"])
        if result.return_code == -1:
            return CommandInfo(path=path, version=None)

        raw = (result.stdout or result.stderr or "").strip()
        version = raw.splitlines()[0] if raw else None
        return CommandInfo(path=path, version=version)

    def _find_known_path(self, command: str) -> Optional[str]:
        candidates = list(_KNOWN_PATHS.get(command, []))
        # Add dynamic paths that depend on runtime environment
        userprofile = os.environ.get("USERPROFILE", r"C:\Users\Default")
        if command == "claude":
            candidates.append(str(Path(userprofile) / ".local" / "bin" / "claude.exe"))
        if command == "uv":
            candidates.append(str(Path(userprofile) / ".local" / "bin" / "uv.exe"))
            candidates.append(str(Path(userprofile) / ".cargo" / "bin" / "uv.exe"))
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
        return None

    # ------------------------------------------------------------------
    # install_prerequisite
    # ------------------------------------------------------------------

    def install_prerequisite(self, prereq: Prerequisite) -> InstallResult:
        if prereq.name == "nodejs":
            return self._install_nodejs()
        if prereq.name == "git":
            return self._install_git()
        if prereq.name == "uv":
            return self._install_uv()
        return InstallResult(
            success=False,
            error=StepResult(
                status=StepStatus.FAILED,
                message=f"No install strategy for: {prereq.name}",
            ),
        )

    def _install_git(self) -> InstallResult:
        tmp = self.get_temp_dir()
        exe_path = tmp / "git-installer.exe"
        commands = [
            ["curl", "-fsSL", _GIT_EXE_URL, "-o", str(exe_path)],
            [str(exe_path), "/VERYSILENT", "/NORESTART"],
        ]
        result = self._run_install_commands(commands)
        if result.success:
            self._refresh_path()
        return result

    def _install_uv(self) -> InstallResult:
        result = run_process([
            "powershell", "-ExecutionPolicy", "ByPass", "-Command",
            "irm https://astral.sh/uv/install.ps1 | iex",
        ])
        if result.succeeded:
            self._refresh_path()
            return InstallResult(success=True)
        return InstallResult(
            success=False,
            error=StepResult(status=StepStatus.FAILED, message=result.stderr or "UV installation failed"),
        )

    def _install_nodejs(self) -> InstallResult:
        tmp = self.get_temp_dir()
        msi_path = tmp / "node-latest.msi"
        commands = [
            ["curl", "-fsSL", _NODEJS_MSI_URL, "-o", str(msi_path)],
            ["msiexec", "/i", str(msi_path), "/qn"],
        ]
        result = self._run_install_commands(commands)
        if result.success:
            self._refresh_path()
        return result

    def _refresh_path(self) -> None:
        """Refresh PATH by adding known install dirs to the existing PATH."""
        # Don't replace PATH from registry (contains unexpanded %VAR% on Windows).
        # Instead, append known install locations to the current process PATH.
        current = os.environ.get("PATH", "")
        userprofile = os.environ.get("USERPROFILE", "")
        dirs_to_add = [
            r"C:\Program Files\Git\cmd",
            r"C:\Program Files\nodejs",
            os.path.join(userprofile, ".local", "bin"),
            os.path.join(userprofile, ".cargo", "bin"),
        ]
        for d in dirs_to_add:
            if d and d not in current:
                current = f"{d};{current}"
        os.environ["PATH"] = current

    def _run_install_commands(self, commands: list[list[str]]) -> InstallResult:
        for cmd in commands:
            result = run_process(cmd)
            if not result.succeeded:
                return InstallResult(
                    success=False,
                    error=StepResult(
                        status=StepStatus.FAILED,
                        message=result.stderr or "Install command failed",
                        detail=f"Command: {' '.join(cmd)}",
                    ),
                )
        return InstallResult(success=True)

    # ------------------------------------------------------------------
    # verify_prerequisite
    # ------------------------------------------------------------------

    def verify_prerequisite(self, prereq: Prerequisite) -> PrereqCheckResult:
        # Extract command name from check_command (e.g., "git --version" -> "git")
        command = prereq.check_command.split()[0]
        info = self.check_command(command)
        if info is None:
            return PrereqCheckResult(prereq=prereq, installed=False)

        current_version = info.version or ""
        if not current_version:
            return PrereqCheckResult(prereq=prereq, installed=True, current_version=None)

        ok = version_gte(current_version, prereq.min_version)
        return PrereqCheckResult(
            prereq=prereq,
            installed=True,
            current_version=current_version,
            needs_upgrade=not ok,
        )

    # ------------------------------------------------------------------
    # add_to_path
    # ------------------------------------------------------------------

    def add_to_path(self, path: Path) -> bool:
        # Query current user PATH via reg command (no winreg import needed)
        query_result = run_process(
            ["reg", "query", r"HKCU\Environment", "/v", "Path"]
        )
        if not query_result.succeeded:
            return False

        current_path = self._extract_reg_value(query_result.stdout)
        if str(path) in current_path:
            return True

        new_path = f"{current_path};{path}" if current_path else str(path)
        set_result = run_process(
            ["reg", "add", r"HKCU\Environment", "/v", "Path", "/t", "REG_EXPAND_SZ", "/d", new_path, "/f"]
        )
        return set_result.succeeded

    def _extract_reg_value(self, reg_output: str) -> str:
        for line in reg_output.splitlines():
            line = line.strip()
            if "REG_EXPAND_SZ" in line or "REG_SZ" in line:
                parts = line.split("REG_EXPAND_SZ", 1) if "REG_EXPAND_SZ" in line else line.split("REG_SZ", 1)
                if len(parts) == 2:
                    return parts[1].strip()
        return ""

    # ------------------------------------------------------------------
    # request_elevation
    # ------------------------------------------------------------------

    def request_elevation(self, reason_key: str) -> bool:
        # Attempt to write to a system-protected location to detect admin rights
        result = run_process(
            ["reg", "query", r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion", "/v", "ProductName"]
        )
        return result.succeeded

    # ------------------------------------------------------------------
    # run_command
    # ------------------------------------------------------------------

    def run_command(self, cmd: list[str], elevated: bool = False) -> CommandResult:
        # Windows does not use sudo; elevation is handled by UAC / runas
        return run_process(cmd)

    # ------------------------------------------------------------------
    # get_temp_dir
    # ------------------------------------------------------------------

    def get_temp_dir(self) -> Path:
        base = os.environ.get("TEMP", tempfile.gettempdir())
        tmp = Path(base) / "aiready"
        tmp.mkdir(parents=True, exist_ok=True)
        return tmp

    # ------------------------------------------------------------------
    # open_browser
    # ------------------------------------------------------------------

    def open_browser(self, url: str) -> bool:
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # get_shell_type
    # ------------------------------------------------------------------

    def get_shell_type(self) -> ShellType:
        if os.environ.get("PSModulePath"):
            return ShellType.POWERSHELL
        return ShellType.CMD
