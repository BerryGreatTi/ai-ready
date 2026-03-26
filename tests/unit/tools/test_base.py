"""Tests for Tool ABC and OnboardingConfig."""
from __future__ import annotations

import pytest

from aiready.tools.base import OnboardingConfig, OnboardingMode, Tool


class TestOnboardingMode:
    def test_has_automatic_value(self):
        assert OnboardingMode.AUTOMATIC.value == "automatic"

    def test_only_one_member(self):
        assert len(list(OnboardingMode)) == 1


class TestOnboardingConfig:
    def test_is_frozen(self):
        config = OnboardingConfig(mode=OnboardingMode.AUTOMATIC)
        with pytest.raises((AttributeError, TypeError)):
            config.mode = OnboardingMode.AUTOMATIC  # type: ignore[misc]


class TestToolABC:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            Tool()  # type: ignore[abstract]

    def test_has_get_name_abstract_method(self):
        assert hasattr(Tool, "get_name")
        assert getattr(Tool.get_name, "__isabstractmethod__", False)

    def test_has_get_prerequisites_abstract_method(self):
        assert hasattr(Tool, "get_prerequisites")
        assert getattr(Tool.get_prerequisites, "__isabstractmethod__", False)

    def test_has_get_steps_abstract_method(self):
        assert hasattr(Tool, "get_steps")
        assert getattr(Tool.get_steps, "__isabstractmethod__", False)

    def test_has_get_verify_commands_abstract_method(self):
        assert hasattr(Tool, "get_verify_commands")
        assert getattr(Tool.get_verify_commands, "__isabstractmethod__", False)

    def test_has_get_onboarding_config_abstract_method(self):
        assert hasattr(Tool, "get_onboarding_config")
        assert getattr(Tool.get_onboarding_config, "__isabstractmethod__", False)

    def test_concrete_subclass_must_implement_all_methods(self):
        class PartialTool(Tool):
            def get_name(self):
                return "partial"

        with pytest.raises(TypeError):
            PartialTool()  # type: ignore[abstract]

    def test_full_concrete_subclass_can_be_instantiated(self):
        class ConcreteTool(Tool):
            def get_name(self):
                return "concrete"

            def get_prerequisites(self, platform):
                return []

            def get_steps(self, platform):
                return []

            def get_verify_commands(self):
                return []

            def get_onboarding_config(self):
                return OnboardingConfig(mode=OnboardingMode.AUTOMATIC)

        tool = ConcreteTool()
        assert tool.get_name() == "concrete"
