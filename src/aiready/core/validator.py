"""Installation verification with retry support."""
from __future__ import annotations
from aiready.core.models import StepResult, StepStatus
from aiready.core.version import version_gte
from aiready.platforms.base import Platform


class InstallationValidator:
    def __init__(self, platform: Platform):
        self._platform = platform

    def validate(self, command: str, min_version: str | None = None) -> StepResult:
        result = self._platform.run_command(command.split())
        if not result.succeeded:
            return StepResult(status=StepStatus.FAILED, message=f"Command failed: {command}", detail=result.stderr)
        if min_version:
            version = result.stdout.strip()
            if not version_gte(version, min_version):
                return StepResult(status=StepStatus.FAILED, message=f"Version {version} < {min_version}")
        return StepResult(status=StepStatus.SUCCESS)

    def validate_with_retry(self, command: str, min_version: str | None = None, retries: int = 1) -> StepResult:
        result = self.validate(command, min_version)
        attempts = 0
        while result.failed and attempts < retries:
            result = self.validate(command, min_version)
            attempts += 1
        return result
