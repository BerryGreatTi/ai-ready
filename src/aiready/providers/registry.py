"""AI provider registry with hardcoded provider definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AIProvider:
    id: str
    name_key: str
    env_var: str
    api_key_url: str
    priority: int
    is_local: bool = False


_PROVIDERS = [
    AIProvider(id="anthropic", name_key="provider.anthropic", env_var="ANTHROPIC_API_KEY",
               api_key_url="https://console.anthropic.com/settings/keys", priority=1),
    AIProvider(id="openai", name_key="provider.openai", env_var="OPENAI_API_KEY",
               api_key_url="https://platform.openai.com/api-keys", priority=2),
    AIProvider(id="gemini", name_key="provider.gemini", env_var="GOOGLE_API_KEY",
               api_key_url="https://aistudio.google.com/apikey", priority=3),
    AIProvider(id="mistral", name_key="provider.mistral", env_var="MISTRAL_API_KEY",
               api_key_url="https://console.mistral.ai/api-keys", priority=10),
    AIProvider(id="cohere", name_key="provider.cohere", env_var="CO_API_KEY",
               api_key_url="https://dashboard.cohere.com/api-keys", priority=11),
    AIProvider(id="ollama", name_key="provider.ollama", env_var="",
               api_key_url="", priority=99, is_local=True),
]


def get_providers() -> list[AIProvider]:
    return sorted(_PROVIDERS, key=lambda p: p.priority)


def get_provider_by_id(provider_id: str) -> Optional[AIProvider]:
    for p in _PROVIDERS:
        if p.id == provider_id:
            return p
    return None
