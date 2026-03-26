# tests/unit/core/test_models.py
import dataclasses
import pytest
from aiready.core.models import (
    Step, StepResult, StepStatus, InstallResult,
    Prerequisite, PrereqCheckResult,
    CommandResult, OSInfo, CommandInfo, ShellType,
)


class TestStepStatus:
    def test_status_values(self):
        assert StepStatus.RUNNING.value == "running"
        assert StepStatus.SUCCESS.value == "success"
        assert StepStatus.FAILED.value == "failed"
        assert StepStatus.SKIPPED.value == "skipped"


class TestStep:
    def test_step_is_frozen(self):
        step = Step(id="test", name_key="step.test", action=lambda: None, required=True)
        assert step.id == "test"
        assert step.required is True

    def test_step_immutable(self):
        step = Step(id="test", name_key="step.test", action=lambda: None, required=True)
        with pytest.raises(dataclasses.FrozenInstanceError):
            step.id = "changed"


class TestStepResult:
    def test_success_result(self):
        result = StepResult(status=StepStatus.SUCCESS, message="Done", detail=None)
        assert result.status == StepStatus.SUCCESS
        assert result.failed is False

    def test_failed_result(self):
        result = StepResult(status=StepStatus.FAILED, message="Error", detail="stack trace")
        assert result.failed is True

    def test_skipped_result(self):
        result = StepResult(status=StepStatus.SKIPPED, message="Not needed", detail=None)
        assert result.failed is False

    def test_default_none_fields(self):
        result = StepResult(status=StepStatus.SUCCESS)
        assert result.message is None
        assert result.detail is None


class TestInstallResult:
    def test_success(self):
        result = InstallResult(success=True)
        assert result.success is True
        assert result.failed_step is None

    def test_failure(self):
        step = Step(id="x", name_key="x", action=lambda: None, required=True)
        error = StepResult(status=StepStatus.FAILED, message="err", detail=None)
        result = InstallResult(success=False, failed_step=step, error=error)
        assert result.success is False
        assert result.failed_step.id == "x"


class TestPrerequisite:
    def test_prerequisite_fields(self):
        p = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        assert p.name == "nodejs"
        assert p.min_version == "22.16"

    def test_prerequisite_immutable(self):
        p = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.name = "changed"


class TestPrereqCheckResult:
    def test_installed_ok(self):
        p = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        r = PrereqCheckResult(prereq=p, installed=True, current_version="24.1.0", needs_upgrade=False)
        assert r.installed is True
        assert r.needs_upgrade is False

    def test_needs_upgrade(self):
        p = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        r = PrereqCheckResult(prereq=p, installed=True, current_version="18.0.0", needs_upgrade=True)
        assert r.needs_upgrade is True

    def test_not_installed(self):
        p = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        r = PrereqCheckResult(prereq=p, installed=False)
        assert r.installed is False
        assert r.current_version is None


class TestCommandResult:
    def test_success(self):
        r = CommandResult(return_code=0, stdout="v24.1.0", stderr="")
        assert r.succeeded is True

    def test_failure(self):
        r = CommandResult(return_code=1, stdout="", stderr="not found")
        assert r.succeeded is False


class TestOSInfo:
    def test_os_info(self):
        info = OSInfo(system="Windows", release="10", version="10.0.19041", arch="AMD64")
        assert info.system == "Windows"


class TestCommandInfo:
    def test_command_info(self):
        info = CommandInfo(path="/usr/bin/node", version="24.1.0")
        assert info.path == "/usr/bin/node"

    def test_command_info_no_version(self):
        info = CommandInfo(path="/usr/bin/node")
        assert info.version is None


class TestShellType:
    def test_shell_values(self):
        assert ShellType.BASH.value == "bash"
        assert ShellType.ZSH.value == "zsh"
        assert ShellType.POWERSHELL.value == "powershell"
        assert ShellType.CMD.value == "cmd"
