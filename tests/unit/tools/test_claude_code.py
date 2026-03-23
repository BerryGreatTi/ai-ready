"""Tests for ClaudeCodeTool."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from aiready.core.models import OSInfo
from aiready.tools.base import OnboardingMode
from aiready.tools.claude_code import ClaudeCodeTool


def _make_platform(system: str = "Linux") -> MagicMock:
    platform = MagicMock()
    platform.get_os_info.return_value = OSInfo(
        system=system,
        release="6.0",
        version="6.0.0",
        arch="x86_64",
    )
    return platform


def _make_tool(platform: MagicMock | None = None) -> ClaudeCodeTool:
    if platform is None:
        platform = _make_platform()
    i18n = MagicMock()
    i18n.get.side_effect = lambda key, **kwargs: key
    return ClaudeCodeTool(platform=platform, i18n=i18n)


class TestClaudeCodeToolName:
    def test_get_name(self):
        tool = _make_tool()
        assert tool.get_name() == "Claude Code"


class TestClaudeCodePrerequisites:
    def test_prerequisites_empty_on_linux(self):
        platform = _make_platform(system="Linux")
        tool = _make_tool(platform)
        prereqs = tool.get_prerequisites(platform)
        assert prereqs == []

    def test_prerequisites_empty_on_macos(self):
        platform = _make_platform(system="Darwin")
        tool = _make_tool(platform)
        prereqs = tool.get_prerequisites(platform)
        assert prereqs == []

    def test_prerequisites_git_on_windows(self):
        platform = _make_platform(system="Windows")
        tool = _make_tool(platform)
        prereqs = tool.get_prerequisites(platform)
        assert len(prereqs) == 1
        assert prereqs[0].name == "git"
        assert prereqs[0].min_version == "2.0"
        assert prereqs[0].check_command == "git --version"


class TestClaudeCodeSteps:
    EXPECTED_STEP_IDS = [
        "check_system",
        "install_prereqs",
        "verify_prereqs",
        "install_tool",
        "verify_install",
        "run_doctor",
        "authenticate",
        "verify_auth",
    ]

    def test_steps_count(self):
        platform = _make_platform()
        tool = _make_tool(platform)
        steps = tool.get_steps(platform)
        assert len(steps) == 8

    def test_step_ids(self):
        platform = _make_platform()
        tool = _make_tool(platform)
        steps = tool.get_steps(platform)
        step_ids = [s.id for s in steps]
        assert step_ids == self.EXPECTED_STEP_IDS

    def test_steps_are_callable(self):
        platform = _make_platform()
        tool = _make_tool(platform)
        steps = tool.get_steps(platform)
        for step in steps:
            assert callable(step.action)

    def test_steps_have_name_keys(self):
        platform = _make_platform()
        tool = _make_tool(platform)
        steps = tool.get_steps(platform)
        for step in steps:
            assert isinstance(step.name_key, str)
            assert len(step.name_key) > 0

    def test_check_system_is_required(self):
        platform = _make_platform()
        tool = _make_tool(platform)
        steps = tool.get_steps(platform)
        check_step = next(s for s in steps if s.id == "check_system")
        assert check_step.required is True


class TestClaudeCodeOnboarding:
    def test_onboarding_is_guided(self):
        tool = _make_tool()
        config = tool.get_onboarding_config()
        assert config.mode == OnboardingMode.GUIDED

    def test_onboarding_no_provider_selection(self):
        tool = _make_tool()
        config = tool.get_onboarding_config()
        assert config.provider_selection is False

    def test_onboarding_no_api_key_input(self):
        tool = _make_tool()
        config = tool.get_onboarding_config()
        assert config.api_key_input is False


class TestClaudeCodeVerifyCommands:
    def test_verify_commands(self):
        tool = _make_tool()
        cmds = tool.get_verify_commands()
        assert "claude --version" in cmds
        assert "claude doctor" in cmds

    def test_verify_commands_count(self):
        tool = _make_tool()
        cmds = tool.get_verify_commands()
        assert len(cmds) == 2
