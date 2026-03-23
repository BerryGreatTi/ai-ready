"""Tests for Tool ABC and OnboardingConfig."""
from __future__ import annotations

import pytest

from aiready.tools.base import OnboardingConfig, OnboardingMode, Tool


class TestOnboardingMode:
    def test_has_automatic_value(self):
        assert OnboardingMode.AUTOMATIC.value == "automatic"

    def test_has_guided_value(self):
        assert OnboardingMode.GUIDED.value == "guided"

    def test_only_two_members(self):
        assert len(list(OnboardingMode)) == 2


class TestOnboardingConfig:
    def test_is_frozen(self):
        config = OnboardingConfig(mode=OnboardingMode.GUIDED)
        with pytest.raises((AttributeError, TypeError)):
            config.mode = OnboardingMode.AUTOMATIC  # type: ignore[misc]

    def test_default_provider_selection_false(self):
        config = OnboardingConfig(mode=OnboardingMode.GUIDED)
        assert config.provider_selection is False

    def test_default_api_key_input_false(self):
        config = OnboardingConfig(mode=OnboardingMode.GUIDED)
        assert config.api_key_input is False

    def test_can_set_provider_selection_true(self):
        config = OnboardingConfig(mode=OnboardingMode.AUTOMATIC, provider_selection=True)
        assert config.provider_selection is True

    def test_can_set_api_key_input_true(self):
        config = OnboardingConfig(mode=OnboardingMode.AUTOMATIC, api_key_input=True)
        assert config.api_key_input is True


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
        """A partial implementation missing methods cannot be instantiated."""

        class PartialTool(Tool):
            def get_name(self):
                return "partial"

        with pytest.raises(TypeError):
            PartialTool()  # type: ignore[abstract]

    def test_full_concrete_subclass_can_be_instantiated(self):
        """A complete implementation can be instantiated."""

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
                return OnboardingConfig(mode=OnboardingMode.GUIDED)

        tool = ConcreteTool()
        assert tool.get_name() == "concrete"
