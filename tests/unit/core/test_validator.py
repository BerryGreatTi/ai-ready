from unittest.mock import MagicMock
from aiready.core.validator import InstallationValidator
from aiready.core.models import CommandResult, StepStatus


class TestInstallationValidator:
    def _make_platform(self, return_code=0, stdout="v24.1.0", stderr=""):
        platform = MagicMock()
        platform.run_command.return_value = CommandResult(
            return_code=return_code, stdout=stdout, stderr=stderr
        )
        return platform

    def test_validate_success(self):
        platform = self._make_platform(0, "v24.1.0")
        validator = InstallationValidator(platform)
        result = validator.validate("node --version")
        assert result.status == StepStatus.SUCCESS

    def test_validate_command_fails(self):
        platform = self._make_platform(1, "", "not found")
        validator = InstallationValidator(platform)
        result = validator.validate("node --version")
        assert result.status == StepStatus.FAILED

    def test_validate_with_version_check_ok(self):
        platform = self._make_platform(0, "v24.1.0")
        validator = InstallationValidator(platform)
        result = validator.validate("node --version", min_version="22.16")
        assert result.status == StepStatus.SUCCESS

    def test_validate_with_version_check_fail(self):
        platform = self._make_platform(0, "v18.0.0")
        validator = InstallationValidator(platform)
        result = validator.validate("node --version", min_version="22.16")
        assert result.status == StepStatus.FAILED

    def test_validate_with_retry_succeeds_second_time(self):
        platform = MagicMock()
        platform.run_command.side_effect = [
            CommandResult(return_code=1, stdout="", stderr="fail"),
            CommandResult(return_code=0, stdout="v24.1.0", stderr=""),
        ]
        validator = InstallationValidator(platform)
        result = validator.validate_with_retry("node --version", retries=1)
        assert result.status == StepStatus.SUCCESS

    def test_validate_with_retry_all_fail(self):
        platform = self._make_platform(1, "", "fail")
        validator = InstallationValidator(platform)
        result = validator.validate_with_retry("node --version", retries=2)
        assert result.status == StepStatus.FAILED
