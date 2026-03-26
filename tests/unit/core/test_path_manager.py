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
        new_path = Path("some_unique_test_path")
        with patch.dict(os.environ, {"PATH": f"other_path_a{os.pathsep}other_path_b"}, clear=False):
            result = manager.add(new_path)

        mock_platform.add_to_path.assert_called_once_with(new_path)
        assert result is True

    def test_add_skips_if_already_in_path(
        self, manager: PathManager, mock_platform: MagicMock
    ) -> None:
        target = "already_in_path_dir"
        new_path = Path(target)
        path_value = f"{target}{os.pathsep}other_path"
        with patch.dict(os.environ, {"PATH": path_value}, clear=False):
            result = manager.add(new_path)

        mock_platform.add_to_path.assert_not_called()
        assert result is True


class TestRefreshSession:
    def test_refresh_session(self, manager: PathManager) -> None:
        new_path = "/opt/custom/bin"
        original_path = f"/usr/bin{os.pathsep}/bin"
        with patch.dict(os.environ, {"PATH": original_path}, clear=False):
            manager.refresh_session(new_path)
            updated = os.environ["PATH"]

        assert new_path in updated
        assert "/usr/bin" in updated

    def test_refresh_session_no_duplicate(self, manager: PathManager) -> None:
        new_path = "/usr/bin"
        with patch.dict(os.environ, {"PATH": f"/usr/bin{os.pathsep}/bin"}, clear=False):
            manager.refresh_session(new_path)
            updated = os.environ["PATH"]

        # Should not add again; count should be same as before
        assert updated.count(new_path) == 1
