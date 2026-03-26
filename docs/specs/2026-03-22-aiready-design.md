# AIReady - Architecture & Design Specification

## 1. Overview

AIReady is a cross-platform installer helper that automates the installation and onboarding of AI coding tools (Claude Code, OpenClaw) for beginners. It targets non-developer users on Korean/English Windows, macOS, and Linux systems.

### Release Deliverables

| Platform | Claude Code | OpenClaw |
|----------|-------------|----------|
| Windows GUI (.exe) | Yes | Yes |
| macOS GUI (.app) | Yes | Yes |

**Total: 4 release artifacts** (GUI only; scripts remain in source but excluded from releases)

Scripts (.bat, .ps1, .sh) are available in the `scripts/` directory of the repository but are not included in GitHub Releases. The GUI is the primary delivery method for all platforms.

File naming convention: `AIReady-{Tool}-{Platform}.{ext}`

Platform abbreviations: `Win` (Windows), `Mac` (macOS), `Linux` (Linux)

Examples:
- `AIReady-ClaudeCode-Win.exe`
- `AIReady-OpenClaw-Mac.app`
- `AIReady-ClaudeCode-Linux.sh`

### Key Decisions

- **Tech stack**: Python 3.12+ / CustomTkinter / PyInstaller
- **Architecture**: Layered Core (Approach A) - shared Python core for GUI, independent native scripts
- **i18n**: Korean + English, language selection at startup
- **Onboarding**: Fully automated (C) where possible, guided (B) where not
- **Script interaction**: Minimal interactive - only essential prompts (API keys)
- **Windows primary script**: BAT (cmd) to avoid Korean encoding issues in PowerShell
- **Distribution**: GitHub Releases + landing page (GitHub Pages)

## 2. Project Structure

```
install-ai/
  pyproject.toml

  src/
    aiready/
      __init__.py
      main.py                   # GUI entry point

      core/
        __init__.py
        installer.py            # Installation orchestration (step engine)
        prereqs.py              # Prerequisite detection and installation
        downloader.py           # Download + integrity + retry
        path_manager.py         # PATH check/modify
        permissions.py          # Permission check/elevation (UAC, sudo)
        process.py              # subprocess wrapper (output capture, timeout)
        validator.py            # Installation verification (--version, doctor)

      i18n/
        __init__.py
        strings.py              # String loading logic
        ko.json                 # Korean
        en.json                 # English

      platforms/
        __init__.py
        base.py                 # Abstract base class (Platform)
        windows.py              # Windows (registry, UAC, Git detection)
        macos.py                # macOS (Gatekeeper, brew, zsh/bash)
        linux.py                # Linux (apt/dnf/pacman, distro detection)
        detect.py               # OS auto-detect -> appropriate Platform

      tools/
        __init__.py
        base.py                 # Abstract base class (Tool)
        claude_code.py          # Claude Code: install, auth guide, verify
        openclaw.py             # OpenClaw: install, API key, onboard, verify

      providers/
        __init__.py
        registry.py             # Provider list (top 3 + rest + Ollama)

      gui/
        __init__.py
        app.py                  # Main app window
        theme.py                # Dark/light theme
        screens/
          __init__.py
          language_select.py    # Language selection
          tool_select.py        # Tool selection
          progress.py           # Installation progress
          api_key.py            # API key input
          provider_select.py    # AI provider selection
          onboarding.py         # Onboarding progress/guide
          complete.py           # Completion screen

  scripts/
    windows/
      AIReady-ClaudeCode.bat
      AIReady-ClaudeCode.ps1
      AIReady-OpenClaw.bat
      AIReady-OpenClaw.ps1
    macos/
      AIReady-ClaudeCode.sh
      AIReady-OpenClaw.sh
    linux/
      AIReady-ClaudeCode.sh
      AIReady-OpenClaw.sh

  build/
    pyinstaller/
      windows-claude.spec
      windows-openclaw.spec
      macos-claude.spec
      macos-openclaw.spec
    entry_claude_code.py        # PyInstaller entry for Claude Code
    entry_openclaw.py           # PyInstaller entry for OpenClaw

  tests/
    unit/
      core/
      platforms/
      tools/
      i18n/
      providers/
    integration/
    scripts/

  docs/
  .dev/
  release/                      # gitignored
```

### Design Principles

- **core/ depends on Platform interface only** - no `if windows` branches in core
- **tools/ depends on Platform interface only** - defines steps, delegates execution
- **gui/ calls core only** - UI logic and business logic fully separated
- **scripts/ are fully independent** - no dependency on Python package

## 3. Core Module Design

### installer.py - Orchestration Engine

```python
@dataclass(frozen=True)
class Step:
    id: str
    name_key: str           # i18n key
    action: Callable
    required: bool          # abort on failure?

@dataclass(frozen=True)
class StepResult:
    status: StepStatus      # RUNNING, SUCCESS, FAILED, SKIPPED
    message: Optional[str]
    detail: Optional[str]

class Installer:
    def __init__(self, platform: Platform, tool: Tool, i18n: I18n):
        self.platform = platform
        self.tool = tool
        self.i18n = i18n

    def run(self, on_progress: Callable[[int, Step, StepResult], None]):
        steps = self.tool.get_steps(self.platform)
        for i, step in enumerate(steps):
            on_progress(i, step, StepResult(StepStatus.RUNNING))
            result = step.action()
            on_progress(i, step, result)
            if result.status == StepStatus.FAILED and step.required:
                return InstallResult(success=False, failed_step=step, error=result)
        return InstallResult(success=True)
```

- GUI uses `on_progress` callback to update progress bar
- All objects are **immutable** (frozen dataclass)
- Step results are new `StepResult` objects (no mutation)

### prereqs.py - Prerequisite Detection

```python
@dataclass(frozen=True)
class Prerequisite:
    name: str               # "nodejs", "git"
    min_version: str        # "22.16", "2.0"
    check_command: str      # "node --version", "git --version"

@dataclass(frozen=True)
class PrereqCheckResult:
    prereq: Prerequisite
    installed: bool
    current_version: Optional[str]
    needs_upgrade: bool
```

### downloader.py - Download Management

- Downloads to temp directory, moves after verification
- Retry: 3 attempts with exponential backoff
- Checksum validation when available
- System proxy auto-detection
- Progress callback for GUI progress bar

### path_manager.py - PATH Management

Delegates to Platform:
- Windows: user-level PATH via registry (HKCU\Environment\Path)
- macOS/Linux: append to ~/.zshrc or ~/.bashrc
- Duplicate prevention
- Session refresh after modification

### i18n/ - Internationalization

JSON key-value files (`ko.json`, `en.json`). Access via `I18n.get("key")`. Missing keys fall back to English.

**Interpolation:** Use `{placeholder}` syntax. Example: `"error.version_mismatch": "Node.js {required}+ required. Current: {current}"`

**Translation rules:**
- Technical terms always in English: API key, CLI, PATH, Node.js, Git, OAuth, URL
- Product names always in English: Claude Code, OpenClaw, Anthropic, OpenAI, Gemini, Ollama
- UI actions translated: buttons, labels, instructions, error descriptions
- Error messages are i18n keys, not hardcoded strings. The error table in section 9 shows English equivalents for readability.

### providers/registry.py - AI Providers

```python
@dataclass(frozen=True)
class AIProvider:
    id: str
    name_key: str           # i18n key
    env_var: str            # "ANTHROPIC_API_KEY" etc.
    api_key_url: str        # Key issuance page URL
    priority: int           # Sort order (lower = higher)
    is_local: bool          # Ollama etc.
```

Priority: Anthropic(1), OpenAI(2), Gemini(3), others(10+), Ollama(99).

**Initial provider list (v0.1.0):**
- Priority 1: Anthropic (Claude) - `ANTHROPIC_API_KEY`
- Priority 2: OpenAI (GPT) - `OPENAI_API_KEY`
- Priority 3: Google Gemini - `GOOGLE_API_KEY`
- Priority 10: Mistral - `MISTRAL_API_KEY`
- Priority 11: Cohere - `CO_API_KEY`
- Priority 99: Ollama (local) - no key needed, `is_local=True`

Provider list is **hardcoded** in registry.py. Adding a new provider requires a code change and new release. This is intentional: each provider needs tested validation logic, so auto-fetching would risk untested providers.

The provider list should be reviewed and updated with each major release based on OpenClaw's supported providers.

## 4. Platform Abstraction

### Platform Interface (base.py)

```python
class Platform(ABC):
    @abstractmethod
    def get_os_info(self) -> OSInfo: ...
    def check_command(self, cmd: str) -> Optional[CommandInfo]: ...
    def install_prerequisite(self, prereq: Prerequisite) -> InstallResult: ...
    def verify_prerequisite(self, prereq: Prerequisite) -> PrereqCheckResult: ...
    def add_to_path(self, path: Path) -> PathResult: ...
    def request_elevation(self, reason_key: str) -> bool: ...
    def run_command(self, cmd: list[str], elevated: bool = False) -> CommandResult: ...
    def get_temp_dir(self) -> Path: ...
    def open_browser(self, url: str) -> bool: ...
    def get_shell_type(self) -> ShellType: ...
```

`verify_prerequisite` is called after `install_prerequisite` to confirm the tool is in PATH and meets version requirements. If verification fails after installation, the installer retries once before reporting failure.

### WindowsPlatform

- `check_command`: `where.exe` + known install paths fallback
- `install_prerequisite`: Direct .msi/.exe download (no winget)
- `add_to_path`: `winreg` HKCU user-level + `SendMessageTimeout` broadcast
- `request_elevation`: `ctypes.windll.shell32.ShellExecuteW` for UAC

### MacOSPlatform

- `install_prerequisite`: brew (if available) or direct .pkg download
- `add_to_path`: Append to ~/.zshrc (default) or ~/.bashrc
- `request_elevation`: `osascript` GUI sudo dialog

### LinuxPlatform

- `_detect_distro`: Parse /etc/os-release
- `_detect_package_manager`: apt-get, dnf, pacman, apk
- `install_prerequisite`: NodeSource repo + distro package manager

### detect.py

```python
def detect_platform() -> Platform:
    system = platform.system()
    if system == "Windows": return WindowsPlatform()
    elif system == "Darwin": return MacOSPlatform()
    elif system == "Linux": return LinuxPlatform()
    raise UnsupportedPlatformError(system)
```

## 5. Tool Abstraction

### Tool Interface (base.py)

```python
class Tool(ABC):
    def get_name(self) -> str: ...
    def get_prerequisites(self) -> list[Prerequisite]: ...
    def get_steps(self, platform: Platform) -> list[Step]: ...
    def get_install_command(self, platform: Platform) -> list[str]: ...
    def get_verify_commands(self) -> list[VerifyCommand]: ...
    def get_onboarding_config(self) -> OnboardingConfig: ...
```

### ClaudeCodeTool

**Prerequisites:** Git (Windows only). None for macOS/Linux.

**Steps:**
1. check_system - OS info
2. install_prereqs - Git, Node.js, UV (all platforms)
3. verify_prereqs - verify all prerequisites in PATH with version check
4. install_tool - native installer (platform-specific, see below)
5. verify_install - `claude --version` + persist binary dir to system PATH

**Platform-specific installation (3-tier fallback on Windows):**
- macOS/Linux: `curl -fsSL https://claude.ai/install.sh | bash` (via `run_process_live`)
- Windows Method 1: PowerShell installer (`install.ps1`) - official primary
- Windows Method 2: CMD installer (`install.cmd`) - fallback
- Windows Method 3: npm install (`@anthropic-ai/claude-code`) - final fallback (Node.js already installed)

**Critical implementation notes (from rc1-rc15 testing):**
- All installer commands use `run_process_live()` to avoid pipe buffer deadlocks with large output. See [ADR-0008](../decisions/ADR-0008-windows-installer-lessons.md).
- Timeout is 600 seconds (10 minutes) for installer commands.
- `stdin=DEVNULL` prevents installers from waiting for user input.
- After each prerequisite install, PATH is refreshed by appending known dirs (never replacing from registry).
- After verify_install, the binary's directory is persisted to system PATH via `platform.add_to_path()`. See [ADR-0006](../decisions/ADR-0006-permanent-path-setup.md).

**Onboarding:** CLI handoff. After install, the GUI launches `claude` in a new terminal. The CLI handles its own first-run authentication. See [ADR-0010](../decisions/ADR-0010-cli-handoff-onboarding.md).

### OpenClawTool

**Prerequisites:** Git >= 2.0, Node.js >= 22.16, UV >= 0.1.0 (all platforms, same as ClaudeCodeTool).

**Steps:**
1. check_system - OS info
2. install_prereqs - Git, Node.js, UV (all platforms)
3. verify_prereqs - verify all prerequisites in PATH with version check
4. install_tool - official installer script (primary), npm fallback
5. verify_install - `openclaw --version` + persist binary dir to system PATH

**Installation fallback strategy:**
- Step 4 first tries official installer script (`curl ... | bash` or PowerShell equivalent)
- If that fails, falls back to `npm install -g openclaw@latest` (Node.js is already installed at this point)
- If both fail: show error with Retry/View Log/Exit buttons

**Onboarding:** CLI handoff. After install, the GUI launches `openclaw onboard` in a new terminal. The CLI handles provider selection, API key input, and daemon setup interactively. See [ADR-0010](../decisions/ADR-0010-cli-handoff-onboarding.md).

## 6. GUI Design

### Screen Flow

```
[Language Select] -> [Tool Select] -> [Progress] -> [Complete]
```

Same flow for both tools. After installation, the Complete screen auto-launches the tool in a terminal for CLI-based onboarding.

### Screens

**Language Select**: Centered hero layout with brand title. Two accent buttons (Korean / English). Selection changes all UI text immediately.

**Tool Select**: Card-style selection with border highlight on click. One tool per card with name, description, and requirement note. Ghost-style back button, accent next button.

**Progress**: Steps displayed in a rounded card container with status indicators (check=done, dot=running, circle=waiting). Slim progress bar. Muted status text. Error state shows error message + Retry/View Log/Exit buttons.

**Complete**: Centered success layout with checkmark. Command displayed in styled code box with copy button. Auto-launches tool in new terminal 500ms after screen appears. "Launch {tool}" primary button for manual re-launch. "Exit" ghost button.

### GUI Constants

- **Window size**: 480x640 fixed (no resize)
- **Theme**: Follow system (dark/light auto)
- **Font**: System default (Korean rendering safety)
- **Back button**: Disabled during Progress, enabled otherwise

## 7. Script Architecture

### Design Principles

- Fully independent - assume no runtime pre-installed
- Self-contained - single file handles everything
- Minimal interactive - only essential prompts

### Permission Model

**Operations that require elevation:**
- Installing system packages (Node.js .msi, Git .exe on Windows; brew/pkg on macOS; apt/dnf on Linux)
- Writing to system directories (/usr/local, C:\Program Files)

**Operations that do NOT require elevation:**
- Checking versions, detecting installed tools
- Downloading files to temp directory
- Modifying user-level PATH (Windows: HKCU registry; macOS/Linux: ~/.zshrc)
- npm global install (uses user prefix when possible)
- Running tool-specific installers that handle their own elevation

**Elevation flow:**
1. Detect if elevation is needed for the specific operation
2. Explain to user WHY elevation is needed (in selected language)
3. Request elevation (UAC dialog / sudo prompt)
4. If denied: attempt alternative (user-level install) or show manual instructions
5. Never run the entire installer as admin/root - only elevate per-operation

### Windows BAT (Primary)

- `chcp 65001` for UTF-8 (fail-safe, continues on error)
- Minimize Korean in source code - use variable-based message branching
- `curl` (built into Windows 10 1803+) for downloads
- No winget/chocolatey dependency
- Direct .msi download for Node.js, .exe for Git
- PATH refresh via registry query within current session

### Windows PS1 (Secondary)

- `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`
- No inline Korean - all strings from hashtable lookup
- PowerShell 5.1 syntax only (no `??`, `?.`, `&&`)
- `Invoke-WebRequest` with `-UseBasicParsing` (no IE dependency)

### macOS/Linux SH

- `#!/usr/bin/env bash` + `set -euo pipefail`
- Separate files for macOS and Linux (different package management)
- macOS: brew preferred, .pkg fallback
- Linux: distro auto-detect via `/etc/os-release`, apt/dnf/pacman/apk
- Color output with ANSI codes
- API key input with `read -s` (silent)
- **PATH permanently written to shell config** (`~/.zshrc` or `~/.bashrc`) via `add_to_path_permanently()` helper. Duplicate prevention via grep check. Comment marker: `# Added by AIReady installer`. See [ADR-0006](../decisions/ADR-0006-permanent-path-setup.md).

### Script File Matrix

| File | Flow |
|------|------|
| windows/AIReady-ClaudeCode.bat | Git check/install -> Claude Code install -> Auth guide |
| windows/AIReady-ClaudeCode.ps1 | Same (PS1 version) |
| windows/AIReady-OpenClaw.bat | Node.js check/install -> OpenClaw install -> API key -> Onboard |
| windows/AIReady-OpenClaw.ps1 | Same (PS1 version) |
| macos/AIReady-ClaudeCode.sh | System check -> Claude Code install -> Auth guide |
| macos/AIReady-OpenClaw.sh | Node.js check/install -> OpenClaw install -> API key -> Onboard |
| linux/AIReady-ClaudeCode.sh | System check -> Claude Code install -> Auth guide |
| linux/AIReady-OpenClaw.sh | Distro detect -> Node.js install -> OpenClaw install -> API key -> Onboard |

## 8. Build Pipeline

### Dependencies (pyproject.toml)

```toml
[project]
name = "aiready"
version = "0.1.0"
requires-python = ">=3.12"
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
```

### Build Process

- PyInstaller builds separate executables per tool via dedicated entry points
- `entry_claude_code.py` -> `AIReady-ClaudeCode-Win.exe` / `AIReady-ClaudeCode-Mac.app`
- `entry_openclaw.py` -> `AIReady-OpenClaw-Win.exe` / `AIReady-OpenClaw-Mac.app`
- Tool Select screen is skipped in dedicated builds (tool pre-selected)
- Scripts require no build step (copied as-is)

### Release Structure

```
release/<version>/
  gui/
    AIReady-ClaudeCode-Win.exe
    AIReady-OpenClaw-Win.exe
    AIReady-ClaudeCode-Mac.app.zip
    AIReady-OpenClaw-Mac.app.zip
  scripts/
    windows/ macos/ linux/
  CHECKSUMS.txt
```

### CI/CD (GitHub Actions)

- Windows runner: .exe builds
- macOS runner: .app builds
- Linux runner: script testing only (shellcheck, bats)
- Tag push triggers automatic release with checksum file
- Landing page auto-updates with latest version links
- PyInstaller flags: `--onefile` for single-file distribution
- Dependency caching: pip cache + PyInstaller cache between runs

### macOS Code Signing

Initial releases will be **unsigned**. This means macOS Gatekeeper will block the app.

**Mitigation for beginners:**
- Landing page includes step-by-step Gatekeeper bypass instructions with screenshots:
  1. "Right-click the app -> Open" (first attempt shows warning)
  2. System Preferences -> Privacy & Security -> "Open Anyway"
- The .sh script alternative is provided for users who cannot bypass Gatekeeper
- Future: Add Apple Developer account for code signing + notarization when the project matures

### Landing Page

Single-page site at `docs/website/index.html` hosted on GitHub Pages.

**OS detection:** `navigator.userAgent` parsing with manual fallback dropdown if detection fails.

**Language detection:** `navigator.language` to auto-suggest Korean or English, with manual toggle.

**Layout:**
- Primary: Large download button for detected OS + detected tool (if came from specific link)
- Secondary: Tab switching between GUI/Script and Claude Code/OpenClaw
- Checksum display with copy-to-clipboard for manual verification
- macOS Gatekeeper bypass instructions (collapsible section)
- Links to GitHub Releases for all versions

## 9. Error Handling

### Error Types and Recovery

| Error Type | Recovery Strategy | User Message |
|-----------|------------------|-------------|
| Network failure | 3 retries (exponential backoff) -> manual URL | "Download failed. Check network." |
| Permission denied | UAC/sudo request -> guide on failure | "Admin permission needed." |
| Disk full | Pre-check blocks start | "1GB+ free space required." |
| PATH not updated | Session refresh -> restart notice | "Please reopen terminal." |
| Version mismatch | Upgrade attempt -> manual guide | "Node.js 24+ required. Current: 18.0" |
| Invalid API key | Re-prompt | "API key invalid. Please check." |
| Verification failed | 1 reinstall attempt -> log + guide | "Installation issue. Check log." |

### Logging

- All command executions and outputs logged
- Log format: plain text with structured prefix `[TIMESTAMP] [LEVEL] [STEP] message`
- Log location: `%TEMP%/aiready/install.log` (Windows), `/tmp/aiready/install.log` (macOS/Linux)
- Max log size: 10MB (single run unlikely to exceed; previous log overwritten on new run)
- Sensitive data masked: API keys (`sk-ant-***`, `sk-***`), tokens, passwords
- **Privacy: Logs are stored locally only. No data is sent externally.**
- GUI: "View Log" button on error
- Scripts: log file path printed on error

## 10. Testing Strategy

### Python Tests

| Area | Coverage Target | Approach |
|------|----------------|----------|
| core/ | 90%+ | Unit tests with mocked Platform |
| platforms/ | 70%+ | Unit tests with mocking (limited by OS) |
| tools/ | 80%+ | Unit tests for step generation, config |
| i18n/ | 100% | Key matching between all language files |
| providers/ | 100% | Registry sorting, field validation |
| gui/ | Manual | UI automation cost too high for value |

### Script Tests

- **shellcheck**: Static analysis for all .sh scripts
- **bats-core**: Bash function unit tests
- **BAT/PS1**: Syntax verification + Windows CI execution tests

### i18n Verification

Automated test ensures all keys in `en.json` exist in `ko.json` and vice versa. New strings without both translations fail CI.

## 11. Critical: Korean Windows Constraints

These constraints apply to ALL Windows deliverables:

1. **Encoding**: Korean Windows (cp949) causes PowerShell script comments and commands to merge. BAT is primary script format. PS1 is secondary.
2. **PowerShell version**: Target 5.1 (ships with Windows 10). No PS 7+ syntax.
3. **winget unavailable**: Some Windows versions lack winget entirely. Direct download only.
4. **Outdated systems**: Assume no Windows Update applied. Test on vanilla Windows 10 1809.
5. **GUI bypasses all shell issues**: The .exe is the most important Windows deliverable.
