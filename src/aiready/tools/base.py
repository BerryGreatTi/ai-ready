"""Abstract base class for installable tools."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from aiready.core.models import Prerequisite, Step
from aiready.platforms.base import Platform


class OnboardingMode(Enum):
    AUTOMATIC = "automatic"


@dataclass(frozen=True)
class OnboardingConfig:
    mode: OnboardingMode


class Tool(ABC):
    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_prerequisites(self, platform: Platform) -> list[Prerequisite]: ...

    @abstractmethod
    def get_steps(self, platform: Platform) -> list[Step]: ...

    @abstractmethod
    def get_verify_commands(self) -> list[str]: ...

    @abstractmethod
    def get_onboarding_config(self) -> OnboardingConfig: ...
