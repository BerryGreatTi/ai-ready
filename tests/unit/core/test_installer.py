"""Tests for Installer orchestration engine."""
from __future__ import annotations

from typing import List
from unittest.mock import MagicMock, call

import pytest

from aiready.core.installer import Installer, ProgressCallback
from aiready.core.models import InstallResult, Step, StepResult, StepStatus
from aiready.i18n.strings import I18n


def _make_step(step_id: str, required: bool = True, status: StepStatus = StepStatus.SUCCESS) -> Step:
    result = StepResult(status=status)
    return Step(
        id=step_id,
        name_key=f"step.{step_id}",
        action=lambda r=result: r,
        required=required,
    )


def _make_installer(steps: list[Step]) -> tuple[Installer, MagicMock]:
    platform = MagicMock()
    tool = MagicMock()
    tool.get_steps.return_value = steps
    i18n = I18n()
    installer = Installer(platform=platform, tool=tool, i18n=i18n)
    return installer, tool


class TestRunAllStepsSucceed:
    def test_run_all_steps_succeed(self) -> None:
        steps = [
            _make_step("step1"),
            _make_step("step2"),
            _make_step("step3"),
        ]
        installer, _ = _make_installer(steps)
        result = installer.run()

        assert result.success is True
        assert result.failed_step is None
        assert result.error is None


class TestRunAbortsOnRequiredFailure:
    def test_run_aborts_on_required_failure(self) -> None:
        step3_action = MagicMock(return_value=StepResult(status=StepStatus.SUCCESS))
        step3 = Step(id="step3", name_key="step.step3", action=step3_action, required=True)

        steps = [
            _make_step("step1"),
            _make_step("step2", required=True, status=StepStatus.FAILED),
            step3,
        ]
        installer, _ = _make_installer(steps)
        result = installer.run()

        assert result.success is False
        assert result.failed_step is not None
        assert result.failed_step.id == "step2"
        step3_action.assert_not_called()


class TestRunContinuesOnOptionalFailure:
    def test_run_continues_on_optional_failure(self) -> None:
        step3_action = MagicMock(return_value=StepResult(status=StepStatus.SUCCESS))
        step3 = Step(id="step3", name_key="step.step3", action=step3_action, required=True)

        steps = [
            _make_step("step1"),
            _make_step("step2", required=False, status=StepStatus.FAILED),
            step3,
        ]
        installer, _ = _make_installer(steps)
        result = installer.run()

        assert result.success is True
        step3_action.assert_called_once()


class TestProgressCallback:
    def test_progress_callback_receives_all_updates(self) -> None:
        steps = [
            _make_step("step1"),
            _make_step("step2"),
        ]
        installer, _ = _make_installer(steps)
        received: list[tuple[int, Step, StepResult]] = []

        def on_progress(index: int, step: Step, result: StepResult) -> None:
            received.append((index, step, result))

        installer.run(on_progress=on_progress)

        # Each step should receive RUNNING then final result
        assert len(received) == 4
        # step1 RUNNING
        assert received[0][0] == 0
        assert received[0][2].status == StepStatus.RUNNING
        # step1 SUCCESS
        assert received[1][0] == 0
        assert received[1][2].status == StepStatus.SUCCESS
        # step2 RUNNING
        assert received[2][0] == 1
        assert received[2][2].status == StepStatus.RUNNING
        # step2 SUCCESS
        assert received[3][0] == 1
        assert received[3][2].status == StepStatus.SUCCESS


class TestEmptySteps:
    def test_empty_steps_returns_success(self) -> None:
        installer, _ = _make_installer([])
        result = installer.run()

        assert result.success is True
