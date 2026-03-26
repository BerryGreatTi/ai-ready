"""Permission management for installation operations."""
from __future__ import annotations
from aiready.platforms.base import Platform

ELEVATED_OPERATIONS = frozenset({"install_package", "write_system_dir"})


class PermissionManager:
    def __init__(self, platform: Platform):
        self._platform = platform

    def needs_elevation(self, operation: str) -> bool:
        return operation in ELEVATED_OPERATIONS

    def request_if_needed(self, operation: str, reason_key: str) -> bool:
        if not self.needs_elevation(operation):
            return True
        return self._platform.request_elevation(reason_key)
