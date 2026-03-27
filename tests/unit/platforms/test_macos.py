# tests/unit/platforms/test_macos.py
"""Tests for MacOSPlatform - all system calls are mocked (running on Linux)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch, call

import pytest

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="macOS platform tests not applicable on Windows")

from aiready.core.models import (
    CommandInfo,
    CommandResult,
    InstallResult,
    OSInfo,
    Prerequisite,
    PrereqCheckResult,
    ShellType,
)
from aiready.platforms.macos import MacOSPlatform


@pytest.fixture
def platform():
    return MacOSPlatform()


@pytest.fixture
def nodejs_prereq():
    return Prerequisite(name="nodejs", min_version="18.0.0", check_command="node")


# ---------------------------------------------------------------------------
# get_os_info
# ---------------------------------------------------------------------------


class TestGetOsInfo:
    def test_returns_osinfo(self, platform):
        with patch("aiready.platforms.macos.platform_module") as mock_plat:
            mock_plat.system.return_value = "Darwin"
            mock_plat.release.return_value = "23.0.0"
            mock_plat.version.return_value = "Darwin Kernel Version 23.0.0"
            mock_plat.machine.return_value = "arm64"

            result = platform.get_os_info()

        assert isinstance(result, OSInfo)
        assert result.system == "Darwin"
        assert result.release == "23.0.0"
        assert result.arch == "arm64"

    def test_version_and_release(self, platform):
        with patch("aiready.platforms.macos.platform_module") as mock_plat:
            mock_plat.system.return_value = "Darwin"
            mock_plat.release.return_value = "22.6.0"
            mock_plat.version.return_value = "Monterey"
            mock_plat.machine.return_value = "x86_64"

            result = platform.get_os_info()

        assert result.version == "Monterey"
        assert result.release == "22.6.0"


# ---------------------------------------------------------------------------
# check_command
# ---------------------------------------------------------------------------


class TestCheckCommand:
    def test_returns_commandinfo_when_found(self, platform):
        mock_result = CommandResult(return_code=0, stdout="node v20.5.0\n", stderr="")
        with patch("shutil.which", return_value="/usr/local/bin/node"), patch(
            "aiready.platforms.macos.run_process", return_value=mock_result
        ):
            result = platform.check_command("node")

        assert isinstance(result, CommandInfo)
        assert result.path == "/usr/local/bin/node"
        assert result.version == "node v20.5.0"

    def test_returns_none_when_not_found(self, platform):
        with patch("shutil.which", return_value=None):
            result = platform.check_command("node")

        assert result is None

    def test_version_from_stderr(self, platform):
        mock_result = CommandResult(return_code=0, stdout="", stderr="git version 2.42.0\n")
        with patch("shutil.which", return_value="/usr/bin/git"), patch(
            "aiready.platforms.macos.run_process", return_value=mock_result
        ):
            result = platform.check_command("git")

        assert isinstance(result, CommandInfo)
        assert "2.42.0" in result.version

    def test_version_none_on_process_error(self, platform):
        mock_result = CommandResult(return_code=-1, stdout="", stderr="Command not found")
        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "aiready.platforms.macos.run_process", return_value=mock_result
        ):
            result = platform.check_command("node")

        assert isinstance(result, CommandInfo)
        assert result.version is None


# ---------------------------------------------------------------------------
# install_prerequisite
# ---------------------------------------------------------------------------


class TestInstallPrerequisite:
    def test_nodejs_install_via_brew_success(self, platform, nodejs_prereq):
        brew_info = CommandInfo(path="/usr/local/bin/brew", version="4.1.0")
        success = CommandResult(return_code=0, stdout="", stderr="")
        with patch.object(platform, "check_command", return_value=brew_info), patch(
            "aiready.platforms.macos.run_process_live", return_value=success
        ), patch.object(platform, "_refresh_path"):
            result = platform.install_prerequisite(nodejs_prereq)

        assert isinstance(result, InstallResult)
        assert result.success is True

    def test_nodejs_install_brew_failure(self, platform, nodejs_prereq):
        brew_info = CommandInfo(path="/usr/local/bin/brew", version="4.1.0")
        fail = CommandResult(return_code=1, stdout="", stderr="Error: brew install failed")
        with patch.object(platform, "check_command", return_value=brew_info), patch(
            "aiready.platforms.macos.run_process_live", return_value=fail
        ):
            result = platform.install_prerequisite(nodejs_prereq)

        assert isinstance(result, InstallResult)
        assert result.success is False
        assert result.error is not None
        assert "brew install" in result.error.message

    def test_nodejs_install_without_brew(self, platform, nodejs_prereq):
        success = CommandResult(return_code=0, stdout="", stderr="")
        with patch.object(platform, "check_command", return_value=None), patch(
            "aiready.platforms.macos.run_process_live", return_value=success
        ), patch.object(platform, "_refresh_path"):
            result = platform.install_prerequisite(nodejs_prereq)

        assert isinstance(result, InstallResult)
        assert result.success is True

    def test_unknown_prereq_returns_failure(self, platform):
        prereq = Prerequisite(name="unknowntool", min_version="1.0.0", check_command="unknowntool")
        result = platform.install_prerequisite(prereq)
        assert isinstance(result, InstallResult)
        assert result.success is False

    def test_git_install_via_brew_success(self, platform):
        git_prereq = Prerequisite(name="git", min_version="2.0", check_command="git --version")
        brew_info = CommandInfo(path="/usr/local/bin/brew", version="4.1.0")
        success = CommandResult(return_code=0, stdout="", stderr="")
        with patch.object(platform, "check_command", return_value=brew_info), patch(
            "aiready.platforms.macos.run_process_live", return_value=success
        ), patch.object(platform, "_refresh_path"):
            result = platform.install_prerequisite(git_prereq)

        assert result.success is True

    def test_git_install_via_brew_failure_returns_error(self, platform):
        git_prereq = Prerequisite(name="git", min_version="2.0", check_command="git --version")
        brew_info = CommandInfo(path="/usr/local/bin/brew", version="4.1.0")
        fail = CommandResult(return_code=1, stdout="", stderr="Error: brew install git failed")
        with patch.object(platform, "check_command", return_value=brew_info), patch(
            "aiready.platforms.macos.run_process_live", return_value=fail
        ):
            result = platform.install_prerequisite(git_prereq)

        assert result.success is False
        assert result.error is not None
        assert "brew install git failed" in result.error.message

    def test_git_install_xcode_polls_until_available(self, platform):
        git_prereq = Prerequisite(name="git", min_version="2.0", check_command="git --version")
        trigger_result = CommandResult(return_code=0, stdout="", stderr="")
        # check_command returns None (no brew), run_process triggers xcode dialog
        with patch.object(platform, "check_command", return_value=None), patch(
            "aiready.platforms.macos.run_process", return_value=trigger_result
        ), patch("aiready.platforms.macos.time.sleep"), patch(
            "aiready.platforms.macos.shutil.which", side_effect=[None, None, "/usr/bin/git"]
        ):
            result = platform.install_prerequisite(git_prereq)

        assert result.success is True

    def test_git_install_xcode_timeout(self, platform):
        git_prereq = Prerequisite(name="git", min_version="2.0", check_command="git --version")
        trigger_result = CommandResult(return_code=0, stdout="", stderr="")
        with patch.object(platform, "check_command", return_value=None), patch(
            "aiready.platforms.macos.run_process", return_value=trigger_result
        ), patch("aiready.platforms.macos.time.sleep"), patch(
            "aiready.platforms.macos.shutil.which", return_value=None
        ):
            result = platform.install_prerequisite(git_prereq)

        assert result.success is False
        assert "timed out" in result.error.message

    def test_uv_install_calls_refresh_path(self, platform):
        uv_prereq = Prerequisite(name="uv", min_version="0.1.0", check_command="uv --version")
        success = CommandResult(return_code=0, stdout="", stderr="")
        with patch("aiready.platforms.macos.run_process_live", return_value=success), patch.object(
            platform, "_refresh_path"
        ) as mock_refresh:
            result = platform.install_prerequisite(uv_prereq)

        assert result.success is True
        mock_refresh.assert_called_once()

    def test_nodejs_pkg_install_uses_sudo(self, platform, nodejs_prereq):
        success = CommandResult(return_code=0, stdout="", stderr="")
        with patch.object(platform, "check_command", return_value=None), patch(
            "aiready.platforms.macos.run_process_live", return_value=success
        ) as mock_run, patch.object(platform, "get_temp_dir", return_value=Path("/tmp/aiready")), patch.object(
            platform, "_refresh_path"
        ):
            platform.install_prerequisite(nodejs_prereq)

        # Verify the installer command includes sudo
        calls = mock_run.call_args_list
        installer_call = [c for c in calls if "installer" in str(c)]
        assert len(installer_call) > 0
        assert installer_call[0][0][0][0] == "sudo"


# ---------------------------------------------------------------------------
# _refresh_path
# ---------------------------------------------------------------------------


class TestRefreshPath:
    def test_adds_common_dirs_to_path(self, platform):
        with patch.dict(os.environ, {"HOME": "/Users/testuser", "PATH": "/usr/bin"}, clear=True):
            platform._refresh_path()
            path = os.environ["PATH"]
            assert "/usr/local/bin" in path
            assert "/opt/homebrew/bin" in path
            assert "/Users/testuser/.local/bin" in path
            assert "/Users/testuser/.cargo/bin" in path

    def test_does_not_duplicate_existing_dirs(self, platform):
        with patch.dict(os.environ, {"HOME": "/Users/testuser", "PATH": "/usr/local/bin:/usr/bin"}, clear=True):
            platform._refresh_path()
            path = os.environ["PATH"]
            assert path.count("/usr/local/bin") == 1


# ---------------------------------------------------------------------------
# verify_prerequisite
# ---------------------------------------------------------------------------


class TestVerifyPrerequisite:
    def test_installed_and_version_ok(self, platform, nodejs_prereq):
        cmd_info = CommandInfo(path="/usr/local/bin/node", version="v20.0.0")
        with patch.object(platform, "check_command", return_value=cmd_info):
            result = platform.verify_prerequisite(nodejs_prereq)

        assert isinstance(result, PrereqCheckResult)
        assert result.installed is True
        assert result.needs_upgrade is False

    def test_not_installed(self, platform, nodejs_prereq):
        with patch.object(platform, "check_command", return_value=None):
            result = platform.verify_prerequisite(nodejs_prereq)

        assert result.installed is False

    def test_version_too_old(self, platform, nodejs_prereq):
        cmd_info = CommandInfo(path="/usr/local/bin/node", version="v14.0.0")
        with patch.object(platform, "check_command", return_value=cmd_info):
            result = platform.verify_prerequisite(nodejs_prereq)

        assert result.installed is True
        assert result.needs_upgrade is True

    def test_version_exactly_minimum(self, platform, nodejs_prereq):
        cmd_info = CommandInfo(path="/usr/local/bin/node", version="v18.0.0")
        with patch.object(platform, "check_command", return_value=cmd_info):
            result = platform.verify_prerequisite(nodejs_prereq)

        assert result.installed is True
        assert result.needs_upgrade is False


# ---------------------------------------------------------------------------
# add_to_path
# ---------------------------------------------------------------------------


class TestAddToPath:
    def test_adds_to_zshrc_by_default(self, platform):
        m = mock_open(read_data="# zsh config\n")
        with patch("builtins.open", m), patch("os.environ", {"SHELL": "/bin/zsh"}), patch(
            "pathlib.Path.home", return_value=Path("/Users/user")
        ):
            result = platform.add_to_path(Path("/opt/mybin"))

        assert result is True

    def test_skips_if_already_present(self, platform):
        existing = 'export PATH="/opt/mybin:$PATH"\n'
        m = mock_open(read_data=existing)
        with patch("builtins.open", m), patch("os.environ", {"SHELL": "/bin/zsh"}), patch(
            "pathlib.Path.home", return_value=Path("/Users/user")
        ):
            result = platform.add_to_path(Path("/opt/mybin"))

        assert result is True
        handle = m()
        handle.write.assert_not_called()

    def test_adds_to_bashrc_for_bash(self, platform):
        m = mock_open(read_data="# bash config\n")
        with patch("builtins.open", m), patch("os.environ", {"SHELL": "/bin/bash"}), patch(
            "pathlib.Path.home", return_value=Path("/Users/user")
        ):
            result = platform.add_to_path(Path("/opt/mybin"))

        assert result is True

    def test_creates_rc_file_if_missing(self, platform):
        m = mock_open()
        m.side_effect = [FileNotFoundError("No such file"), mock_open()()]
        with patch("builtins.open", m), patch("os.environ", {"SHELL": "/bin/zsh"}), patch(
            "pathlib.Path.home", return_value=Path("/Users/user")
        ):
            result = platform.add_to_path(Path("/opt/mybin"))

        assert result is True

    def test_returns_false_on_io_error(self, platform):
        with patch("builtins.open", side_effect=OSError("Permission denied")), patch(
            "os.environ", {"SHELL": "/bin/zsh"}
        ), patch("pathlib.Path.home", return_value=Path("/Users/user")):
            result = platform.add_to_path(Path("/opt/mybin"))

        assert result is False


# ---------------------------------------------------------------------------
# request_elevation
# ---------------------------------------------------------------------------


class TestRequestElevation:
    def test_already_root_returns_true(self, platform):
        with patch("os.geteuid", return_value=0):
            result = platform.request_elevation("need_root")

        assert result is True

    def test_not_root_returns_false(self, platform):
        with patch("os.geteuid", return_value=501):
            result = platform.request_elevation("need_root")

        assert result is False


# ---------------------------------------------------------------------------
# run_command
# ---------------------------------------------------------------------------


class TestRunCommand:
    def test_delegates_to_run_process(self, platform):
        expected = CommandResult(return_code=0, stdout="ok", stderr="")
        with patch("aiready.platforms.macos.run_process", return_value=expected) as mock_rp:
            result = platform.run_command(["ls", "-la"])

        mock_rp.assert_called_once_with(["ls", "-la"], timeout=120)
        assert result == expected

    def test_elevated_prepends_sudo(self, platform):
        expected = CommandResult(return_code=0, stdout="ok", stderr="")
        with patch("aiready.platforms.macos.run_process", return_value=expected) as mock_rp:
            platform.run_command(["installer", "-pkg", "node.pkg", "-target", "/"], elevated=True)

        mock_rp.assert_called_once_with(["sudo", "installer", "-pkg", "node.pkg", "-target", "/"], timeout=120)


# ---------------------------------------------------------------------------
# get_temp_dir
# ---------------------------------------------------------------------------


class TestGetTempDir:
    def test_returns_path_under_tempdir(self, platform):
        with patch("tempfile.gettempdir", return_value="/var/folders/tmp"), patch(
            "pathlib.Path.mkdir"
        ) as mock_mkdir:
            result = platform.get_temp_dir()

        assert result == Path("/var/folders/tmp/aiready")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# open_browser
# ---------------------------------------------------------------------------


class TestOpenBrowser:
    def test_uses_open_command(self, platform):
        success = CommandResult(return_code=0, stdout="", stderr="")
        with patch("aiready.platforms.macos.run_process", return_value=success) as mock_rp:
            result = platform.open_browser("https://example.com")

        mock_rp.assert_called_once_with(["open", "https://example.com"])
        assert result is True

    def test_returns_false_on_failure(self, platform):
        fail = CommandResult(return_code=1, stdout="", stderr="")
        with patch("aiready.platforms.macos.run_process", return_value=fail):
            result = platform.open_browser("https://example.com")

        assert result is False

    def test_returns_false_on_exception(self, platform):
        with patch("aiready.platforms.macos.run_process", side_effect=Exception("error")):
            result = platform.open_browser("https://example.com")

        assert result is False


# ---------------------------------------------------------------------------
# get_shell_type
# ---------------------------------------------------------------------------


class TestGetShellType:
    def test_zsh_is_default(self, platform):
        with patch("os.environ", {"SHELL": "/bin/zsh"}):
            result = platform.get_shell_type()

        assert result == ShellType.ZSH

    def test_bash_shell(self, platform):
        with patch("os.environ", {"SHELL": "/bin/bash"}):
            result = platform.get_shell_type()

        assert result == ShellType.BASH

    def test_default_zsh_when_no_shell_env(self, platform):
        with patch("os.environ", {}):
            result = platform.get_shell_type()

        assert result == ShellType.ZSH
