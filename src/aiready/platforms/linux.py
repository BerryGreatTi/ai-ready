# src/aiready/platforms/linux.py
"""Linux platform implementation."""

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

_APT_DISTROS = {"ubuntu", "debian", "linuxmint", "pop", "elementary"}
_DNF_DISTROS = {"fedora", "rhel", "centos", "rocky", "almalinux", "ol"}
_PACMAN_DISTROS = {"arch", "manjaro", "endeavouros", "garuda"}
_APK_DISTROS = {"alpine"}


class LinuxPlatform(Platform):
    """Platform implementation for Linux operating systems."""

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
            # run_process error (timeout / file-not-found / OS error) — no version
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
        pkg_manager = self._detect_package_manager()
        if pkg_manager == "apt-get":
            cmd = ["sudo", "apt-get", "install", "-y", "git"]
        elif pkg_manager == "dnf":
            cmd = ["sudo", "dnf", "install", "-y", "git"]
        elif pkg_manager == "pacman":
            cmd = ["sudo", "pacman", "-Sy", "--noconfirm", "git"]
        else:
            return InstallResult(success=False, error=StepResult(status=StepStatus.FAILED, message="No supported package manager for git"))
        result = run_process(cmd)
        return InstallResult(success=result.succeeded)

    def _install_uv(self) -> InstallResult:
        result = run_process(["bash", "-c", "curl -LsSf https://astral.sh/uv/install.sh | bash"])
        if result.succeeded:
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
        pkg_manager = self._detect_package_manager()
        if pkg_manager == "apt-get":
            commands = [
                ["curl", "-fsSL", "https://deb.nodesource.com/setup_24.x", "-o", "/tmp/nodesource_setup.sh"],
                ["bash", "/tmp/nodesource_setup.sh"],
                ["apt-get", "install", "-y", "nodejs"],
            ]
        elif pkg_manager == "dnf":
            commands = [
                ["dnf", "module", "enable", "-y", "nodejs:lts"],
                ["dnf", "install", "-y", "nodejs"],
            ]
        elif pkg_manager == "pacman":
            commands = [["pacman", "-S", "--noconfirm", "nodejs", "npm"]]
        elif pkg_manager == "apk":
            commands = [["apk", "add", "--no-cache", "nodejs", "npm"]]
        else:
            commands = [["apt-get", "install", "-y", "nodejs"]]

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
        if "zsh" in shell:
            return home / ".zshrc"
        return home / ".bashrc"

    # ------------------------------------------------------------------
    # request_elevation
    # ------------------------------------------------------------------

    def request_elevation(self, reason_key: str) -> bool:
        return os.geteuid() == 0

    # ------------------------------------------------------------------
    # run_command
    # ------------------------------------------------------------------

    def run_command(self, cmd: list[str], elevated: bool = False) -> CommandResult:
        actual_cmd = (["sudo"] + cmd) if elevated else cmd
        return run_process(actual_cmd)

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
            webbrowser.open(url)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # get_shell_type
    # ------------------------------------------------------------------

    def get_shell_type(self) -> ShellType:
        shell = os.environ.get("SHELL", "")
        if "zsh" in shell:
            return ShellType.ZSH
        return ShellType.BASH

    # ------------------------------------------------------------------
    # _detect_distro
    # ------------------------------------------------------------------

    def _detect_distro(self) -> str:
        try:
            with open("/etc/os-release") as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith("ID="):
                        return line.split("=", 1)[1].strip().strip('"').lower()
        except FileNotFoundError:
            pass
        return "unknown"

    # ------------------------------------------------------------------
    # _detect_package_manager
    # ------------------------------------------------------------------

    def _detect_package_manager(self) -> str:
        distro = self._detect_distro()
        if distro in _APT_DISTROS:
            return "apt-get"
        if distro in _DNF_DISTROS:
            return "dnf"
        if distro in _PACMAN_DISTROS:
            return "pacman"
        if distro in _APK_DISTROS:
            return "apk"
        return "apt-get"
