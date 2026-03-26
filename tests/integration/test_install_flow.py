"""Integration tests for the full installation flow."""
from __future__ import annotations

from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import pytest

from aiready.core.installer import Installer
from aiready.core.models import (
    CommandInfo,
    CommandResult,
    InstallResult,
    OSInfo,
    PrereqCheckResult,
    ShellType,
    StepResult,
    StepStatus,
)
from aiready.i18n.strings import I18n
from aiready.platforms.base import Platform
from aiready.tools.claude_code import ClaudeCodeTool
from aiready.tools.openclaw import OpenClawTool
from aiready.core.models import Prerequisite


class MockPlatform(Platform):
    """Concrete Platform implementation where all operations succeed."""

    def get_os_info(self) -> OSInfo:
        return OSInfo(system="Linux", release="6.0", version="6.0.0", arch="x86_64")

    def check_command(self, command: str) -> Optional[CommandInfo]:
        return CommandInfo(path=f"/usr/bin/{command}", version="99.0.0")

    def install_prerequisite(self, prereq: Prerequisite) -> InstallResult:
        return InstallResult(success=True)

    def verify_prerequisite(self, prereq: Prerequisite) -> PrereqCheckResult:
        return PrereqCheckResult(prereq=prereq, installed=True, current_version="99.0.0")

    def add_to_path(self, path: Path) -> bool:
        return True

    def request_elevation(self, reason_key: str) -> bool:
        return True

    def run_command(self, cmd: list[str], elevated: bool = False, timeout: int = 120) -> CommandResult:
        return CommandResult(return_code=0, stdout="OK", stderr="")

    def get_temp_dir(self) -> Path:
        return Path("/tmp/aiready-test")

    def open_browser(self, url: str) -> bool:
        return True

    def get_shell_type(self) -> ShellType:
        return ShellType.BASH


class FailingCheckSystemPlatform(MockPlatform):
    """Platform where the first run_command (check_system) fails."""

    def __init__(self) -> None:
        self._call_count = 0

    def run_command(self, cmd: list[str], elevated: bool = False, timeout: int = 120) -> CommandResult:
        # First call is check_system - make it succeed but we simulate failure
        # by making check_command return None for the verify step
        return CommandResult(return_code=1, stdout="", stderr="system check failed")

    def check_command(self, command: str) -> Optional[CommandInfo]:
        return None


def _make_i18n() -> I18n:
    return I18n(language="en")


class TestClaudeCodeFullFlow:
    def test_claude_code_full_flow_success(self):
        platform = MockPlatform()
        i18n = _make_i18n()
        tool = ClaudeCodeTool(platform=platform, i18n=i18n)
        installer = Installer(platform=platform, tool=tool, i18n=i18n)

        result = installer.run()

        assert result.success is True
        assert result.failed_step is None

    def test_claude_code_full_flow_all_steps_executed(self):
        platform = MockPlatform()
        i18n = _make_i18n()
        tool = ClaudeCodeTool(platform=platform, i18n=i18n)
        installer = Installer(platform=platform, tool=tool, i18n=i18n)

        executed_step_ids: list[str] = []

        def on_progress(index, step, result):
            if result.status == StepStatus.SUCCESS:
                executed_step_ids.append(step.id)

        installer.run(on_progress=on_progress)

        steps = tool.get_steps(platform)
        for step in steps:
            assert step.id in executed_step_ids, f"Step {step.id!r} was not executed"


class TestOpenClawFullFlow:
    def test_openclaw_full_flow_success(self):
        platform = MockPlatform()
        i18n = _make_i18n()
        tool = OpenClawTool(platform=platform, i18n=i18n)
        installer = Installer(platform=platform, tool=tool, i18n=i18n)

        result = installer.run()

        assert result.success is True
        assert result.failed_step is None

    def test_openclaw_full_flow_all_steps_executed(self):
        platform = MockPlatform()
        i18n = _make_i18n()
        tool = OpenClawTool(platform=platform, i18n=i18n)
        installer = Installer(platform=platform, tool=tool, i18n=i18n)

        executed_step_ids: list[str] = []

        def on_progress(index, step, result):
            if result.status == StepStatus.SUCCESS:
                executed_step_ids.append(step.id)

        installer.run(on_progress=on_progress)

        steps = tool.get_steps(platform)
        for step in steps:
            assert step.id in executed_step_ids, f"Step {step.id!r} was not executed"


class TestFlowAbortOnFailure:
    def test_flow_aborts_on_system_check_failure(self):
        """When check_system fails and is required, installation aborts early."""

        class SystemCheckFailPlatform(MockPlatform):
            def run_command(self, cmd: list[str], elevated: bool = False, timeout: int = 120) -> CommandResult:
                # Fail all run_command calls to ensure check_system fails
                return CommandResult(return_code=1, stdout="", stderr="error")

            def check_command(self, command: str) -> Optional[CommandInfo]:
                return None

        platform = SystemCheckFailPlatform()
        i18n = _make_i18n()

        # ClaudeCodeTool: check_system calls run_command - with return_code=1,
        # check_system returns SUCCESS (it's a soft check). But verify_install
        # calls check_command which returns None -> FAILED and required=True.
        # We need a tool that marks check_system as hard-failed.
        # Use a custom tool to test abort logic directly.
        from aiready.core.models import Step
        from aiready.tools.base import OnboardingConfig, OnboardingMode, Tool

        class AbortingTool(Tool):
            def get_name(self):
                return "AbortTest"

            def get_prerequisites(self, platform):
                return []

            def get_steps(self, platform):
                return [
                    Step(
                        id="check_system",
                        name_key="step.check_system",
                        action=lambda: StepResult(
                            status=StepStatus.FAILED, message="System check failed"
                        ),
                        required=True,
                    ),
                    Step(
                        id="install_tool",
                        name_key="step.install_tool",
                        action=lambda: StepResult(status=StepStatus.SUCCESS),
                        required=True,
                    ),
                ]

            def get_verify_commands(self):
                return []

            def get_onboarding_config(self):
                return OnboardingConfig(mode=OnboardingMode.AUTOMATIC)

        tool = AbortingTool()
        installer = Installer(platform=platform, tool=tool, i18n=i18n)

        result = installer.run()

        assert result.success is False
        assert result.failed_step is not None
        assert result.failed_step.id == "check_system"

    def test_abort_does_not_run_subsequent_steps(self):
        """Steps after a required failure are not executed."""
        from aiready.core.models import Step
        from aiready.tools.base import OnboardingConfig, OnboardingMode, Tool

        executed: list[str] = []

        class FailFirstTool(Tool):
            def get_name(self):
                return "FailFirst"

            def get_prerequisites(self, platform):
                return []

            def get_steps(self, platform):
                return [
                    Step(
                        id="check_system",
                        name_key="step.check_system",
                        action=lambda: StepResult(
                            status=StepStatus.FAILED, message="fail"
                        ),
                        required=True,
                    ),
                    Step(
                        id="install_tool",
                        name_key="step.install_tool",
                        action=lambda: (
                            executed.append("install_tool"),
                            StepResult(status=StepStatus.SUCCESS),
                        )[-1],
                        required=True,
                    ),
                ]

            def get_verify_commands(self):
                return []

            def get_onboarding_config(self):
                return OnboardingConfig(mode=OnboardingMode.AUTOMATIC)

        platform = MockPlatform()
        i18n = _make_i18n()
        tool = FailFirstTool()
        installer = Installer(platform=platform, tool=tool, i18n=i18n)

        result = installer.run()

        assert result.success is False
        assert "install_tool" not in executed


class TestProgressCallback:
    def test_progress_callback_receives_all_steps(self):
        """Each step receives exactly RUNNING then SUCCESS callback invocations."""
        platform = MockPlatform()
        i18n = _make_i18n()
        tool = ClaudeCodeTool(platform=platform, i18n=i18n)
        installer = Installer(platform=platform, tool=tool, i18n=i18n)

        steps = tool.get_steps(platform)
        invocations: list[tuple[str, StepStatus]] = []

        def on_progress(index, step, result):
            invocations.append((step.id, result.status))

        installer.run(on_progress=on_progress)

        # Each step should have a RUNNING then a terminal status
        for step in steps:
            step_calls = [(sid, status) for sid, status in invocations if sid == step.id]
            assert len(step_calls) == 2, (
                f"Step {step.id!r} should receive 2 callbacks, got {len(step_calls)}"
            )
            assert step_calls[0][1] == StepStatus.RUNNING
            assert step_calls[1][1] in (
                StepStatus.SUCCESS, StepStatus.FAILED, StepStatus.SKIPPED
            )

    def test_openclaw_progress_callback_receives_all_steps(self):
        """Each OpenClaw step receives RUNNING then a terminal status."""
        platform = MockPlatform()
        i18n = _make_i18n()
        tool = OpenClawTool(platform=platform, i18n=i18n)
        installer = Installer(platform=platform, tool=tool, i18n=i18n)

        steps = tool.get_steps(platform)
        invocations: list[tuple[str, StepStatus]] = []

        def on_progress(index, step, result):
            invocations.append((step.id, result.status))

        installer.run(on_progress=on_progress)

        for step in steps:
            step_calls = [(sid, status) for sid, status in invocations if sid == step.id]
            assert len(step_calls) == 2, (
                f"Step {step.id!r} should receive 2 callbacks, got {len(step_calls)}"
            )
            assert step_calls[0][1] == StepStatus.RUNNING
