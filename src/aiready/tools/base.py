"""Abstract base class for installable tools."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from aiready.core.models import Step
from aiready.platforms.base import Platform


class Tool(ABC):
    @abstractmethod
    def get_steps(self, platform: Platform) -> List[Step]: ...
