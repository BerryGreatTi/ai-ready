# src/aiready/platforms/macos.py
"""macOS platform implementation."""

from __future__ import annotations

import os
import platform as platform_module
import shutil
import tempfile
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
from aiready.core.process import run_process, run_process_live
from aiready.core.version import version_gte
from aiready.platforms.base import Platform

# Download URL for Node.js macOS installer (.pkg)
_NODEJS_PKG_URL = "https://nodejs.org/dist/v24.14.0/node-v24.14.0.pkg"


class MacOSPlatform(Platform):
    """Platform implementation for macOS (Darwin)."""

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
        path = shutil.which(command)
        if path is None:
            return None

        result = run_process([command, "--version"])
        if result.return_code == -1:
            return CommandInfo(path=path, version=None)

        raw = (result.stdout or result.stderr or "").strip()
        version = raw.splitlines()[0] if raw else None
        return CommandInfo(path=path, version=version)

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
        brew = self.check_command("brew")
        if brew:
            result = run_process_live(["brew", "install", "git"])
        else:
            result = run_process_live(["xcode-select", "--install"])
        return InstallResult(success=result.succeeded)

    def _install_uv(self) -> InstallResult:
        result = run_process_live(["bash", "-c", "curl -LsSf https://astral.sh/uv/install.sh | bash"])
        if result.succeeded:
            import os
            home = os.environ.get("HOME", os.path.expanduser("~"))
            cargo_bin = os.path.join(home, ".cargo", "bin")
            local_bin = os.path.join(home, ".local", "bin")
            current = os.environ.get("PATH", "")
            for d in [cargo_bin, local_bin]:
                if d not in current:
                    os.environ["PATH"] = f"{d}:{current}"
                    current = os.environ["PATH"]
            return InstallResult(success=True)
        return InstallResult(success=False, error=StepResult(status=StepStatus.FAILED, message=result.stderr or "UV installation failed"))

    def _install_nodejs(self) -> InstallResult:
        brew = self.check_command("brew")
        if brew is not None:
            return self._install_nodejs_via_brew()
        return self._install_nodejs_via_pkg()

    def _install_nodejs_via_brew(self) -> InstallResult:
        result = run_process_live(["brew", "install", "node"])
        if result.succeeded:
            return InstallResult(success=True)
        return InstallResult(
            success=False,
            error=StepResult(
                status=StepStatus.FAILED,
                message=result.stderr or "brew install node failed",
            ),
        )

    def _install_nodejs_via_pkg(self) -> InstallResult:
        tmp = self.get_temp_dir()
        pkg_path = tmp / "node-latest.pkg"
        commands = [
            ["curl", "-fsSL", _NODEJS_PKG_URL, "-o", str(pkg_path)],
            ["installer", "-pkg", str(pkg_path), "-target", "/"],
        ]
        for cmd in commands:
            result = run_process_live(cmd)
            if not result.succeeded:
                return InstallResult(
                    success=False,
                    error=StepResult(
                        status=StepStatus.FAILED,
                        message=result.stderr or "Package install failed",
                        detail=f"Command: {' '.join(cmd)}",
                    ),
                )
        return InstallResult(success=True)

    # ------------------------------------------------------------------
    # verify_prerequisite
    # ------------------------------------------------------------------

    def verify_prerequisite(self, prereq: Prerequisite) -> PrereqCheckResult:
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
        rc_file = self._get_rc_file()
        export_line = f'export PATH="{path}:$PATH"'
        try:
            with open(rc_file, "r") as fh:
                content = fh.read()
            if str(path) in content:
                return True
            with open(rc_file, "a") as fh:
                fh.write(f"\n{export_line}\n")
            return True
        except OSError:
            return False

    def _get_rc_file(self) -> Path:
        shell = os.environ.get("SHELL", "")
        home = Path.home()
        if "bash" in shell:
            return home / ".bashrc"
        return home / ".zshrc"

    # ------------------------------------------------------------------
    # request_elevation
    # ------------------------------------------------------------------

    def request_elevation(self, reason_key: str) -> bool:
        return os.geteuid() == 0

    # ------------------------------------------------------------------
    # run_command
    # ------------------------------------------------------------------

    def run_command(self, cmd: list[str], elevated: bool = False, timeout: int = 120) -> CommandResult:
        actual_cmd = (["sudo"] + cmd) if elevated else cmd
        return run_process(actual_cmd, timeout=timeout)

    # ------------------------------------------------------------------
    # get_temp_dir
    # ------------------------------------------------------------------

    def get_temp_dir(self) -> Path:
        tmp = Path(tempfile.gettempdir()) / "aiready"
        tmp.mkdir(parents=True, exist_ok=True)
        return tmp

    # ------------------------------------------------------------------
    # open_browser
    # ------------------------------------------------------------------

    def open_browser(self, url: str) -> bool:
        try:
            result = run_process(["open", url])
            return result.succeeded
        except Exception:
            return False

    # ------------------------------------------------------------------
    # get_shell_type
    # ------------------------------------------------------------------

    def get_shell_type(self) -> ShellType:
        shell = os.environ.get("SHELL", "")
        if "bash" in shell:
            return ShellType.BASH
        return ShellType.ZSH
