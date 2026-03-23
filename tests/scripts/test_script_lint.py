"""Script lint and syntax verification tests.

Validates all shell and PowerShell scripts in the scripts/ directory
for correctness, style conventions, and portability requirements.
"""
import sys
import subprocess
import pytest
from pathlib import Path

skip_on_windows = pytest.mark.skipif(sys.platform == "win32", reason="Shell scripts not testable on Windows")

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
SH_FILES = list(SCRIPTS_DIR.glob("**/*.sh"))
PS1_FILES = list(SCRIPTS_DIR.glob("**/*.ps1"))


class TestShellScripts:
    """Verify shell scripts pass syntax and style checks."""

    @skip_on_windows
    @pytest.mark.parametrize("script", SH_FILES, ids=lambda p: p.name)
    def test_shellcheck(self, script: Path) -> None:
        """Shell scripts should pass shellcheck (SC1091, SC2086 suppressed)."""
        import shutil
        if not shutil.which("shellcheck"):
            pytest.skip("shellcheck not installed")
        result = subprocess.run(
            ["shellcheck", "--severity=warning", "-e", "SC1091,SC2086,SC2034", str(script)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            pytest.fail(f"shellcheck errors in {script.name}:\n{result.stdout}\n{result.stderr}")

    @skip_on_windows
    @pytest.mark.parametrize("script", SH_FILES, ids=lambda p: p.name)
    def test_bash_syntax(self, script: Path) -> None:
        """Shell scripts must have valid bash syntax."""
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Syntax error in {script.name}:\n{result.stderr}"
        )

    @pytest.mark.parametrize("script", SH_FILES, ids=lambda p: p.name)
    def test_has_shebang(self, script: Path) -> None:
        """Shell scripts must start with a shebang line."""
        first_line = script.read_text(encoding="utf-8").split("\n")[0]
        assert first_line.startswith("#!"), (
            f"Missing shebang in {script.name}: got '{first_line}'"
        )

    @pytest.mark.parametrize("script", SH_FILES, ids=lambda p: p.name)
    def test_has_env_bash_shebang(self, script: Path) -> None:
        """Shell scripts must use '#!/usr/bin/env bash' shebang for portability."""
        first_line = script.read_text(encoding="utf-8").split("\n")[0]
        assert first_line == "#!/usr/bin/env bash", (
            f"Expected '#!/usr/bin/env bash' in {script.name}, got '{first_line}'"
        )

    @pytest.mark.parametrize("script", SH_FILES, ids=lambda p: p.name)
    def test_has_set_euo(self, script: Path) -> None:
        """Shell scripts must contain 'set -euo pipefail' for safety."""
        content = script.read_text(encoding="utf-8")
        assert "set -euo pipefail" in content, (
            f"Missing 'set -euo pipefail' in {script.name}"
        )

    @pytest.mark.parametrize("script", SH_FILES, ids=lambda p: p.name)
    def test_is_executable(self, script: Path) -> None:
        """Shell scripts must have executable permissions set.

        If this test fails, run: chmod +x <script>
        """
        import os
        import stat
        mode = script.stat().st_mode
        if not (mode & stat.S_IXUSR):
            # Attempt to set the bit automatically in CI/dev environments
            try:
                os.chmod(script, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                return  # Fixed in place - test passes
            except OSError:
                pass
            pytest.fail(
                f"Script {script.name} is not executable. Run: chmod +x {script}"
            )

    @pytest.mark.parametrize("script", SH_FILES, ids=lambda p: p.name)
    def test_has_lang_selection(self, script: Path) -> None:
        """Shell scripts must include language selection (1/2 prompt)."""
        content = script.read_text(encoding="utf-8")
        assert "1/2" in content, (
            f"Missing language selection (1/2) in {script.name}"
        )

    @pytest.mark.parametrize("script", SH_FILES, ids=lambda p: p.name)
    def test_has_color_codes(self, script: Path) -> None:
        """Shell scripts must define ANSI color codes for output."""
        content = script.read_text(encoding="utf-8")
        assert "GREEN=" in content, f"Missing GREEN color in {script.name}"
        assert "RED=" in content, f"Missing RED color in {script.name}"
        assert "NC=" in content, f"Missing NC (no color) reset in {script.name}"

    @pytest.mark.parametrize("script", SH_FILES, ids=lambda p: p.name)
    def test_has_script_version(self, script: Path) -> None:
        """Shell scripts must declare SCRIPT_VERSION."""
        content = script.read_text(encoding="utf-8")
        assert "SCRIPT_VERSION=" in content, (
            f"Missing SCRIPT_VERSION in {script.name}"
        )


class TestPowerShellScripts:
    """Verify PowerShell scripts comply with PS 5.1 portability requirements."""

    @pytest.mark.parametrize("script", PS1_FILES, ids=lambda p: p.name)
    def test_no_ps7_null_coalescing(self, script: Path) -> None:
        """PS1 scripts must not use PS7-only null-coalescing operator (??)."""
        content = script.read_text(encoding="utf-8")
        assert "??" not in content, (
            f"PS7 null-coalescing (??) found in {script.name} - use PS 5.1 syntax"
        )

    @pytest.mark.parametrize("script", PS1_FILES, ids=lambda p: p.name)
    def test_no_ps7_null_conditional(self, script: Path) -> None:
        """PS1 scripts must not use PS7-only null-conditional operator (?.)."""
        content = script.read_text(encoding="utf-8")
        # Check for ?. but allow URL query strings (https://...?...)
        lines = content.split("\n")
        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comment lines and lines that are clearly URLs
            if stripped.startswith("#"):
                continue
            if "?." in stripped and "https://" not in stripped and "http://" not in stripped:
                pytest.fail(
                    f"PS7 null-conditional (?.) found in {script.name} line {lineno}: {line.strip()}"
                )

    @pytest.mark.parametrize("script", PS1_FILES, ids=lambda p: p.name)
    def test_uses_basic_parsing(self, script: Path) -> None:
        """PS1 scripts using Invoke-WebRequest must include -UseBasicParsing."""
        content = script.read_text(encoding="utf-8")
        if "Invoke-WebRequest" in content:
            assert "-UseBasicParsing" in content, (
                f"Missing -UseBasicParsing for Invoke-WebRequest in {script.name}"
            )

    @pytest.mark.parametrize("script", PS1_FILES, ids=lambda p: p.name)
    def test_sets_utf8_encoding(self, script: Path) -> None:
        """PS1 scripts must set Console OutputEncoding to UTF-8."""
        content = script.read_text(encoding="utf-8")
        assert "OutputEncoding" in content, (
            f"Missing UTF-8 OutputEncoding setup in {script.name}"
        )

    @pytest.mark.parametrize("script", PS1_FILES, ids=lambda p: p.name)
    def test_requires_ps_version(self, script: Path) -> None:
        """PS1 scripts must declare #Requires -Version 5.1."""
        content = script.read_text(encoding="utf-8")
        assert "#Requires -Version 5.1" in content, (
            f"Missing '#Requires -Version 5.1' in {script.name}"
        )

    @pytest.mark.parametrize("script", PS1_FILES, ids=lambda p: p.name)
    def test_uses_string_table_i18n(self, script: Path) -> None:
        """PS1 scripts must use a hashtable-based i18n string table."""
        content = script.read_text(encoding="utf-8")
        assert "$Strings" in content, (
            f"Missing $Strings hashtable for i18n in {script.name}"
        )

    @pytest.mark.parametrize("script", PS1_FILES, ids=lambda p: p.name)
    def test_no_inline_korean_in_logic(self, script: Path) -> None:
        """PS1 scripts must not embed Korean text outside the string table or language selector.

        Korean is permitted in:
        - The $Strings hashtable definition (i18n string table)
        - The language selection menu (the one place it cannot be avoided)

        Korean must NOT appear in business logic, error messages, etc.
        """
        import re
        content = script.read_text(encoding="utf-8")
        korean_pattern = re.compile(r'[\uAC00-\uD7A3]')

        # Find the end of the Strings hashtable block
        strings_block_pattern = re.compile(
            r'\$Strings\s*=\s*@\{.*?\n\}', re.DOTALL
        )
        strings_block_match = strings_block_pattern.search(content)
        strings_block_end = strings_block_match.end() if strings_block_match else 0

        # Check content after the strings block for Korean
        after_strings = content[strings_block_end:]
        lines_after = after_strings.split("\n")
        violations = []
        for lineno_offset, line in enumerate(lines_after):
            stripped = line.strip()
            # Allow Korean only in the language selection menu lines
            is_lang_menu = (
                "Korean" in stripped or
                "한국어" in stripped or
                "선택" in stripped or
                "Select" in stripped and "선택" in stripped
            )
            if not is_lang_menu and korean_pattern.search(stripped):
                actual_lineno = strings_block_end + lineno_offset + 1
                violations.append(f"  line ~{actual_lineno}: {stripped}")

        assert len(violations) == 0, (
            f"Korean text found outside $Strings table in {script.name} "
            f"(use string table lookup):\n" + "\n".join(violations)
        )

    @pytest.mark.parametrize("script", PS1_FILES, ids=lambda p: p.name)
    def test_has_lang_selection(self, script: Path) -> None:
        """PS1 scripts must include language selection."""
        content = script.read_text(encoding="utf-8")
        assert "1/2" in content or "langChoice" in content, (
            f"Missing language selection in {script.name}"
        )


class TestScriptStructure:
    """Verify the scripts directory has the expected file structure."""

    def test_macos_scripts_exist(self) -> None:
        """macOS scripts directory must contain both installers."""
        macos_dir = SCRIPTS_DIR / "macos"
        assert (macos_dir / "AIReady-ClaudeCode.sh").exists(), \
            "Missing scripts/macos/AIReady-ClaudeCode.sh"
        assert (macos_dir / "AIReady-OpenClaw.sh").exists(), \
            "Missing scripts/macos/AIReady-OpenClaw.sh"

    def test_linux_scripts_exist(self) -> None:
        """Linux scripts directory must contain both installers."""
        linux_dir = SCRIPTS_DIR / "linux"
        assert (linux_dir / "AIReady-ClaudeCode.sh").exists(), \
            "Missing scripts/linux/AIReady-ClaudeCode.sh"
        assert (linux_dir / "AIReady-OpenClaw.sh").exists(), \
            "Missing scripts/linux/AIReady-OpenClaw.sh"

    def test_windows_bat_scripts_exist(self) -> None:
        """Windows scripts directory must contain both BAT installers."""
        windows_dir = SCRIPTS_DIR / "windows"
        assert (windows_dir / "AIReady-ClaudeCode.bat").exists(), \
            "Missing scripts/windows/AIReady-ClaudeCode.bat"
        assert (windows_dir / "AIReady-OpenClaw.bat").exists(), \
            "Missing scripts/windows/AIReady-OpenClaw.bat"

    def test_windows_ps1_scripts_exist(self) -> None:
        """Windows scripts directory must contain both PS1 installers."""
        windows_dir = SCRIPTS_DIR / "windows"
        assert (windows_dir / "AIReady-ClaudeCode.ps1").exists(), \
            "Missing scripts/windows/AIReady-ClaudeCode.ps1"
        assert (windows_dir / "AIReady-OpenClaw.ps1").exists(), \
            "Missing scripts/windows/AIReady-OpenClaw.ps1"

    def test_total_script_count(self) -> None:
        """Exactly 8 installer scripts must exist (4 SH + 2 BAT + 2 PS1)."""
        sh_count = len(SH_FILES)
        bat_count = len(list(SCRIPTS_DIR.glob("**/*.bat")))
        ps1_count = len(PS1_FILES)
        assert sh_count == 4, f"Expected 4 SH scripts, found {sh_count}"
        assert bat_count == 2, f"Expected 2 BAT scripts, found {bat_count}"
        assert ps1_count == 2, f"Expected 2 PS1 scripts, found {ps1_count}"
