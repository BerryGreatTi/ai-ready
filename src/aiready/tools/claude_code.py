"""Claude Code tool definition."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from aiready.core.models import Prerequisite, Step, StepResult, StepStatus
from aiready.platforms.base import Platform
from aiready.tools.base import OnboardingConfig, OnboardingMode, Tool

if TYPE_CHECKING:
    from aiready.i18n.strings import I18n
    from aiready.core.logger import InstallLogger

_UNIVERSAL_PREREQS = [
    Prerequisite("git", "2.0", "git --version"),
    Prerequisite("nodejs", "22.16", "node --version"),
    Prerequisite("uv", "0.1.0", "uv --version"),
]


class ClaudeCodeTool(Tool):
    """Defines the installation workflow for Claude Code."""

    def __init__(
        self,
        platform: Platform,
        i18n: "I18n",
        logger: Optional["InstallLogger"] = None,
    ) -> None:
        self._platform = platform
        self._i18n = i18n
        self._logger = logger

    def get_name(self) -> str:
        return "Claude Code"

    def get_prerequisites(self, platform: Platform) -> list[Prerequisite]:
        return list(_UNIVERSAL_PREREQS)

    def get_steps(self, platform: Platform) -> list[Step]:
        steps: list[Step] = [
            Step(
                id="check_system",
                name_key="step.check_system",
                action=lambda: self._check_system(platform),
                required=True,
            ),
            Step(
                id="install_prereqs",
                name_key="step.install_prereqs",
                action=lambda: self._install_prereqs(platform),
                required=True,
            ),
            Step(
                id="verify_prereqs",
                name_key="step.verify_prereqs",
                action=lambda: self._verify_prereqs(platform),
                required=True,
            ),
            Step(
                id="install_tool",
                name_key="step.install_tool",
                action=lambda: self._install_tool(platform),
                required=True,
            ),
            Step(
                id="verify_install",
                name_key="step.verify_install",
                action=lambda: self._verify_install(platform),
                required=True,
            ),
            Step(
                id="run_doctor",
                name_key="step.run_doctor",
                action=lambda: self._run_doctor(platform),
                required=False,
            ),
            Step(
                id="authenticate",
                name_key="step.authenticate",
                action=lambda: self._authenticate(platform),
                required=True,
            ),
            Step(
                id="verify_auth",
                name_key="step.verify_auth",
                action=lambda: self._verify_auth(platform),
                required=True,
            ),
        ]
        return steps

    def get_verify_commands(self) -> list[str]:
        return ["claude --version", "claude doctor"]

    def get_onboarding_config(self) -> OnboardingConfig:
        return OnboardingConfig(mode=OnboardingMode.GUIDED)

    # -- private step implementations --

    def _check_system(self, platform: Platform) -> StepResult:
        os_info = platform.get_os_info()
        return StepResult(
            status=StepStatus.SUCCESS,
            message=f"{os_info.system} {os_info.release}",
        )

    def _install_prereqs(self, platform: Platform) -> StepResult:
        prereqs = self.get_prerequisites(platform)
        for prereq in prereqs:
            # Skip if already installed and version is sufficient
            check = platform.verify_prerequisite(prereq)
            if self._logger:
                self._logger.debug("install_prereqs", f"{prereq.name}: installed={check.installed} version={check.current_version} needs_upgrade={check.needs_upgrade}")
            if check.installed and not check.needs_upgrade:
                if self._logger:
                    self._logger.debug("install_prereqs", f"Skipping {prereq.name} - already installed")
                continue
            install_result = platform.install_prerequisite(prereq)
            if self._logger:
                self._logger.debug("install_prereqs", f"{prereq.name} install result: success={install_result.success}")
                if install_result.error:
                    self._logger.debug("install_prereqs", f"{prereq.name} error: {install_result.error.message}")
                    if install_result.error.detail:
                        self._logger.debug("install_prereqs", f"{prereq.name} detail: {install_result.error.detail}")
            if not install_result.success:
                error_msg = f"Failed to install {prereq.name}"
                error_detail = ""
                if install_result.error:
                    error_detail = install_result.error.detail or install_result.error.message or ""
                return StepResult(
                    status=StepStatus.FAILED,
                    message=error_msg,
                    detail=error_detail,
                )
        return StepResult(status=StepStatus.SUCCESS)

    def _verify_prereqs(self, platform: Platform) -> StepResult:
        prereqs = self.get_prerequisites(platform)
        for prereq in prereqs:
            check = platform.verify_prerequisite(prereq)
            if self._logger:
                import os
                self._logger.debug("verify_prereqs", f"{prereq.name}: installed={check.installed} version={check.current_version} PATH={os.environ.get('PATH', 'NOT SET')[:200]}")
            if not check.installed:
                return StepResult(
                    status=StepStatus.FAILED,
                    message=f"{prereq.name} not found",
                    detail=f"check_command={prereq.check_command}",
                )
        return StepResult(status=StepStatus.SUCCESS)

    def _install_tool(self, platform: Platform) -> StepResult:
        system = platform.get_os_info().system
        if system == "Windows":
            # Use CMD-based installer (avoids PowerShell Korean encoding issues)
            tmp = platform.get_temp_dir()
            dl_result = platform.run_command([
                "curl", "-fsSL", "https://claude.ai/install.cmd",
                "-o", str(tmp / "claude-install.cmd"),
            ])
            if not dl_result.succeeded:
                return StepResult(status=StepStatus.FAILED, message="Failed to download installer")
            result = platform.run_command(["cmd", "/c", str(tmp / "claude-install.cmd")])
        else:
            # macOS/Linux: native installer via curl
            result = platform.run_command(["bash", "-c", "curl -fsSL https://claude.ai/install.sh | bash"])
        if result.succeeded:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.FAILED, message=result.stderr or "Installation failed")

    def _verify_install(self, platform: Platform) -> StepResult:
        info = platform.check_command("claude")
        if info is not None:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.FAILED, message="claude command not found")

    def _run_doctor(self, platform: Platform) -> StepResult:
        result = platform.run_command(["claude", "doctor"])
        if result.succeeded:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.SUCCESS, message="doctor check completed with warnings")

    def _authenticate(self, platform: Platform) -> StepResult:
        platform.open_browser("https://claude.ai/login")
        return StepResult(status=StepStatus.SUCCESS)

    def _verify_auth(self, platform: Platform) -> StepResult:
        result = platform.run_command(["claude", "--version"])
        if result.succeeded:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.FAILED, message="Authentication verification failed")
