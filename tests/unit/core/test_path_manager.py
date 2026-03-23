"""Tests for PathManager: check, add, refresh."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aiready.core.path_manager import PathManager


@pytest.fixture
def mock_platform() -> MagicMock:
    platform = MagicMock()
    platform.add_to_path.return_value = True
    return platform


@pytest.fixture
def manager(mock_platform: MagicMock) -> PathManager:
    return PathManager(mock_platform)


class TestCheck:
    def test_check_finds_command(self, manager: PathManager) -> None:
        with patch("aiready.core.path_manager.shutil.which", return_value="/usr/bin/python3"):
            result = manager.check("python3")
        assert result == "/usr/bin/python3"

    def test_check_not_found(self, manager: PathManager) -> None:
        with patch("aiready.core.path_manager.shutil.which", return_value=None):
            result = manager.check("nonexistent-tool")
        assert result is None


class TestAdd:
    def test_add_delegates_to_platform(
        self, manager: PathManager, mock_platform: MagicMock
    ) -> None:
        new_path = Path("/usr/local/bin")
        # Ensure this path is NOT in PATH
        with patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}, clear=False):
            result = manager.add(new_path)

        mock_platform.add_to_path.assert_called_once_with(new_path)
        assert result is True

    def test_add_skips_if_already_in_path(
        self, manager: PathManager, mock_platform: MagicMock
    ) -> None:
        new_path = Path("/usr/local/bin")
        with patch.dict(os.environ, {"PATH": "/usr/local/bin:/usr/bin"}, clear=False):
            result = manager.add(new_path)

        mock_platform.add_to_path.assert_not_called()
        assert result is True


class TestRefreshSession:
    def test_refresh_session(self, manager: PathManager) -> None:
        new_path = "/opt/custom/bin"
        original_path = "/usr/bin:/bin"
        with patch.dict(os.environ, {"PATH": original_path}, clear=False):
            manager.refresh_session(new_path)
            updated = os.environ["PATH"]

        assert new_path in updated
        assert original_path in updated

    def test_refresh_session_no_duplicate(self, manager: PathManager) -> None:
        new_path = "/usr/bin"
        with patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}, clear=False):
            manager.refresh_session(new_path)
            updated = os.environ["PATH"]

        # Should not add again; count should be same as before
        assert updated.count(new_path) == 1
