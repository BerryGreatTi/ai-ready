"""Tests for launch_in_terminal and resolve_command logic in CompleteScreen."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from aiready.gui.screens.complete import (
    _launch_in_terminal, _launch_in_linux_terminal,
    _resolve_command, _display_command,
)


class TestResolveCommand:
    @patch("aiready.gui.screens.complete.shutil.which")
    def test_resolves_claude_to_absolute_path(self, mock_which):
        mock_which.return_value = "/usr/local/bin/claude"

        result = _resolve_command("claude_code")

        assert '"/usr/local/bin/claude"' in result
        mock_which.assert_called_once_with("claude")

    @patch("aiready.gui.screens.complete.shutil.which")
    def test_resolves_openclaw_with_onboard_arg(self, mock_which):
        mock_which.return_value = "/home/user/.local/bin/openclaw"

        result = _resolve_command("openclaw")

        assert '"/home/user/.local/bin/openclaw"' in result
        assert result.endswith("onboard")

    @patch("aiready.gui.screens.complete.shutil.which")
    def test_falls_back_to_binary_name_when_not_found(self, mock_which):
        mock_which.return_value = None

        result = _resolve_command("claude_code")

        assert result == "claude"

    def test_display_command_claude(self):
        assert _display_command("claude_code") == "claude"

    def test_display_command_openclaw(self):
        assert _display_command("openclaw") == "openclaw onboard"


class TestLaunchInTerminal:
    @patch("aiready.gui.screens.complete.sys")
    @patch("aiready.gui.screens.complete.subprocess")
    def test_windows_uses_powershell(self, mock_subprocess, mock_sys):
        mock_sys.platform = "win32"
        mock_subprocess.CREATE_NEW_CONSOLE = 0x10

        result = _launch_in_terminal("claude")

        assert result is True
        mock_subprocess.Popen.assert_called_once()
        args = mock_subprocess.Popen.call_args
        cmd = args[0][0]
        assert cmd[0] == "powershell"
        assert "-NoExit" in cmd
        assert "-Command" in cmd
        assert "claude" in cmd

    @patch("aiready.gui.screens.complete.sys")
    @patch("aiready.gui.screens.complete.subprocess")
    def test_macos_uses_osascript(self, mock_subprocess, mock_sys):
        mock_sys.platform = "darwin"

        result = _launch_in_terminal("claude")

        assert result is True
        mock_subprocess.Popen.assert_called_once()
        args = mock_subprocess.Popen.call_args
        cmd = args[0][0]
        assert cmd[0] == "osascript"
        assert "-e" in cmd

    @patch("aiready.gui.screens.complete.sys")
    @patch("aiready.gui.screens.complete.subprocess")
    def test_macos_escapes_double_quotes(self, mock_subprocess, mock_sys):
        mock_sys.platform = "darwin"

        _launch_in_terminal('some "quoted" cmd')

        args = mock_subprocess.Popen.call_args
        script = args[0][0][2]  # osascript -e <script>
        assert '\\"' in script
        assert 'some \\"quoted\\" cmd' in script

    @patch("aiready.gui.screens.complete._launch_in_linux_terminal")
    @patch("aiready.gui.screens.complete.sys")
    def test_linux_delegates_to_linux_launcher(self, mock_sys, mock_linux):
        mock_sys.platform = "linux"

        result = _launch_in_terminal("claude")

        assert result is True
        mock_linux.assert_called_once_with("claude")

    @patch("aiready.gui.screens.complete.sys")
    @patch("aiready.gui.screens.complete.subprocess")
    def test_returns_false_on_exception(self, mock_subprocess, mock_sys):
        mock_sys.platform = "win32"
        mock_subprocess.CREATE_NEW_CONSOLE = 0x10
        mock_subprocess.Popen.side_effect = OSError("fail")

        result = _launch_in_terminal("claude")

        assert result is False


class TestLaunchInLinuxTerminal:
    @patch("aiready.gui.screens.complete.subprocess")
    @patch("aiready.gui.screens.complete.shutil")
    def test_tries_gnome_terminal_first(self, mock_shutil, mock_subprocess):
        mock_shutil.which.return_value = "/usr/bin/gnome-terminal"

        _launch_in_linux_terminal("claude")

        first_call = mock_subprocess.Popen.call_args_list[0]
        cmd = first_call[0][0]
        assert cmd[0] == "gnome-terminal"

    @patch("aiready.gui.screens.complete.subprocess")
    @patch("aiready.gui.screens.complete.shutil")
    def test_falls_back_to_next_terminal(self, mock_shutil, mock_subprocess):
        mock_shutil.which.side_effect = [None, "/usr/bin/konsole"]

        _launch_in_linux_terminal("claude")

        assert mock_subprocess.Popen.call_count == 1
        first_call = mock_subprocess.Popen.call_args_list[0]
        cmd = first_call[0][0]
        assert cmd[0] == "konsole"

    @patch("aiready.gui.screens.complete.subprocess")
    @patch("aiready.gui.screens.complete.shutil")
    def test_command_included_in_terminal_args(self, mock_shutil, mock_subprocess):
        mock_shutil.which.return_value = "/usr/bin/gnome-terminal"

        _launch_in_linux_terminal("openclaw onboard")

        first_call = mock_subprocess.Popen.call_args_list[0]
        cmd = first_call[0][0]
        cmd_str = " ".join(cmd)
        assert "openclaw onboard" in cmd_str
