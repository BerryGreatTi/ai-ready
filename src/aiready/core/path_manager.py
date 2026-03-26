"""PATH management: check, add, refresh."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional

from aiready.platforms.base import Platform


class PathManager:
    def __init__(self, platform: Platform):
        self._platform = platform

    def check(self, command: str) -> Optional[str]:
        return shutil.which(command)

    def add(self, path: Path) -> bool:
        path_str = str(path)
        if path_str in os.environ.get("PATH", ""):
            return True
        return self._platform.add_to_path(path)

    def refresh_session(self, new_path: str) -> None:
        current = os.environ.get("PATH", "")
        if new_path not in current:
            os.environ["PATH"] = f"{new_path}{os.pathsep}{current}"
