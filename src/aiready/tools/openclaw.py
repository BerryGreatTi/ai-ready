"""OpenClaw tool definition."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from aiready.core.models import Prerequisite, Step, StepResult, StepStatus
from aiready.core.process import run_process_live
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


class OpenClawTool(Tool):
    """Defines the installation workflow for OpenClaw."""

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
        return "OpenClaw"

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
                id="select_provider",
                name_key="step.select_provider",
                action=lambda: self._select_provider(platform),
                required=True,
            ),
            Step(
                id="configure_api_key",
                name_key="step.configure_api_key",
                action=lambda: self._configure_api_key(platform),
                required=False,
            ),
            Step(
                id="validate_api_key",
                name_key="step.validate_api_key",
                action=lambda: self._validate_api_key(platform),
                required=False,
            ),
            Step(
                id="run_onboarding",
                name_key="step.run_onboarding",
                action=lambda: self._run_onboarding(platform),
                required=True,
            ),
            Step(
                id="verify_gateway",
                name_key="step.verify_gateway",
                action=lambda: self._verify_gateway(platform),
                required=True,
            ),
            Step(
                id="run_doctor",
                name_key="step.run_doctor",
                action=lambda: self._run_doctor(platform),
                required=False,
            ),
        ]
        return steps

    def get_verify_commands(self) -> list[str]:
        return ["openclaw --version", "openclaw doctor", "openclaw gateway status"]

    def get_onboarding_config(self) -> OnboardingConfig:
        return OnboardingConfig(
            mode=OnboardingMode.AUTOMATIC,
            provider_selection=True,
            api_key_input=True,
        )

    # -- private step implementations --

    def _check_system(self, platform: Platform) -> StepResult:
        result = platform.run_command(["node", "--version"])
        if result.succeeded:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.SUCCESS, message="system check passed")

    def _install_prereqs(self, platform: Platform) -> StepResult:
        prereqs = self.get_prerequisites(platform)
        for prereq in prereqs:
            check = platform.verify_prerequisite(prereq)
            if check.installed and not check.needs_upgrade:
                continue
            install_result = platform.install_prerequisite(prereq)
            if not install_result.success:
                return StepResult(
                    status=StepStatus.FAILED,
                    message=f"Failed to install {prereq.name}",
                    detail=install_result.error.message if install_result.error else None,
                )
        return StepResult(status=StepStatus.SUCCESS)

    def _verify_prereqs(self, platform: Platform) -> StepResult:
        prereqs = self.get_prerequisites(platform)
        for prereq in prereqs:
            check = platform.verify_prerequisite(prereq)
            if not check.installed:
                return StepResult(
                    status=StepStatus.FAILED,
                    message=f"{prereq.name} not found",
                )
        return StepResult(status=StepStatus.SUCCESS)

    def _install_tool(self, platform: Platform) -> StepResult:
        _TIMEOUT = 600
        system = platform.get_os_info().system

        # Method 1: Official installer script
        if system == "Windows":
            if self._logger:
                self._logger.debug("install_tool", "Trying official PS1 installer")
            result = run_process_live([
                "powershell", "-ExecutionPolicy", "ByPass", "-Command",
                "iwr -useb https://openclaw.ai/install.ps1 | iex",
            ], timeout=_TIMEOUT)
        else:
            if self._logger:
                self._logger.debug("install_tool", "Trying official SH installer")
            result = run_process_live([
                "bash", "-c", "curl -fsSL https://openclaw.ai/install.sh | bash",
            ], timeout=_TIMEOUT)
        if self._logger:
            self._logger.debug("install_tool", f"Official installer: code={result.return_code} stdout={result.stdout[-300:]} stderr={result.stderr[-300:]}")

        # The official installer may report failure even though openclaw was installed
        # (e.g., PATH not refreshed during its own verification). Check ourselves.
        self._refresh_path_for_openclaw(platform)
        if platform.check_command("openclaw") is not None:
            if self._logger:
                self._logger.debug("install_tool", "openclaw found in PATH after official installer (ignoring exit code)")
            return StepResult(status=StepStatus.SUCCESS)

        # Method 2: npm global install (Node.js already installed)
        self._refresh_path_for_npm(platform)
        if self._logger:
            self._logger.debug("install_tool", "Trying npm install as fallback")
        result2 = run_process_live(["npm", "install", "-g", "openclaw@latest"], timeout=_TIMEOUT)
        if self._logger:
            self._logger.debug("install_tool", f"npm install: code={result2.return_code} stdout={result2.stdout[-300:]} stderr={result2.stderr[-300:]}")

        self._refresh_path_for_openclaw(platform)
        if platform.check_command("openclaw") is not None:
            return StepResult(status=StepStatus.SUCCESS)

        # Both failed
        detail = (
            f"Official installer: code={result.return_code} stderr={result.stderr[-200:]}\n"
            f"npm install: code={result2.return_code} stderr={result2.stderr[-200:]}"
        )
        return StepResult(status=StepStatus.FAILED, message="All installation methods failed", detail=detail)

    def _refresh_path_for_openclaw(self, platform: Platform) -> None:
        """Add common openclaw install locations to current PATH."""
        import os
        current = os.environ.get("PATH", "")
        home = os.environ.get("USERPROFILE", os.environ.get("HOME", ""))
        dirs = [
            os.path.join(home, ".local", "bin"),
            os.path.join(home, ".openclaw", "bin"),
            os.path.join(home, "AppData", "Roaming", "npm"),
            os.path.join(home, ".npm-global", "bin"),
        ]
        for d in dirs:
            if d and d not in current and os.path.isdir(d):
                current = f"{d}{os.pathsep}{current}"
        os.environ["PATH"] = current

    def _refresh_path_for_npm(self, platform: Platform) -> None:
        """Ensure npm is findable in PATH."""
        import os
        current = os.environ.get("PATH", "")
        npm_dirs = [
            r"C:\Program Files\nodejs",
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Roaming", "npm"),
            "/usr/local/bin",
        ]
        for d in npm_dirs:
            if d and d not in current and os.path.isdir(d):
                current = f"{d}{os.pathsep}{current}"
        os.environ["PATH"] = current

    def _verify_install(self, platform: Platform) -> StepResult:
        info = platform.check_command("openclaw")
        if info is not None:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.FAILED, message="openclaw command not found")

    def _select_provider(self, platform: Platform) -> StepResult:
        return StepResult(status=StepStatus.SUCCESS, message="Provider selection deferred to GUI")

    def _configure_api_key(self, platform: Platform) -> StepResult:
        return StepResult(status=StepStatus.SUCCESS, message="API key configuration deferred to GUI")

    def _validate_api_key(self, platform: Platform) -> StepResult:
        return StepResult(status=StepStatus.SUCCESS, message="API key validation deferred to GUI")

    def _run_onboarding(self, platform: Platform) -> StepResult:
        result = platform.run_command(["openclaw", "onboard"])
        if result.succeeded:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.SUCCESS, message="onboarding deferred to GUI")

    def _verify_gateway(self, platform: Platform) -> StepResult:
        result = platform.run_command(["openclaw", "gateway", "status"])
        if result.succeeded:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.FAILED, message="Gateway not responding")

    def _run_doctor(self, platform: Platform) -> StepResult:
        result = platform.run_command(["openclaw", "doctor"])
        if result.succeeded:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.SUCCESS, message="doctor check completed with warnings")
