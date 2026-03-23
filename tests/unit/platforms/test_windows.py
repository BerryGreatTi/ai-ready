# tests/unit/platforms/test_windows.py
"""Tests for WindowsPlatform - all system calls are mocked (running on Linux)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, call, mock_open, patch

import pytest

from aiready.core.models import (
    CommandInfo,
    CommandResult,
    InstallResult,
    OSInfo,
    Prerequisite,
    PrereqCheckResult,
    ShellType,
)
from aiready.platforms.windows import WindowsPlatform


@pytest.fixture
def platform():
    return WindowsPlatform()


@pytest.fixture
def nodejs_prereq():
    return Prerequisite(name="nodejs", min_version="18.0.0", check_command="node")


@pytest.fixture
def git_prereq():
    return Prerequisite(name="git", min_version="2.0.0", check_command="git")


# ---------------------------------------------------------------------------
# get_os_info
# ---------------------------------------------------------------------------


class TestGetOsInfo:
    def test_returns_osinfo(self, platform):
        with patch("aiready.platforms.windows.platform_module") as mock_plat:
            mock_plat.system.return_value = "Windows"
            mock_plat.release.return_value = "10"
            mock_plat.version.return_value = "10.0.19041"
            mock_plat.machine.return_value = "AMD64"

            result = platform.get_os_info()

        assert isinstance(result, OSInfo)
        assert result.system == "Windows"
        assert result.release == "10"
        assert result.arch == "AMD64"

    def test_version_field(self, platform):
        with patch("aiready.platforms.windows.platform_module") as mock_plat:
            mock_plat.system.return_value = "Windows"
            mock_plat.release.return_value = "11"
            mock_plat.version.return_value = "10.0.22621"
            mock_plat.machine.return_value = "AMD64"

            result = platform.get_os_info()

        assert result.version == "10.0.22621"


# ---------------------------------------------------------------------------
# check_command
# ---------------------------------------------------------------------------


class TestCheckCommand:
    def test_returns_commandinfo_when_found_via_which(self, platform):
        mock_result = CommandResult(return_code=0, stdout="v20.0.0\n", stderr="")
        with patch("shutil.which", return_value=r"C:\Program Files\nodejs\node.exe"), patch(
            "aiready.platforms.windows.run_process", return_value=mock_result
        ):
            result = platform.check_command("node")

        assert isinstance(result, CommandInfo)
        assert result.path == r"C:\Program Files\nodejs\node.exe"
        assert result.version == "v20.0.0"

    def test_returns_none_when_not_found_and_no_fallback(self, platform):
        with patch("shutil.which", return_value=None), patch(
            "pathlib.Path.exists", return_value=False
        ):
            result = platform.check_command("unknowntool")

        assert result is None

    def test_fallback_to_known_path_for_git(self, platform):
        mock_result = CommandResult(return_code=0, stdout="git version 2.42.0\n", stderr="")
        with patch("shutil.which", return_value=None), patch(
            "pathlib.Path.exists", return_value=True
        ), patch("aiready.platforms.windows.run_process", return_value=mock_result):
            result = platform.check_command("git")

        assert isinstance(result, CommandInfo)
        assert result.path is not None
        assert result.version == "git version 2.42.0"

    def test_fallback_to_known_path_for_node(self, platform):
        mock_result = CommandResult(return_code=0, stdout="v20.0.0\n", stderr="")
        with patch("shutil.which", return_value=None), patch(
            "pathlib.Path.exists", return_value=True
        ), patch("aiready.platforms.windows.run_process", return_value=mock_result):
            result = platform.check_command("node")

        assert isinstance(result, CommandInfo)
        assert result.path is not None

    def test_version_from_stderr_fallback(self, platform):
        mock_result = CommandResult(return_code=1, stdout="", stderr="git version 2.39.0\n")
        with patch("shutil.which", return_value=r"C:\Program Files\Git\cmd\git.exe"), patch(
            "aiready.platforms.windows.run_process", return_value=mock_result
        ):
            result = platform.check_command("git")

        assert isinstance(result, CommandInfo)
        assert "2.39.0" in result.version

    def test_version_none_on_process_error(self, platform):
        mock_result = CommandResult(return_code=-1, stdout="", stderr="Command not found")
        with patch("shutil.which", return_value=r"C:\Program Files\nodejs\node.exe"), patch(
            "aiready.platforms.windows.run_process", return_value=mock_result
        ):
            result = platform.check_command("node")

        assert isinstance(result, CommandInfo)
        assert result.version is None


# ---------------------------------------------------------------------------
# install_prerequisite
# ---------------------------------------------------------------------------


class TestInstallPrerequisite:
    def test_nodejs_install_success(self, platform, nodejs_prereq):
        success = CommandResult(return_code=0, stdout="", stderr="")
        with patch("aiready.platforms.windows.run_process", return_value=success), patch.object(
            platform, "get_temp_dir", return_value=Path(r"C:\Temp\aiready")
        ):
            result = platform.install_prerequisite(nodejs_prereq)

        assert isinstance(result, InstallResult)
        assert result.success is True

    def test_nodejs_install_failure(self, platform, nodejs_prereq):
        fail = CommandResult(return_code=1, stdout="", stderr="Download failed")
        with patch("aiready.platforms.windows.run_process", return_value=fail), patch.object(
            platform, "get_temp_dir", return_value=Path(r"C:\Temp\aiready")
        ):
            result = platform.install_prerequisite(nodejs_prereq)

        assert isinstance(result, InstallResult)
        assert result.success is False

    def test_git_install_success(self, platform, git_prereq):
        success = CommandResult(return_code=0, stdout="", stderr="")
        with patch("aiready.platforms.windows.run_process", return_value=success), patch.object(
            platform, "get_temp_dir", return_value=Path(r"C:\Temp\aiready")
        ):
            result = platform.install_prerequisite(git_prereq)

        assert isinstance(result, InstallResult)
        assert result.success is True

    def test_unknown_prereq_returns_failure(self, platform):
        prereq = Prerequisite(name="unknowntool", min_version="1.0.0", check_command="unknowntool")
        result = platform.install_prerequisite(prereq)
        assert isinstance(result, InstallResult)
        assert result.success is False

    def test_nodejs_uses_msiexec_not_winget(self, platform, nodejs_prereq):
        """Verify nodejs install uses msiexec, not winget."""
        calls = []

        def capture_run(cmd, *args, **kwargs):
            calls.append(cmd)
            return CommandResult(return_code=0, stdout="", stderr="")

        with patch("aiready.platforms.windows.run_process", side_effect=capture_run), patch.object(
            platform, "get_temp_dir", return_value=Path(r"C:\Temp\aiready")
        ):
            platform.install_prerequisite(nodejs_prereq)

        all_cmds_flat = " ".join(str(c) for cmd in calls for c in cmd)
        assert "winget" not in all_cmds_flat
        assert any("msiexec" in str(c) for cmd in calls for c in cmd)


# ---------------------------------------------------------------------------
# verify_prerequisite
# ---------------------------------------------------------------------------


class TestVerifyPrerequisite:
    def test_installed_and_version_ok(self, platform, nodejs_prereq):
        cmd_info = CommandInfo(path=r"C:\Program Files\nodejs\node.exe", version="v20.0.0")
        with patch.object(platform, "check_command", return_value=cmd_info):
            result = platform.verify_prerequisite(nodejs_prereq)

        assert isinstance(result, PrereqCheckResult)
        assert result.installed is True
        assert result.needs_upgrade is False

    def test_not_installed(self, platform, nodejs_prereq):
        with patch.object(platform, "check_command", return_value=None):
            result = platform.verify_prerequisite(nodejs_prereq)

        assert result.installed is False
        assert result.needs_upgrade is False

    def test_version_too_old(self, platform, nodejs_prereq):
        cmd_info = CommandInfo(path=r"C:\Program Files\nodejs\node.exe", version="v14.0.0")
        with patch.object(platform, "check_command", return_value=cmd_info):
            result = platform.verify_prerequisite(nodejs_prereq)

        assert result.installed is True
        assert result.needs_upgrade is True

    def test_version_exactly_minimum(self, platform, nodejs_prereq):
        cmd_info = CommandInfo(path=r"C:\Program Files\nodejs\node.exe", version="v18.0.0")
        with patch.object(platform, "check_command", return_value=cmd_info):
            result = platform.verify_prerequisite(nodejs_prereq)

        assert result.installed is True
        assert result.needs_upgrade is False


# ---------------------------------------------------------------------------
# add_to_path
# ---------------------------------------------------------------------------


class TestAddToPath:
    def test_adds_path_when_not_present(self, platform):
        query_result = CommandResult(
            return_code=0, stdout="    Path    REG_EXPAND_SZ    C:\\Windows\\System32", stderr=""
        )
        set_result = CommandResult(return_code=0, stdout="", stderr="")
        with patch(
            "aiready.platforms.windows.run_process", side_effect=[query_result, set_result]
        ):
            result = platform.add_to_path(Path(r"C:\mytools\bin"))

        assert result is True

    def test_skips_when_already_present(self, platform):
        query_result = CommandResult(
            return_code=0,
            stdout=r"    Path    REG_EXPAND_SZ    C:\Windows\System32;C:\mytools\bin",
            stderr="",
        )
        with patch("aiready.platforms.windows.run_process", return_value=query_result) as mock_rp:
            result = platform.add_to_path(Path(r"C:\mytools\bin"))

        assert result is True
        # Only one call (the query), no set call
        assert mock_rp.call_count == 1

    def test_returns_false_on_query_failure(self, platform):
        fail_result = CommandResult(return_code=1, stdout="", stderr="Access denied")
        with patch("aiready.platforms.windows.run_process", return_value=fail_result):
            result = platform.add_to_path(Path(r"C:\mytools\bin"))

        assert result is False

    def test_returns_false_on_set_failure(self, platform):
        query_result = CommandResult(
            return_code=0, stdout="    Path    REG_EXPAND_SZ    C:\\Windows\\System32", stderr=""
        )
        fail_result = CommandResult(return_code=1, stdout="", stderr="Access denied")
        with patch(
            "aiready.platforms.windows.run_process", side_effect=[query_result, fail_result]
        ):
            result = platform.add_to_path(Path(r"C:\mytools\bin"))

        assert result is False

    def test_no_winreg_import(self, platform):
        """Verify add_to_path uses reg command, not winreg module."""
        import aiready.platforms.windows as win_module
        assert not hasattr(win_module, "winreg"), "Should not import winreg at module level"


# ---------------------------------------------------------------------------
# request_elevation
# ---------------------------------------------------------------------------


class TestRequestElevation:
    def test_returns_true_when_write_succeeds(self, platform):
        success = CommandResult(return_code=0, stdout="", stderr="")
        with patch("aiready.platforms.windows.run_process", return_value=success):
            result = platform.request_elevation("need_admin")

        assert result is True

    def test_returns_false_when_write_fails(self, platform):
        fail = CommandResult(return_code=1, stdout="", stderr="Access is denied.")
        with patch("aiready.platforms.windows.run_process", return_value=fail):
            result = platform.request_elevation("need_admin")

        assert result is False


# ---------------------------------------------------------------------------
# run_command
# ---------------------------------------------------------------------------


class TestRunCommand:
    def test_delegates_to_run_process(self, platform):
        expected = CommandResult(return_code=0, stdout="ok", stderr="")
        with patch("aiready.platforms.windows.run_process", return_value=expected) as mock_rp:
            result = platform.run_command(["dir"])

        mock_rp.assert_called_once_with(["dir"])
        assert result == expected

    def test_elevated_does_not_prepend_sudo(self, platform):
        """Windows does not use sudo."""
        expected = CommandResult(return_code=0, stdout="ok", stderr="")
        with patch("aiready.platforms.windows.run_process", return_value=expected) as mock_rp:
            platform.run_command(["msiexec", "/i", "node.msi"], elevated=True)

        # Should NOT prepend sudo
        call_args = mock_rp.call_args[0][0]
        assert call_args[0] != "sudo"
        assert call_args[0] == "msiexec"


# ---------------------------------------------------------------------------
# get_temp_dir
# ---------------------------------------------------------------------------


class TestGetTempDir:
    def test_returns_path_under_temp_env(self, platform):
        with patch.dict(os.environ, {"TEMP": r"C:\Users\user\AppData\Local\Temp"}), patch(
            "pathlib.Path.mkdir"
        ) as mock_mkdir:
            result = platform.get_temp_dir()

        assert str(result).endswith("aiready")
        assert "AppData" in str(result) or "Temp" in str(result)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_falls_back_to_tempfile_gettempdir(self, platform):
        env = {k: v for k, v in os.environ.items() if k != "TEMP"}
        with patch.dict(os.environ, env, clear=True), patch(
            "tempfile.gettempdir", return_value=r"C:\Windows\Temp"
        ), patch("pathlib.Path.mkdir"):
            result = platform.get_temp_dir()

        assert str(result).endswith("aiready")


# ---------------------------------------------------------------------------
# open_browser
# ---------------------------------------------------------------------------


class TestOpenBrowser:
    def test_opens_url_returns_true(self, platform):
        with patch("webbrowser.open", return_value=True) as mock_wb:
            result = platform.open_browser("https://example.com")

        mock_wb.assert_called_once_with("https://example.com")
        assert result is True

    def test_returns_false_on_exception(self, platform):
        with patch("webbrowser.open", side_effect=Exception("no browser")):
            result = platform.open_browser("https://example.com")

        assert result is False


# ---------------------------------------------------------------------------
# get_shell_type
# ---------------------------------------------------------------------------


class TestGetShellType:
    def test_powershell_detection(self, platform):
        with patch.dict(os.environ, {"PSModulePath": r"C:\Windows\system32\WindowsPowerShell\v1.0\Modules"}):
            result = platform.get_shell_type()

        assert result == ShellType.POWERSHELL

    def test_default_cmd_when_no_powershell(self, platform):
        with patch.dict(os.environ, {"PSModulePath": ""}, clear=False):
            result = platform.get_shell_type()

        assert result == ShellType.CMD

    def test_returns_shell_type_enum(self, platform):
        with patch.dict(os.environ, {"PSModulePath": r"C:\PowerShell"}):
            result = platform.get_shell_type()

        assert isinstance(result, ShellType)
