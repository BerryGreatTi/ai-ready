"""Installation orchestration engine."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional

from aiready.core.models import InstallResult, Step, StepResult, StepStatus
from aiready.core.logger import InstallLogger
from aiready.i18n.strings import I18n
from aiready.platforms.base import Platform

if TYPE_CHECKING:
    from aiready.tools.base import Tool


ProgressCallback = Callable[[int, Step, StepResult], None]


class Installer:
    def __init__(
        self,
        platform: Platform,
        tool: "Tool",
        i18n: I18n,
        logger: Optional[InstallLogger] = None,
    ):
        self._platform = platform
        self._tool = tool
        self._i18n = i18n
        self._logger = logger

    def run(self, on_progress: Optional[ProgressCallback] = None) -> InstallResult:
        steps: List[Step] = self._tool.get_steps(self._platform)
        tool_name = self._tool.get_name()
        if self._logger:
            self._logger.debug("installer", f"Starting {tool_name} with {len(steps)} steps")
            import os
            self._logger.debug("installer", f"PATH={os.environ.get('PATH', 'NOT SET')}")
        for i, step in enumerate(steps):
            if on_progress:
                on_progress(i, step, StepResult(status=StepStatus.RUNNING))
            if self._logger:
                self._logger.info(step.id, self._i18n.get(step.name_key, tool=tool_name))
            result = step.action()
            if self._logger:
                self._logger.debug(step.id, f"result={result.status.value} message={result.message or ''} detail={result.detail or ''}")
            if on_progress:
                on_progress(i, step, result)
            if self._logger and result.failed:
                self._logger.error(step.id, result.message or "Failed")
            if result.failed and step.required:
                return InstallResult(success=False, failed_step=step, error=result)
        return InstallResult(success=True)
