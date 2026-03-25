# tests/unit/platforms/test_linux.py
"""Tests for LinuxPlatform - all system calls are mocked."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="Linux platform tests not applicable on Windows")

from aiready.core.models import (
    CommandInfo,
    CommandResult,
    InstallResult,
    OSInfo,
    Prerequisite,
    PrereqCheckResult,
    ShellType,
)
from aiready.platforms.linux import LinuxPlatform


@pytest.fixture
def platform():
    return LinuxPlatform()


@pytest.fixture
def nodejs_prereq():
    return Prerequisite(name="nodejs", min_version="18.0.0", check_command="node")


# ---------------------------------------------------------------------------
# get_os_info
# ---------------------------------------------------------------------------


class TestGetOsInfo:
    def test_returns_osinfo(self, platform):
        with patch("aiready.platforms.linux.platform_module") as mock_plat:
            mock_plat.system.return_value = "Linux"
            mock_plat.release.return_value = "5.15.0"
            mock_plat.version.return_value = "#1 SMP"
            mock_plat.machine.return_value = "x86_64"

            result = platform.get_os_info()

        assert isinstance(result, OSInfo)
        assert result.system == "Linux"
        assert result.release == "5.15.0"
        assert result.arch == "x86_64"

    def test_returns_correct_version(self, platform):
        with patch("aiready.platforms.linux.platform_module") as mock_plat:
            mock_plat.system.return_value = "Linux"
            mock_plat.release.return_value = "6.1.0"
            mock_plat.version.return_value = "#2 SMP"
            mock_plat.machine.return_value = "aarch64"

            result = platform.get_os_info()

        assert result.version == "#2 SMP"
        assert result.arch == "aarch64"


# ---------------------------------------------------------------------------
# check_command
# ---------------------------------------------------------------------------


class TestCheckCommand:
    def test_returns_commandinfo_when_found(self, platform):
        mock_result = CommandResult(return_code=0, stdout="node v20.0.0\n", stderr="")
        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "aiready.platforms.linux.run_process", return_value=mock_result
        ):
            result = platform.check_command("node")

        assert isinstance(result, CommandInfo)
        assert result.path == "/usr/bin/node"
        assert result.version == "node v20.0.0"

    def test_returns_none_when_not_found(self, platform):
        with patch("shutil.which", return_value=None):
            result = platform.check_command("node")

        assert result is None

    def test_version_from_stderr_fallback(self, platform):
        mock_result = CommandResult(return_code=1, stdout="", stderr="git version 2.39.0\n")
        with patch("shutil.which", return_value="/usr/bin/git"), patch(
            "aiready.platforms.linux.run_process", return_value=mock_result
        ):
            result = platform.check_command("git")

        assert isinstance(result, CommandInfo)
        assert result.path == "/usr/bin/git"
        assert "2.39.0" in result.version

    def test_version_none_on_run_failure(self, platform):
        mock_result = CommandResult(return_code=-1, stdout="", stderr="Command not found: node")
        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "aiready.platforms.linux.run_process", return_value=mock_result
        ):
            result = platform.check_command("node")

        assert isinstance(result, CommandInfo)
        assert result.version is None


# ---------------------------------------------------------------------------
# install_prerequisite
# ---------------------------------------------------------------------------


class TestInstallPrerequisite:
    def test_nodejs_install_success(self, platform, nodejs_prereq):
        success_result = CommandResult(return_code=0, stdout="", stderr="")
        with patch.object(platform, "_detect_package_manager", return_value="apt-get"), patch(
            "aiready.platforms.linux.run_process", return_value=success_result
        ):
            result = platform.install_prerequisite(nodejs_prereq)

        assert isinstance(result, InstallResult)
        assert result.success is True

    def test_nodejs_install_failure(self, platform, nodejs_prereq):
        fail_result = CommandResult(return_code=1, stdout="", stderr="E: Unable to locate package")
        with patch.object(platform, "_detect_package_manager", return_value="apt-get"), patch(
            "aiready.platforms.linux.run_process", return_value=fail_result
        ):
            result = platform.install_prerequisite(nodejs_prereq)

        assert isinstance(result, InstallResult)
        assert result.success is False

    def test_unknown_prereq_returns_failure(self, platform):
        prereq = Prerequisite(name="unknowntool", min_version="1.0.0", check_command="unknowntool")
        result = platform.install_prerequisite(prereq)
        assert isinstance(result, InstallResult)
        assert result.success is False

    def test_nodejs_with_dnf(self, platform, nodejs_prereq):
        success_result = CommandResult(return_code=0, stdout="", stderr="")
        with patch.object(platform, "_detect_package_manager", return_value="dnf"), patch(
            "aiready.platforms.linux.run_process", return_value=success_result
        ):
            result = platform.install_prerequisite(nodejs_prereq)

        assert isinstance(result, InstallResult)
        assert result.success is True


# ---------------------------------------------------------------------------
# verify_prerequisite
# ---------------------------------------------------------------------------


class TestVerifyPrerequisite:
    def test_installed_and_version_ok(self, platform, nodejs_prereq):
        cmd_info = CommandInfo(path="/usr/bin/node", version="v20.0.0")
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
        cmd_info = CommandInfo(path="/usr/bin/node", version="v14.0.0")
        with patch.object(platform, "check_command", return_value=cmd_info):
            result = platform.verify_prerequisite(nodejs_prereq)

        assert result.installed is True
        assert result.needs_upgrade is True

    def test_version_exactly_minimum(self, platform, nodejs_prereq):
        cmd_info = CommandInfo(path="/usr/bin/node", version="v18.0.0")
        with patch.object(platform, "check_command", return_value=cmd_info):
            result = platform.verify_prerequisite(nodejs_prereq)

        assert result.installed is True
        assert result.needs_upgrade is False


# ---------------------------------------------------------------------------
# add_to_path
# ---------------------------------------------------------------------------


class TestAddToPath:
    def test_adds_to_bashrc(self, platform):
        m = mock_open(read_data="# existing content\n")
        with patch("builtins.open", m), patch("os.environ", {"SHELL": "/bin/bash"}), patch(
            "pathlib.Path.exists", return_value=True
        ), patch("pathlib.Path.home", return_value=Path("/home/user")):
            result = platform.add_to_path(Path("/opt/mybin"))

        assert result is True

    def test_skips_if_already_present(self, platform):
        existing = 'export PATH="/opt/mybin:$PATH"\n'
        m = mock_open(read_data=existing)
        with patch("builtins.open", m), patch("os.environ", {"SHELL": "/bin/bash"}), patch(
            "pathlib.Path.home", return_value=Path("/home/user")
        ):
            result = platform.add_to_path(Path("/opt/mybin"))

        assert result is True
        # Write should not be called (only read)
        handle = m()
        handle.write.assert_not_called()

    def test_adds_to_zshrc_for_zsh(self, platform):
        m = mock_open(read_data="# zsh config\n")
        with patch("builtins.open", m), patch(
            "os.environ", {"SHELL": "/bin/zsh"}
        ), patch("pathlib.Path.home", return_value=Path("/home/user")):
            result = platform.add_to_path(Path("/opt/mybin"))

        assert result is True


# ---------------------------------------------------------------------------
# request_elevation
# ---------------------------------------------------------------------------


class TestRequestElevation:
    def test_already_root_returns_true(self, platform):
        with patch("os.geteuid", return_value=0):
            result = platform.request_elevation("need_root")

        assert result is True

    def test_not_root_returns_false(self, platform):
        with patch("os.geteuid", return_value=1000):
            result = platform.request_elevation("need_root")

        assert result is False


# ---------------------------------------------------------------------------
# run_command
# ---------------------------------------------------------------------------


class TestRunCommand:
    def test_delegates_to_run_process(self, platform):
        expected = CommandResult(return_code=0, stdout="ok", stderr="")
        with patch("aiready.platforms.linux.run_process", return_value=expected) as mock_rp:
            result = platform.run_command(["ls", "-la"])

        mock_rp.assert_called_once_with(["ls", "-la"], timeout=120)
        assert result == expected

    def test_elevated_prepends_sudo(self, platform):
        expected = CommandResult(return_code=0, stdout="ok", stderr="")
        with patch("aiready.platforms.linux.run_process", return_value=expected) as mock_rp:
            platform.run_command(["apt-get", "install", "node"], elevated=True)

        mock_rp.assert_called_once_with(["sudo", "apt-get", "install", "node"], timeout=120)


# ---------------------------------------------------------------------------
# get_temp_dir
# ---------------------------------------------------------------------------


class TestGetTempDir:
    def test_returns_path_under_tempdir(self, platform):
        with patch("tempfile.gettempdir", return_value="/tmp"), patch(
            "pathlib.Path.mkdir"
        ) as mock_mkdir:
            result = platform.get_temp_dir()

        assert result == Path("/tmp/aiready")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


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
    def test_bash_shell(self, platform):
        with patch("os.environ", {"SHELL": "/bin/bash"}):
            result = platform.get_shell_type()

        assert result == ShellType.BASH

    def test_zsh_shell(self, platform):
        with patch("os.environ", {"SHELL": "/usr/bin/zsh"}):
            result = platform.get_shell_type()

        assert result == ShellType.ZSH

    def test_default_bash_on_unknown(self, platform):
        with patch("os.environ", {}):
            result = platform.get_shell_type()

        assert result == ShellType.BASH


# ---------------------------------------------------------------------------
# _detect_distro
# ---------------------------------------------------------------------------


class TestDetectDistro:
    def test_ubuntu(self, platform):
        content = 'ID=ubuntu\nVERSION_ID="22.04"\n'
        with patch("builtins.open", mock_open(read_data=content)):
            result = platform._detect_distro()

        assert result == "ubuntu"

    def test_fedora(self, platform):
        content = "ID=fedora\nVERSION_ID=38\n"
        with patch("builtins.open", mock_open(read_data=content)):
            result = platform._detect_distro()

        assert result == "fedora"

    def test_arch(self, platform):
        content = "ID=arch\n"
        with patch("builtins.open", mock_open(read_data=content)):
            result = platform._detect_distro()

        assert result == "arch"

    def test_file_missing_returns_unknown(self, platform):
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = platform._detect_distro()

        assert result == "unknown"


# ---------------------------------------------------------------------------
# _detect_package_manager
# ---------------------------------------------------------------------------


class TestDetectPackageManager:
    def test_ubuntu_uses_apt_get(self, platform):
        with patch.object(platform, "_detect_distro", return_value="ubuntu"):
            result = platform._detect_package_manager()

        assert result == "apt-get"

    def test_debian_uses_apt_get(self, platform):
        with patch.object(platform, "_detect_distro", return_value="debian"):
            result = platform._detect_package_manager()

        assert result == "apt-get"

    def test_fedora_uses_dnf(self, platform):
        with patch.object(platform, "_detect_distro", return_value="fedora"):
            result = platform._detect_package_manager()

        assert result == "dnf"

    def test_arch_uses_pacman(self, platform):
        with patch.object(platform, "_detect_distro", return_value="arch"):
            result = platform._detect_package_manager()

        assert result == "pacman"

    def test_alpine_uses_apk(self, platform):
        with patch.object(platform, "_detect_distro", return_value="alpine"):
            result = platform._detect_package_manager()

        assert result == "apk"

    def test_unknown_defaults_to_apt_get(self, platform):
        with patch.object(platform, "_detect_distro", return_value="unknown"):
            result = platform._detect_package_manager()

        assert result == "apt-get"
