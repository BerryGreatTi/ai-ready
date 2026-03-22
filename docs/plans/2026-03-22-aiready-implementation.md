# AIReady Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a cross-platform installer helper (GUI + scripts) for beginners to install Claude Code and OpenClaw.

**Architecture:** Layered Core with Platform/Tool abstractions. Python + CustomTkinter GUI packaged via PyInstaller. Independent native scripts (BAT/PS1/SH) for terminal users.

**Tech Stack:** Python 3.12+, CustomTkinter, PyInstaller, requests, pytest

**Spec:** [docs/specs/2026-03-22-aiready-design.md](../specs/2026-03-22-aiready-design.md)

**Working directory:** All bash commands assume `/home/taeikkim92/Projects/install-ai` unless otherwise specified.

**Note:** Linux does NOT have a GUI build (scripts only per design spec). PyInstaller specs exist only for Windows and macOS.

---

## Phase 1: Project Setup & Core Data Models

### Task 1: Initialize Python project

**Files:**
- Create: `pyproject.toml`
- Create: `src/aiready/__init__.py`
- Create: `src/aiready/core/__init__.py`
- Create: `src/aiready/i18n/__init__.py`
- Create: `src/aiready/platforms/__init__.py`
- Create: `src/aiready/tools/__init__.py`
- Create: `src/aiready/providers/__init__.py`
- Create: `src/aiready/gui/__init__.py`
- Create: `src/aiready/gui/screens/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/unit/core/__init__.py`
- Create: `tests/unit/platforms/__init__.py`
- Create: `tests/unit/tools/__init__.py`
- Create: `tests/unit/i18n/__init__.py`
- Create: `tests/unit/providers/__init__.py`
- Create: `tests/integration/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "aiready"
version = "0.1.0"
requires-python = ">=3.12"
description = "Cross-platform installer helper for AI coding tools"
dependencies = [
    "customtkinter>=5.2",
    "requests>=2.31",
]

[project.optional-dependencies]
dev = [
    "pyinstaller>=6.0",
    "pytest>=8.0",
    "pytest-cov>=5.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.coverage.run]
source = ["aiready"]

[tool.coverage.report]
fail_under = 80
```

- [ ] **Step 2: Create all `__init__.py` files**

All `__init__.py` files are empty except `src/aiready/__init__.py`:

```python
"""AIReady - Cross-platform installer helper for AI coding tools."""

__version__ = "0.1.0"
```

- [ ] **Step 3: Create virtual environment and install dependencies**

Run:
```bash
cd /home/taeikkim92/Projects/install-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

- [ ] **Step 4: Verify pytest runs with zero tests**

Run: `pytest -v`
Expected: "no tests ran" with exit code 5 (no tests collected)

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/ tests/
git commit -m "feat: initialize Python project structure with pyproject.toml"
```

---

### Task 2: Core data models

**Files:**
- Create: `src/aiready/core/models.py`
- Create: `tests/unit/core/test_models.py`

- [ ] **Step 1: Write tests for core data models**

```python
# tests/unit/core/test_models.py
from aiready.core.models import (
    Step, StepResult, StepStatus, InstallResult,
    Prerequisite, PrereqCheckResult,
    CommandResult, OSInfo, ShellType,
)


class TestStepStatus:
    def test_status_values(self):
        assert StepStatus.RUNNING.value == "running"
        assert StepStatus.SUCCESS.value == "success"
        assert StepStatus.FAILED.value == "failed"
        assert StepStatus.SKIPPED.value == "skipped"


class TestStep:
    def test_step_is_frozen(self):
        step = Step(id="test", name_key="step.test", action=lambda: None, required=True)
        assert step.id == "test"
        assert step.required is True

    def test_step_immutable(self):
        step = Step(id="test", name_key="step.test", action=lambda: None, required=True)
        import dataclasses
        with __import__("pytest").raises(dataclasses.FrozenInstanceError):
            step.id = "changed"


class TestStepResult:
    def test_success_result(self):
        result = StepResult(status=StepStatus.SUCCESS, message="Done", detail=None)
        assert result.status == StepStatus.SUCCESS
        assert result.failed is False

    def test_failed_result(self):
        result = StepResult(status=StepStatus.FAILED, message="Error", detail="stack trace")
        assert result.failed is True

    def test_skipped_result(self):
        result = StepResult(status=StepStatus.SKIPPED, message="Not needed", detail=None)
        assert result.failed is False


class TestInstallResult:
    def test_success(self):
        result = InstallResult(success=True)
        assert result.success is True
        assert result.failed_step is None

    def test_failure(self):
        step = Step(id="x", name_key="x", action=lambda: None, required=True)
        error = StepResult(status=StepStatus.FAILED, message="err", detail=None)
        result = InstallResult(success=False, failed_step=step, error=error)
        assert result.success is False
        assert result.failed_step.id == "x"


class TestPrerequisite:
    def test_prerequisite_fields(self):
        p = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        assert p.name == "nodejs"
        assert p.min_version == "22.16"


class TestPrereqCheckResult:
    def test_installed_ok(self):
        p = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        r = PrereqCheckResult(prereq=p, installed=True, current_version="24.1.0", needs_upgrade=False)
        assert r.installed is True
        assert r.needs_upgrade is False

    def test_needs_upgrade(self):
        p = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        r = PrereqCheckResult(prereq=p, installed=True, current_version="18.0.0", needs_upgrade=True)
        assert r.needs_upgrade is True


class TestCommandResult:
    def test_success(self):
        r = CommandResult(return_code=0, stdout="v24.1.0", stderr="")
        assert r.succeeded is True

    def test_failure(self):
        r = CommandResult(return_code=1, stdout="", stderr="not found")
        assert r.succeeded is False


class TestOSInfo:
    def test_os_info(self):
        info = OSInfo(system="Windows", release="10", version="10.0.19041", arch="AMD64")
        assert info.system == "Windows"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/core/test_models.py -v`
Expected: FAIL (ImportError - module not found)

- [ ] **Step 3: Implement core data models**

```python
# src/aiready/core/models.py
"""Core data models for AIReady. All models are immutable (frozen dataclass)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


class StepStatus(Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ShellType(Enum):
    BASH = "bash"
    ZSH = "zsh"
    POWERSHELL = "powershell"
    CMD = "cmd"


@dataclass(frozen=True)
class Step:
    id: str
    name_key: str
    action: Callable[[], StepResult]
    required: bool


@dataclass(frozen=True)
class StepResult:
    status: StepStatus
    message: Optional[str] = None
    detail: Optional[str] = None

    @property
    def failed(self) -> bool:
        return self.status == StepStatus.FAILED


@dataclass(frozen=True)
class InstallResult:
    success: bool
    failed_step: Optional[Step] = None
    error: Optional[StepResult] = None


@dataclass(frozen=True)
class Prerequisite:
    name: str
    min_version: str
    check_command: str


@dataclass(frozen=True)
class PrereqCheckResult:
    prereq: Prerequisite
    installed: bool
    current_version: Optional[str] = None
    needs_upgrade: bool = False


@dataclass(frozen=True)
class CommandResult:
    return_code: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.return_code == 0


@dataclass(frozen=True)
class OSInfo:
    system: str
    release: str
    version: str
    arch: str


@dataclass(frozen=True)
class CommandInfo:
    path: str
    version: Optional[str] = None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/core/test_models.py -v`
Expected: ALL PASS

- [ ] **Step 5: Check coverage**

Run: `pytest tests/unit/core/test_models.py --cov=aiready.core.models --cov-report=term-missing`
Expected: 90%+

- [ ] **Step 6: Commit**

```bash
git add src/aiready/core/models.py tests/unit/core/test_models.py
git commit -m "feat: add core data models (Step, StepResult, Prerequisite, etc.)"
```

---

### Task 3: Version comparison utility

**Files:**
- Create: `src/aiready/core/version.py`
- Create: `tests/unit/core/test_version.py`

- [ ] **Step 1: Write tests for version comparison**

```python
# tests/unit/core/test_version.py
from aiready.core.version import version_gte, parse_version


class TestParseVersion:
    def test_simple(self):
        assert parse_version("1.2.3") == (1, 2, 3)

    def test_with_v_prefix(self):
        assert parse_version("v24.1.0") == (24, 1, 0)

    def test_two_parts(self):
        assert parse_version("22.16") == (22, 16)

    def test_single(self):
        assert parse_version("5") == (5,)

    def test_strips_extra(self):
        assert parse_version("v18.0.0-lts") == (18, 0, 0)


class TestVersionGte:
    def test_equal(self):
        assert version_gte("22.16.0", "22.16") is True

    def test_greater(self):
        assert version_gte("24.1.0", "22.16") is True

    def test_less(self):
        assert version_gte("18.0.0", "22.16") is False

    def test_with_v_prefix(self):
        assert version_gte("v24.1.0", "22.16") is True

    def test_patch_comparison(self):
        assert version_gte("22.16.1", "22.16.0") is True
        assert version_gte("22.15.9", "22.16.0") is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/core/test_version.py -v`
Expected: FAIL

- [ ] **Step 3: Implement version utilities**

```python
# src/aiready/core/version.py
"""Semantic version parsing and comparison."""

from __future__ import annotations

import re


def parse_version(version_str: str) -> tuple[int, ...]:
    cleaned = version_str.strip().lstrip("v")
    cleaned = re.split(r"[^0-9.]", cleaned)[0]
    parts = cleaned.split(".")
    return tuple(int(p) for p in parts if p)


def version_gte(current: str, minimum: str) -> bool:
    cur = parse_version(current)
    min_ = parse_version(minimum)
    max_len = max(len(cur), len(min_))
    cur_padded = cur + (0,) * (max_len - len(cur))
    min_padded = min_ + (0,) * (max_len - len(min_))
    return cur_padded >= min_padded
```

- [ ] **Step 4: Run tests and verify pass**

Run: `pytest tests/unit/core/test_version.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/aiready/core/version.py tests/unit/core/test_version.py
git commit -m "feat: add version parsing and comparison utility"
```

---

## Phase 2: Internationalization

### Task 4: i18n string system

**Files:**
- Create: `src/aiready/i18n/strings.py`
- Create: `src/aiready/i18n/en.json`
- Create: `src/aiready/i18n/ko.json`
- Create: `tests/unit/i18n/test_strings.py`

- [ ] **Step 1: Write tests for i18n system**

```python
# tests/unit/i18n/test_strings.py
import json
from pathlib import Path
from aiready.i18n.strings import I18n

I18N_DIR = Path(__file__).resolve().parents[3] / "src" / "aiready" / "i18n"


class TestI18n:
    def test_load_english(self):
        i18n = I18n("en")
        assert i18n.get("app.title") == "AIReady - AI Tool Setup Helper"

    def test_load_korean(self):
        i18n = I18n("ko")
        assert "AIReady" in i18n.get("app.title")

    def test_fallback_to_english(self):
        i18n = I18n("ko")
        result = i18n.get("nonexistent.key")
        assert result == "nonexistent.key"

    def test_interpolation(self):
        i18n = I18n("en")
        result = i18n.get("error.version_mismatch", required="22.16", current="18.0")
        assert "22.16" in result
        assert "18.0" in result

    def test_change_language(self):
        i18n = I18n("en")
        assert i18n.language == "en"
        i18n.set_language("ko")
        assert i18n.language == "ko"


class TestI18nKeyParity:
    def test_all_en_keys_exist_in_ko(self):
        en = json.loads((I18N_DIR / "en.json").read_text(encoding="utf-8"))
        ko = json.loads((I18N_DIR / "ko.json").read_text(encoding="utf-8"))
        missing = set(en.keys()) - set(ko.keys())
        assert missing == set(), f"Keys missing in ko.json: {missing}"

    def test_all_ko_keys_exist_in_en(self):
        en = json.loads((I18N_DIR / "en.json").read_text(encoding="utf-8"))
        ko = json.loads((I18N_DIR / "ko.json").read_text(encoding="utf-8"))
        extra = set(ko.keys()) - set(en.keys())
        assert extra == set(), f"Extra keys in ko.json not in en.json: {extra}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/i18n/test_strings.py -v`
Expected: FAIL

- [ ] **Step 3: Create en.json with initial strings**

Create `src/aiready/i18n/en.json` with all UI strings. Include keys for:
- `app.title`, `app.subtitle`
- `lang.select.title`, `lang.korean`, `lang.english`
- `tool.select.title`, `tool.claude_code.name`, `tool.claude_code.desc`, `tool.claude_code.note`, `tool.openclaw.name`, `tool.openclaw.desc`, `tool.openclaw.note`
- `step.check_system`, `step.install_git`, `step.install_nodejs`, `step.install_tool`, `step.verify_install`, `step.run_doctor`, `step.authenticate`, `step.verify_auth`, `step.select_provider`, `step.configure_api_key`, `step.validate_api_key`, `step.run_onboarding`, `step.verify_gateway`, `step.verify_prereqs`, `step.install_tool_fallback`
- `progress.title`, `progress.status.done`, `progress.status.running`, `progress.status.waiting`, `progress.status.failed`
- `error.network`, `error.permission`, `error.disk_full`, `error.path_not_updated`, `error.version_mismatch`, `error.invalid_api_key`, `error.verification_failed`
- `provider.select.title`, `provider.anthropic`, `provider.openai`, `provider.gemini`, `provider.mistral`, `provider.cohere`, `provider.ollama`, `provider.recommended`, `provider.local_no_key`
- `apikey.title`, `apikey.prompt`, `apikey.paste`, `apikey.show`, `apikey.hide`, `apikey.get_key`, `apikey.validate`, `apikey.valid`, `apikey.invalid`, `apikey.validating`
- `auth.title`, `auth.step1`, `auth.step2`, `auth.step3`, `auth.subscription_warning`, `auth.open_browser`, `auth.verify`
- `complete.title`, `complete.success`, `complete.command_hint`, `complete.copy`, `complete.new_terminal_notice`, `complete.open_terminal`, `complete.exit`
- `button.next`, `button.back`, `button.retry`, `button.view_log`, `button.exit`
- `elevation.reason.install_package`, `elevation.denied`

- [ ] **Step 4: Create ko.json with all matching keys (Korean translations)**

Mirror every key from `en.json`. Translate all UI-facing strings to Korean. Keep technical terms (API key, CLI, PATH, Node.js, Git, OAuth, URL) and product names (Claude Code, OpenClaw, Anthropic, OpenAI, Gemini, Ollama) in English.

- [ ] **Step 5: Implement I18n class**

```python
# src/aiready/i18n/strings.py
"""Internationalization string loader with interpolation and fallback."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class I18n:
    _SUPPORTED = ("en", "ko")
    _DIR = Path(__file__).parent

    def __init__(self, language: str = "en"):
        self._strings: dict[str, dict[str, str]] = {}
        for lang in self._SUPPORTED:
            path = self._DIR / f"{lang}.json"
            if path.exists():
                self._strings[lang] = json.loads(path.read_text(encoding="utf-8"))
        self._language = language if language in self._SUPPORTED else "en"

    @property
    def language(self) -> str:
        return self._language

    def set_language(self, language: str) -> None:
        if language in self._SUPPORTED:
            self._language = language

    def get(self, key: str, **kwargs: str) -> str:
        value = self._strings.get(self._language, {}).get(key)
        if value is None:
            value = self._strings.get("en", {}).get(key)
        if value is None:
            return key
        if kwargs:
            try:
                value = value.format(**kwargs)
            except KeyError:
                pass
        return value
```

- [ ] **Step 6: Run tests and verify pass**

Run: `pytest tests/unit/i18n/test_strings.py -v`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add src/aiready/i18n/ tests/unit/i18n/
git commit -m "feat: add i18n system with Korean and English translations"
```

---

## Phase 3: Platform Layer

### Task 5: Platform base interface and detect

**Files:**
- Create: `src/aiready/platforms/base.py`
- Create: `src/aiready/platforms/detect.py`
- Create: `tests/unit/platforms/test_base.py`
- Create: `tests/unit/platforms/test_detect.py`

- [ ] **Step 1: Write tests**

Test that `Platform` is abstract and cannot be instantiated directly. Test `detect_platform()` returns the correct platform type for the current OS (use mocking for cross-platform coverage).

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/platforms/ -v`

- [ ] **Step 3: Implement Platform ABC**

Define all abstract methods from the design spec: `get_os_info`, `check_command`, `install_prerequisite`, `verify_prerequisite`, `add_to_path`, `request_elevation`, `run_command`, `get_temp_dir`, `open_browser`, `get_shell_type`.

- [ ] **Step 4: Implement detect_platform()**

Uses `platform.system()` to return `WindowsPlatform`, `MacOSPlatform`, or `LinuxPlatform`. Raises `UnsupportedPlatformError` for unknown systems.

- [ ] **Step 5: Run tests and verify pass**

- [ ] **Step 6: Commit**

```bash
git add src/aiready/platforms/base.py src/aiready/platforms/detect.py tests/unit/platforms/
git commit -m "feat: add Platform ABC and OS detection"
```

---

### Task 6: Process wrapper (subprocess utility)

**Files:**
- Create: `src/aiready/core/process.py`
- Create: `tests/unit/core/test_process.py`

- [ ] **Step 1: Write tests**

Test `run_command` with a simple command (`echo hello`), test timeout behavior, test that output is captured in `CommandResult`.

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement process.py**

Wrap `subprocess.run` with timeout, output capture, and error handling. Return `CommandResult` (immutable). Use `shlex.split` on non-Windows, pass list directly on Windows.

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/core/process.py tests/unit/core/test_process.py
git commit -m "feat: add subprocess wrapper with timeout and output capture"
```

---

### Task 7: Linux platform implementation

**Files:**
- Create: `src/aiready/platforms/linux.py`
- Create: `tests/unit/platforms/test_linux.py`

Why Linux first: It's the current development environment, so we can run integration tests directly.

- [ ] **Step 1: Write tests**

Test `_detect_distro` (mock `/etc/os-release`), `_detect_package_manager` (mock `which`), `check_command` with mocked subprocess, `get_os_info`, `get_shell_type`, `add_to_path` (mock file write to `~/.bashrc`).

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement LinuxPlatform**

Implement all `Platform` abstract methods. `_detect_distro` parses `/etc/os-release`. `_detect_package_manager` checks for apt-get, dnf, pacman, apk. `install_prerequisite` uses NodeSource repo for Node.js. `add_to_path` appends to `~/.bashrc` or `~/.zshrc`.

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/platforms/linux.py tests/unit/platforms/test_linux.py
git commit -m "feat: add Linux platform implementation"
```

---

### Task 8: macOS platform implementation

**Files:**
- Create: `src/aiready/platforms/macos.py`
- Create: `tests/unit/platforms/test_macos.py`

- [ ] **Step 1: Write tests**

Test `check_command` (mock `which`), `install_prerequisite` (mock brew detection + subprocess), `add_to_path` (mock ~/.zshrc write), `get_shell_type` (detect zsh as default). Use mocking since development may not be on macOS.

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement MacOSPlatform**

brew detection and usage for Node.js. Fallback to .pkg download. `add_to_path` writes to `~/.zshrc` (default) or `~/.bashrc`. `open_browser` uses `open` command. `request_elevation` uses `osascript` for GUI sudo.

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/platforms/macos.py tests/unit/platforms/test_macos.py
git commit -m "feat: add macOS platform implementation"
```

---

### Task 9: Windows platform implementation

**Files:**
- Create: `src/aiready/platforms/windows.py`
- Create: `tests/unit/platforms/test_windows.py`

- [ ] **Step 1: Write tests**

Test `check_command` (mock `where.exe` + known paths), `install_prerequisite` (mock download + msiexec), `add_to_path` (mock winreg), `request_elevation` (mock ctypes). All using mocks since development is on Linux.

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement WindowsPlatform**

`check_command`: try `where.exe`, fallback to known paths (`C:\Program Files\Git`, `C:\Program Files\nodejs`). `install_prerequisite`: direct .msi/.exe download (no winget). `add_to_path`: use `winreg` for HKCU user PATH. `request_elevation`: `ctypes.windll.shell32`. Guard all Windows-specific imports with `if sys.platform == "win32"`.

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/platforms/windows.py tests/unit/platforms/test_windows.py
git commit -m "feat: add Windows platform implementation"
```

---

## Phase 4: Missing Core Modules

### Task 10: Prerequisite checker module

**Files:**
- Create: `src/aiready/core/prereqs.py`
- Create: `tests/unit/core/test_prereqs.py`

- [ ] **Step 1: Write tests**

Test `PrerequisiteChecker.check(prereq, platform)` returns `PrereqCheckResult` with correct `installed`, `current_version`, `needs_upgrade` fields. Test version comparison integration (uses `version_gte`). Test that missing command returns `installed=False`. Test that outdated version returns `needs_upgrade=True`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/core/test_prereqs.py -v`

- [ ] **Step 3: Implement PrerequisiteChecker**

```python
# src/aiready/core/prereqs.py
class PrerequisiteChecker:
    def __init__(self, platform: Platform):
        self._platform = platform

    def check(self, prereq: Prerequisite) -> PrereqCheckResult:
        cmd_info = self._platform.check_command(prereq.check_command.split()[0])
        if cmd_info is None:
            return PrereqCheckResult(prereq=prereq, installed=False)
        current = cmd_info.version
        needs_upgrade = not version_gte(current, prereq.min_version) if current else True
        return PrereqCheckResult(
            prereq=prereq, installed=True,
            current_version=current, needs_upgrade=needs_upgrade
        )

    def check_all(self, prereqs: list[Prerequisite]) -> list[PrereqCheckResult]:
        return [self.check(p) for p in prereqs]
```

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/core/prereqs.py tests/unit/core/test_prereqs.py
git commit -m "feat: add prerequisite checker module"
```

---

### Task 11: Permission manager module

**Files:**
- Create: `src/aiready/core/permissions.py`
- Create: `tests/unit/core/test_permissions.py`

- [ ] **Step 1: Write tests**

Test `needs_elevation(operation)` returns True for system-level operations (install_package, write_system_dir), False for user-level operations (check_version, download, modify_user_path). Test `request_elevation(platform, reason_key)` delegates to `platform.request_elevation()`. Test that elevation denied returns failure result.

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement PermissionManager**

```python
# src/aiready/core/permissions.py
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
```

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/core/permissions.py tests/unit/core/test_permissions.py
git commit -m "feat: add permission manager module"
```

---

### Task 12: Installation validator module

**Files:**
- Create: `src/aiready/core/validator.py`
- Create: `tests/unit/core/test_validator.py`

- [ ] **Step 1: Write tests**

Test `validate_installation(command, expected_version)` runs command and checks version output. Test success case (command exists, version matches). Test failure case (command not found). Test version mismatch case. Test `validate_with_retry(command, retries=1)` retries once on failure.

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement InstallationValidator**

```python
# src/aiready/core/validator.py
class InstallationValidator:
    def __init__(self, platform: Platform):
        self._platform = platform

    def validate(self, command: str, min_version: str | None = None) -> StepResult:
        result = self._platform.run_command(command.split())
        if not result.succeeded:
            return StepResult(status=StepStatus.FAILED, message=f"Command failed: {command}")
        if min_version:
            version = result.stdout.strip()
            if not version_gte(version, min_version):
                return StepResult(
                    status=StepStatus.FAILED,
                    message=f"Version {version} < {min_version}"
                )
        return StepResult(status=StepStatus.SUCCESS)

    def validate_with_retry(self, command: str, min_version: str | None = None, retries: int = 1) -> StepResult:
        for _ in range(retries + 1):
            result = self.validate(command, min_version)
            if not result.failed:
                return result
        return result
```

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/core/validator.py tests/unit/core/test_validator.py
git commit -m "feat: add installation validator with retry support"
```

---

## Phase 5: Provider Registry

### Task 13: AI provider registry

**Files:**
- Create: `src/aiready/providers/registry.py`
- Create: `tests/unit/providers/test_registry.py`

- [ ] **Step 1: Write tests**

```python
# tests/unit/providers/test_registry.py
from aiready.providers.registry import AIProvider, get_providers, get_provider_by_id


class TestProviderRegistry:
    def test_provider_count(self):
        providers = get_providers()
        assert len(providers) == 6

    def test_sorted_by_priority(self):
        providers = get_providers()
        assert providers[0].id == "anthropic"
        assert providers[1].id == "openai"
        assert providers[2].id == "gemini"
        assert providers[-1].id == "ollama"

    def test_anthropic_details(self):
        p = get_provider_by_id("anthropic")
        assert p is not None
        assert p.env_var == "ANTHROPIC_API_KEY"
        assert p.is_local is False
        assert p.priority == 1

    def test_ollama_is_local(self):
        p = get_provider_by_id("ollama")
        assert p is not None
        assert p.is_local is True

    def test_unknown_provider(self):
        assert get_provider_by_id("nonexistent") is None

    def test_all_providers_have_api_key_url(self):
        for p in get_providers():
            if not p.is_local:
                assert p.api_key_url.startswith("https://")

    def test_providers_are_frozen(self):
        import dataclasses
        import pytest
        p = get_provider_by_id("anthropic")
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.id = "changed"
```

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement registry.py**

Define `AIProvider` dataclass and hardcoded list of 6 providers. `get_providers()` returns sorted list. `get_provider_by_id()` returns single provider or None.

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/providers/registry.py tests/unit/providers/test_registry.py
git commit -m "feat: add AI provider registry with 6 initial providers"
```

---

## Phase 6: Core Engine

### Task 14: Downloader with retry and progress

**Files:**
- Create: `src/aiready/core/downloader.py`
- Create: `tests/unit/core/test_downloader.py`

- [ ] **Step 1: Write tests**

Test retry logic (mock requests to fail 2x then succeed), test checksum validation (mock file hash), test progress callback invocation, test timeout handling. Use `unittest.mock.patch` on `requests.get`.

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement Downloader class**

Use `requests` with streaming, write to temp file, optional SHA256 checksum verification, exponential backoff retry (3 attempts, 1s/2s/4s), progress callback with bytes downloaded/total. Detect system proxy via `requests` (automatic from env vars).

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/core/downloader.py tests/unit/core/test_downloader.py
git commit -m "feat: add downloader with retry, checksum, and progress callback"
```

---

### Task 15: PATH manager

**Files:**
- Create: `src/aiready/core/path_manager.py`
- Create: `tests/unit/core/test_path_manager.py`

- [ ] **Step 1: Write tests**

Test `check_in_path` (mock `shutil.which`), test `add_to_path` delegates to platform, test duplicate prevention logic, test PATH refresh for current session.

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement PathManager**

`check(command)` uses `shutil.which`. `add(path, platform)` delegates to `platform.add_to_path()` after checking for duplicates. `refresh_session()` updates `os.environ["PATH"]` for the current process.

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/core/path_manager.py tests/unit/core/test_path_manager.py
git commit -m "feat: add PATH manager with duplicate prevention"
```

---

### Task 16: Installation logger

**Files:**
- Create: `src/aiready/core/logger.py`
- Create: `tests/unit/core/test_logger.py`

- [ ] **Step 1: Write tests**

Test log entry format, test API key masking (`sk-ant-api03-xxx` -> `sk-ant-***`), test log file creation in temp directory, test that previous log is overwritten on new run.

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement InstallLogger**

Plain text format: `[2026-03-22 15:30:00] [INFO] [step.install_nodejs] Installing Node.js...`. Mask patterns: `sk-ant-*`, `sk-*`, `key-*`. Write to `{tempdir}/aiready/install.log`. Privacy: local only. On new run, **truncate** previous log file (do not append).

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/core/logger.py tests/unit/core/test_logger.py
git commit -m "feat: add installation logger with sensitive data masking"
```

---

### Task 17: Installer orchestration engine

**Files:**
- Create: `src/aiready/core/installer.py`
- Create: `tests/unit/core/test_installer.py`

- [ ] **Step 1: Write tests**

Test full run with mock Tool that returns 3 steps (all succeed). Test abort on required step failure. Test non-required step failure continues. Test progress callback receives correct step index and status. Test retry on verification failure.

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement Installer class**

Takes `Platform`, `Tool`, `I18n`, and `InstallLogger`. `run(on_progress)` iterates through `tool.get_steps(platform)`, calls each step's action, reports progress via callback. Aborts on required step failure. Returns `InstallResult`.

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Check coverage for entire core/**

Run: `pytest tests/unit/core/ --cov=aiready.core --cov-report=term-missing`
Expected: 90%+

- [ ] **Step 6: Commit**

```bash
git add src/aiready/core/installer.py tests/unit/core/test_installer.py
git commit -m "feat: add installer orchestration engine"
```

---

## Phase 7: Tool Definitions

### Task 18: Tool base interface

**Files:**
- Create: `src/aiready/tools/base.py`
- Create: `tests/unit/tools/test_base.py`

- [ ] **Step 1: Write tests**

Test that `Tool` is abstract and cannot be instantiated. Test `OnboardingConfig` and `OnboardingMode` enum.

- [ ] **Step 2: Implement Tool ABC and OnboardingConfig**

```python
class OnboardingMode(Enum):
    AUTOMATIC = "automatic"
    GUIDED = "guided"

@dataclass(frozen=True)
class OnboardingConfig:
    mode: OnboardingMode
    provider_selection: bool = False
    api_key_input: bool = False
    ...

class Tool(ABC):
    @abstractmethod
    def get_name(self) -> str: ...
    @abstractmethod
    def get_prerequisites(self, platform: Platform) -> list[Prerequisite]: ...
    @abstractmethod
    def get_steps(self, platform: Platform) -> list[Step]: ...
    @abstractmethod
    def get_verify_commands(self) -> list[str]: ...
    @abstractmethod
    def get_onboarding_config(self) -> OnboardingConfig: ...
```

- [ ] **Step 3: Run tests and verify pass**

- [ ] **Step 4: Commit**

```bash
git add src/aiready/tools/base.py tests/unit/tools/test_base.py
git commit -m "feat: add Tool ABC and OnboardingConfig"
```

---

### Task 19: Claude Code tool implementation

**Files:**
- Create: `src/aiready/tools/claude_code.py`
- Create: `tests/unit/tools/test_claude_code.py`

- [ ] **Step 1: Write tests**

Test `get_prerequisites` returns Git for mock Windows platform, empty for mock macOS/Linux. Test `get_steps` returns correct step count and IDs. Test `get_onboarding_config` returns GUIDED mode. Test `get_verify_commands` includes `claude --version` and `claude doctor`. Test platform-specific install commands (CMD for Windows, curl for macOS/Linux).

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement ClaudeCodeTool**

8 steps as defined in design spec. Platform-specific install command selection. GUIDED onboarding with browser auth.

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/tools/claude_code.py tests/unit/tools/test_claude_code.py
git commit -m "feat: add Claude Code tool definition with platform-specific install"
```

---

### Task 20: OpenClaw tool implementation

**Files:**
- Create: `src/aiready/tools/openclaw.py`
- Create: `tests/unit/tools/test_openclaw.py`

- [ ] **Step 1: Write tests**

Test `get_prerequisites` returns Node.js for all platforms. Test `get_steps` returns 12 steps. Test fallback step (install_tool_fallback) exists after install_tool. Test `get_onboarding_config` returns AUTOMATIC mode with provider_selection=True. Test API key validation step with mock HTTP.

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement OpenClawTool**

12 steps as defined in design spec. Fallback from official installer to npm. AUTOMATIC onboarding with provider selection and API key validation.

- [ ] **Step 4: Run tests and verify pass**

- [ ] **Step 5: Commit**

```bash
git add src/aiready/tools/openclaw.py tests/unit/tools/test_openclaw.py
git commit -m "feat: add OpenClaw tool definition with npm fallback"
```

---

## Phase 8: Integration Test

### Task 21: Full installation flow integration test

**Files:**
- Create: `tests/integration/test_install_flow.py`

- [ ] **Step 1: Write integration tests**

Create a `MockPlatform` that simulates successful command execution. Wire it with `ClaudeCodeTool` and `OpenClawTool`. Test that `Installer.run()` progresses through all steps and returns success. Test that progress callback receives all step updates in order. Test failure scenario (mock a step failure mid-flow).

- [ ] **Step 2: Run integration tests**

Run: `pytest tests/integration/ -v`
Expected: ALL PASS

- [ ] **Step 3: Run full test suite with coverage**

Run: `pytest --cov=aiready --cov-report=term-missing`
Expected: 80%+ overall

- [ ] **Step 4: Commit**

```bash
git add tests/integration/test_install_flow.py
git commit -m "test: add integration tests for full installation flow"
```

---

## Phase 9: GUI

### Task 22: GUI app skeleton and theme

**Files:**
- Create: `src/aiready/gui/app.py`
- Create: `src/aiready/gui/theme.py`
- Create: `src/aiready/main.py`

- [ ] **Step 1: Implement theme.py**

Define color constants, font sizes, padding values. Configure CustomTkinter appearance mode to follow system. Window dimensions: 480x640.

- [ ] **Step 2: Implement app.py - main application window**

`AIReadyApp(ctk.CTk)` class. Fixed 480x640, non-resizable. Screen navigation via `show_screen(screen_class)`. Holds reference to `I18n`, `Platform`, `Tool`, and `InstallLogger` instances.

- [ ] **Step 3: Implement main.py - entry point**

```python
def run(tool: str | None = None):
    platform = detect_platform()
    i18n = I18n("en")  # default, changed by language select
    app = AIReadyApp(platform=platform, i18n=i18n, preset_tool=tool)
    app.mainloop()
```

- [ ] **Step 4: Test manually - app window opens and closes**

Run: `cd /home/taeikkim92/Projects/install-ai && python -m aiready.main`
Expected: Empty window opens at 480x640

- [ ] **Step 5: Commit**

```bash
git add src/aiready/gui/app.py src/aiready/gui/theme.py src/aiready/main.py
git commit -m "feat: add GUI app skeleton with CustomTkinter"
```

---

### Task 23: Language select screen

**Files:**
- Create: `src/aiready/gui/screens/language_select.py`

- [ ] **Step 1: Implement language select screen**

Two large buttons: "Korean" and "English". Centered layout with AIReady title. On selection: update `app.i18n.set_language()`, navigate to tool select screen.

- [ ] **Step 2: Test manually**

Run the app. Verify both buttons appear, clicking switches language and navigates.

- [ ] **Step 3: Commit**

```bash
git add src/aiready/gui/screens/language_select.py
git commit -m "feat: add language selection screen"
```

---

### Task 24: Tool select screen

**Files:**
- Create: `src/aiready/gui/screens/tool_select.py`

- [ ] **Step 1: Implement tool select screen**

Card-style buttons for Claude Code and OpenClaw. Each card shows: tool name (i18n), one-line description (i18n), requirement note (i18n). Single selection. "Next" button. "Back" button returns to language select. If `preset_tool` is set (PyInstaller build), skip this screen.

- [ ] **Step 2: Test manually**

- [ ] **Step 3: Commit**

```bash
git add src/aiready/gui/screens/tool_select.py
git commit -m "feat: add tool selection screen with card-style buttons"
```

---

### Task 25: Progress screen

**Files:**
- Create: `src/aiready/gui/screens/progress.py`

- [ ] **Step 1: Implement progress screen**

Step checklist with dynamic rendering from `tool.get_steps()`. Status indicators: checkmark (done), spinning dot (running), circle (waiting), X (failed). Overall progress bar. Current operation detail text. Error state: red indicator, error message, Retry/View Log/Exit buttons. Runs `Installer.run()` in a background thread (tkinter is single-threaded).

Key implementation detail: Use `threading.Thread` for installer execution, `app.after()` for UI updates from the background thread.

- [ ] **Step 2: Test manually with a mock tool that has 3 quick steps**

- [ ] **Step 3: Commit**

```bash
git add src/aiready/gui/screens/progress.py
git commit -m "feat: add installation progress screen with background execution"
```

---

### Task 26: Provider select screen (OpenClaw)

**Files:**
- Create: `src/aiready/gui/screens/provider_select.py`

- [ ] **Step 1: Implement provider select screen**

Radio button list loaded from `get_providers()`. Top 3 above separator. Anthropic has "Recommended" badge. Ollama at bottom with "(Local - No API key needed)" label. "Next" button. "Back" button.

- [ ] **Step 2: Test manually**

- [ ] **Step 3: Commit**

```bash
git add src/aiready/gui/screens/provider_select.py
git commit -m "feat: add AI provider selection screen"
```

---

### Task 27: API key input screen

**Files:**
- Create: `src/aiready/gui/screens/api_key.py`

- [ ] **Step 1: Implement API key input screen**

Masked text field (show `*`). Paste button (reads clipboard). Show/Hide toggle. "Get API Key" link (opens provider's `api_key_url` in browser). Validate button (runs test API call in background thread, shows spinner). Validation result display. Skip this screen entirely if Ollama was selected.

- [ ] **Step 2: Test manually**

- [ ] **Step 3: Commit**

```bash
git add src/aiready/gui/screens/api_key.py
git commit -m "feat: add API key input screen with validation"
```

---

### Task 28: Onboarding screen (unified for both tools)

**Files:**
- Create: `src/aiready/gui/screens/onboarding.py`

- [ ] **Step 1: Implement auth/onboarding screen**

Single file handles both tools via conditional logic based on selected tool. For Claude Code (GUIDED): numbered step instructions, subscription warning, "Open Browser" button, "Verify Authentication" button (clicking runs `claude doctor` to confirm auth, retries on failure). For OpenClaw (AUTOMATIC): runs `openclaw onboard --install-daemon` with progress display.

- [ ] **Step 2: Test manually**

- [ ] **Step 3: Commit**

```bash
git add src/aiready/gui/screens/onboarding.py
git commit -m "feat: add onboarding/auth guide screen"
```

---

### Task 29: Complete screen

**Files:**
- Create: `src/aiready/gui/screens/complete.py`

- [ ] **Step 1: Implement complete screen**

Success message. Command box with copy button. "New terminal required" notice (if PATH was updated). "Open Terminal" button (platform-specific). "Exit" button.

- [ ] **Step 2: Test full GUI flow manually (language -> tool -> progress -> complete)**

- [ ] **Step 3: Commit**

```bash
git add src/aiready/gui/screens/complete.py
git commit -m "feat: add installation complete screen"
```

---

## Phase 10: Native Scripts

### Task 30: macOS Claude Code script

**Files:**
- Create: `scripts/macos/AIReady-ClaudeCode.sh`

- [ ] **Step 1: Write the script**

Follow design spec section 7. Include: shebang, `set -euo pipefail`, language selection, color output, system check, Claude Code native installer (`curl | bash`), `claude --version` verification, `claude doctor`, auth guide (print instructions + open browser with `open` command).

- [ ] **Step 2: Run shellcheck**

Run: `shellcheck scripts/macos/AIReady-ClaudeCode.sh`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add scripts/macos/AIReady-ClaudeCode.sh
git commit -m "feat: add macOS Claude Code installation script"
```

---

### Task 31: macOS OpenClaw script

**Files:**
- Create: `scripts/macos/AIReady-OpenClaw.sh`

- [ ] **Step 1: Write the script**

Language selection, system check, Node.js check/install (brew or .pkg), OpenClaw installer script, fallback to npm, provider selection (text menu), API key input (`read -s`), `openclaw onboard --install-daemon`, verification.

- [ ] **Step 2: Run shellcheck**

- [ ] **Step 3: Commit**

```bash
git add scripts/macos/AIReady-OpenClaw.sh
git commit -m "feat: add macOS OpenClaw installation script"
```

---

### Task 32: Linux Claude Code script

**Files:**
- Create: `scripts/linux/AIReady-ClaudeCode.sh`

- [ ] **Step 1: Write the script**

Similar to macOS but without brew. System check, Claude Code native installer, verification, auth guide.

- [ ] **Step 2: Run shellcheck**

- [ ] **Step 3: Commit**

```bash
git add scripts/linux/AIReady-ClaudeCode.sh
git commit -m "feat: add Linux Claude Code installation script"
```

---

### Task 33: Linux OpenClaw script

**Files:**
- Create: `scripts/linux/AIReady-OpenClaw.sh`

- [ ] **Step 1: Write the script**

Distro detection (`/etc/os-release`), package manager detection, Node.js install (NodeSource for apt/dnf, pacman for Arch), OpenClaw install with npm fallback, provider selection, API key, onboarding, verification.

- [ ] **Step 2: Run shellcheck**

- [ ] **Step 3: Commit**

```bash
git add scripts/linux/AIReady-OpenClaw.sh
git commit -m "feat: add Linux OpenClaw installation script"
```

---

### Task 34: Windows Claude Code BAT script

**Files:**
- Create: `scripts/windows/AIReady-ClaudeCode.bat`

- [ ] **Step 1: Write the script**

`@echo off`, `chcp 65001`, `setlocal EnableDelayedExpansion`. Language selection. Git check (via `where git` + known paths). Git install (direct .exe download with `curl`). Claude Code install via `install.cmd`. Verification. Auth guide (print instructions + `start` to open browser).

Encoding constraint: minimize non-ASCII, use variables for Korean messages.

- [ ] **Step 2: Verify syntax (review manually for BAT correctness)**

- [ ] **Step 3: Commit**

```bash
git add scripts/windows/AIReady-ClaudeCode.bat
git commit -m "feat: add Windows BAT script for Claude Code installation"
```

---

### Task 35: Windows OpenClaw BAT script

**Files:**
- Create: `scripts/windows/AIReady-OpenClaw.bat`

- [ ] **Step 1: Write the script**

Language selection. Node.js check/install (direct .msi). OpenClaw installer (PowerShell one-liner or npm fallback). Provider text menu. API key input (`set /p`). Onboarding. Verification.

- [ ] **Step 2: Verify syntax**

- [ ] **Step 3: Commit**

```bash
git add scripts/windows/AIReady-OpenClaw.bat
git commit -m "feat: add Windows BAT script for OpenClaw installation"
```

---

### Task 36: Windows PS1 scripts (secondary)

**Files:**
- Create: `scripts/windows/AIReady-ClaudeCode.ps1`
- Create: `scripts/windows/AIReady-OpenClaw.ps1`

- [ ] **Step 1: Write both PS1 scripts**

Follow design spec. `[Console]::OutputEncoding = UTF8`. All strings from hashtable (no inline Korean). PS 5.1 syntax. `-UseBasicParsing` for web requests.

- [ ] **Step 2: Verify PS 5.1 syntax compatibility (no `??`, `?.`, `&&`)**

- [ ] **Step 3: Commit**

```bash
git add scripts/windows/AIReady-ClaudeCode.ps1 scripts/windows/AIReady-OpenClaw.ps1
git commit -m "feat: add Windows PowerShell scripts (secondary)"
```

---

### Task 37: Script tests

**Files:**
- Create: `tests/scripts/test_sh_syntax.sh`
- Create: `tests/scripts/test_script_lint.py`

- [ ] **Step 1: Create shellcheck test runner**

Run `shellcheck` on all .sh files. Run basic BAT syntax checks (balanced parentheses, no common errors). Verify PS1 files don't use PS 7+ syntax (grep for `??`, `?.`, `&&`).

- [ ] **Step 2: Run script tests**

Run: `pytest tests/scripts/ -v`
Expected: ALL PASS (assuming shellcheck is installed)

- [ ] **Step 3: Commit**

```bash
git add tests/scripts/
git commit -m "test: add script linting and syntax verification tests"
```

---

## Phase 11: Build & Distribution

### Task 38: PyInstaller entry points and specs

**Files:**
- Create: `build/entry_claude_code.py`
- Create: `build/entry_openclaw.py`
- Create: `build/pyinstaller/windows-claude.spec`
- Create: `build/pyinstaller/windows-openclaw.spec`
- Create: `build/pyinstaller/macos-claude.spec`
- Create: `build/pyinstaller/macos-openclaw.spec`

- [ ] **Step 1: Create entry points**

```python
# build/entry_claude_code.py
from aiready.main import run
run(tool="claude_code")

# build/entry_openclaw.py
from aiready.main import run
run(tool="openclaw")
```

- [ ] **Step 2: Create PyInstaller spec files**

Each spec: `--onefile`, `--windowed` (GUI), include `i18n/*.json` as data files, set name to `AIReady-{Tool}-{Platform}`.

- [ ] **Step 3: Test local build (Linux, for verification)**

Run: `pyinstaller build/pyinstaller/linux-claude.spec` (if applicable, or just test that spec parsing works)

- [ ] **Step 4: Commit**

```bash
git add build/
git commit -m "feat: add PyInstaller entry points and build specs"
```

---

### Task 39: Build automation script

**Files:**
- Create: `.dev/scripts/build-all.sh`
- Create: `.dev/scripts/build-release.sh`

- [ ] **Step 1: Write build-all.sh**

Takes version argument. Runs PyInstaller for current platform. Copies scripts. Generates CHECKSUMS.txt. Outputs to `release/<version>/`.

- [ ] **Step 2: Write build-release.sh**

Orchestrates full release: tag git, build, collect artifacts.

- [ ] **Step 3: Commit**

```bash
git add .dev/scripts/build-all.sh .dev/scripts/build-release.sh
git commit -m "feat: add build automation scripts"
```

---

### Task 40: GitHub Actions CI/CD

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Create CI workflow**

Triggers on push/PR. Matrix: ubuntu-latest, macos-latest, windows-latest. Steps: checkout, setup Python 3.12, install deps, run `pytest --cov`, run shellcheck (Linux only), run script lint tests.

- [ ] **Step 2: Create release workflow**

Triggers on tag push (`v*`). Matrix builds: Windows .exe (windows-latest), macOS .app (macos-latest). Upload artifacts to GitHub Release. Generate checksums.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/
git commit -m "ci: add CI/CD workflows for testing and release"
```

---

### Task 41: Landing page

**Files:**
- Create: `docs/website/index.html`
- Create: `docs/website/style.css`

- [ ] **Step 1: Create single-page landing site**

HTML + CSS only (no build step). OS detection via `navigator.userAgent`. Language detection via `navigator.language`. Download buttons for GUI/Script x ClaudeCode/OpenClaw. Links to GitHub Releases. macOS Gatekeeper bypass instructions (collapsible). Checksum display. Responsive design for mobile.

- [ ] **Step 2: Test locally**

Run: `python -m http.server -d docs/website 8080` and open in browser.

- [ ] **Step 3: Commit**

```bash
git add docs/website/
git commit -m "feat: add landing page with OS detection and download links"
```

---

## Phase 12: Final Verification

### Task 42: Full test suite and coverage

- [ ] **Step 1: Run full test suite**

Run: `pytest --cov=aiready --cov-report=term-missing --cov-report=html -v`
Expected: 80%+ overall, all tests pass

- [ ] **Step 2: Run shellcheck on all scripts**

Run: `shellcheck scripts/**/*.sh`
Expected: No errors

- [ ] **Step 3: Manual GUI smoke test**

Launch app, go through full flow for both tools. Verify all screens render correctly, i18n switches work, back button works.

- [ ] **Step 4: Fix any issues found**

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "test: final verification pass - all tests green, 80%+ coverage"
```

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1. Project Setup | 1-3 | pyproject.toml, data models, version util |
| 2. i18n | 4 | String system with ko/en JSON files |
| 3. Platform Layer | 5-9 | Platform ABC, process wrapper, Linux/macOS/Windows |
| 4. Missing Core Modules | 10-12 | Prerequisite checker, permission manager, validator |
| 5. Provider Registry | 13 | AI provider registry (6 providers) |
| 6. Core Engine | 14-17 | Downloader, PATH manager, logger, installer |
| 7. Tool Definitions | 18-20 | Tool ABC + Claude Code + OpenClaw |
| 8. Integration Test | 21 | Full flow integration test |
| 9. GUI | 22-29 | All 8 screens + app skeleton |
| 10. Scripts | 30-37 | All 8 native scripts + lint tests |
| 11. Build | 38-41 | PyInstaller, CI/CD, landing page |
| 12. Verification | 42 | Full test suite, coverage, smoke test |

**Total: 42 tasks across 12 phases**
