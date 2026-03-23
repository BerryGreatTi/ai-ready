"""Prerequisite detection and version checking."""
from __future__ import annotations
from aiready.core.models import Prerequisite, PrereqCheckResult
from aiready.core.version import version_gte
from aiready.platforms.base import Platform


class PrerequisiteChecker:
    def __init__(self, platform: Platform):
        self._platform = platform

    def check(self, prereq: Prerequisite) -> PrereqCheckResult:
        command = prereq.check_command.split()[0]
        cmd_info = self._platform.check_command(command)
        if cmd_info is None:
            return PrereqCheckResult(prereq=prereq, installed=False)
        current = cmd_info.version
        needs_upgrade = not version_gte(current, prereq.min_version) if current else True
        return PrereqCheckResult(
            prereq=prereq, installed=True,
            current_version=current, needs_upgrade=needs_upgrade,
        )

    def check_all(self, prereqs: list[Prerequisite]) -> list[PrereqCheckResult]:
        return [self.check(p) for p in prereqs]
