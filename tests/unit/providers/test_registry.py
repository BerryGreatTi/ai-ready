import dataclasses
import pytest
from aiready.providers.registry import AIProvider, get_providers, get_provider_by_id


class TestProviderRegistry:
    def test_provider_count(self):
        assert len(get_providers()) == 6

    def test_sorted_by_priority(self):
        providers = get_providers()
        assert providers[0].id == "anthropic"
        assert providers[1].id == "openai"
        assert providers[2].id == "gemini"
        assert providers[-1].id == "ollama"

    def test_anthropic_details(self):
        p = get_provider_by_id("anthropic")
        assert p is not None
        assert p.env_var == "ANTHROPIC_API_KEY"
        assert p.is_local is False
        assert p.priority == 1

    def test_openai_details(self):
        p = get_provider_by_id("openai")
        assert p is not None
        assert p.env_var == "OPENAI_API_KEY"
        assert p.priority == 2

    def test_gemini_details(self):
        p = get_provider_by_id("gemini")
        assert p is not None
        assert p.env_var == "GOOGLE_API_KEY"
        assert p.priority == 3

    def test_ollama_is_local(self):
        p = get_provider_by_id("ollama")
        assert p is not None
        assert p.is_local is True
        assert p.priority == 99

    def test_unknown_provider(self):
        assert get_provider_by_id("nonexistent") is None

    def test_all_non_local_have_api_key_url(self):
        for p in get_providers():
            if not p.is_local:
                assert p.api_key_url.startswith("https://")

    def test_providers_are_frozen(self):
        p = get_provider_by_id("anthropic")
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.id = "changed"

    def test_priorities_are_unique(self):
        priorities = [p.priority for p in get_providers()]
        assert len(priorities) == len(set(priorities))
