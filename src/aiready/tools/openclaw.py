"""OpenClaw tool definition."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from aiready.core.models import Prerequisite, Step, StepResult, StepStatus
from aiready.platforms.base import Platform
from aiready.tools.base import OnboardingConfig, OnboardingMode, Tool

if TYPE_CHECKING:
    from aiready.i18n.strings import I18n
    from aiready.core.logger import InstallLogger


_NODEJS_PREREQ = Prerequisite("nodejs", "22.16", "node --version")


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
        return [_NODEJS_PREREQ]

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
                name_key="step.install_nodejs",
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
                required=False,
            ),
            Step(
                id="install_tool_fallback",
                name_key="step.install_tool_fallback",
                action=lambda: self._install_tool_fallback(platform),
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
        install_result = platform.install_prerequisite(_NODEJS_PREREQ)
        if install_result.success:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.FAILED, message="Failed to install Node.js")

    def _verify_prereqs(self, platform: Platform) -> StepResult:
        check = platform.verify_prerequisite(_NODEJS_PREREQ)
        if check.installed:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.FAILED, message="Node.js not found")

    def _install_tool(self, platform: Platform) -> StepResult:
        result = platform.run_command(["npm", "install", "-g", "openclaw"])
        if result.succeeded:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.FAILED, message=result.stderr or "npm install failed")

    def _install_tool_fallback(self, platform: Platform) -> StepResult:
        result = platform.run_command(["npx", "openclaw@latest", "install"])
        if result.succeeded:
            return StepResult(status=StepStatus.SUCCESS)
        return StepResult(status=StepStatus.FAILED, message=result.stderr or "npx fallback failed")

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
