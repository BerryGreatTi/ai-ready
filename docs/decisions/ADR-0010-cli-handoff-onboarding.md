# ADR-0010: Hand Off Authentication and Onboarding to CLI

## Status

Accepted (supersedes GUIDED onboarding mode)

## Context

Previously, the GUI handled post-installation setup differently per tool:
- **Claude Code (GUIDED)**: GUI opened a browser for OAuth, displayed step-by-step instructions, and verified authentication via `claude --version`.
- **OpenClaw (AUTOMATIC)**: GUI presented a ProviderSelectScreen, ApiKeyScreen, then ran `openclaw onboard --install-daemon` in the background.

Both approaches had problems:
1. Claude Code's browser-based auth in the GUI was fragile and added complexity (OnboardingScreen with multiple states).
2. OpenClaw's GUI-based provider/API key flow duplicated functionality that the CLI already handles better (more providers, better validation, interactive prompts).
3. Both tools' CLIs provide richer first-run experiences than the GUI can replicate.

## Decision

After installation and PATH setup, the GUI launches the tool directly in a new terminal window instead of handling onboarding in the GUI:

- **Claude Code**: Opens terminal, runs `claude` (CLI handles its own first-run auth).
- **OpenClaw**: Opens terminal, runs `openclaw onboard` (CLI handles provider selection, API key, daemon setup).

Platform-specific terminal launch:
- **Windows**: `powershell -NoExit -Command "<absolute_path>"` (better UTF-8/ANSI support than CMD).
- **macOS**: AppleScript to open Terminal.app with the command.
- **Linux**: Tries gnome-terminal, konsole, xfce4-terminal, xterm in order.

The binary is resolved to an absolute path via `shutil.which()` before launching, because the new terminal inherits the system PATH (not the GUI process's modified `os.environ["PATH"]`).

## Consequences

- GUI flow simplified: `LanguageSelect -> ToolSelect -> Progress -> CompleteScreen` (same for both tools).
- Removed 5 GUI screens: ProviderSelectScreen, ApiKeyScreen, OnboardingScreen (guided), OnboardingScreen (automatic), AuthGuide.
- Removed `OnboardingMode.GUIDED`, `provider_selection`, `api_key_input` from `OnboardingConfig`.
- Removed `providers/registry.py` (only used by deleted screens).
- ~564 lines of dead code removed.
- Users get the full CLI onboarding experience with all options, not a limited GUI subset.

## Alternatives Considered

- **Keep GUIDED mode for Claude Code**: Rejected. The GUI auth flow was fragile and `claude doctor` (used for verification) hangs without TTY (see ADR-0009).
- **Keep AUTOMATIC mode for OpenClaw**: Rejected. The GUI's provider/API key screens were a subset of what `openclaw onboard` offers interactively.
- **Embed a terminal emulator in the GUI**: Overkill for a one-time setup tool.
