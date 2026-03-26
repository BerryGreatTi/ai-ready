# Onboarding Modes

How AIReady handles post-installation setup for each tool.

## CLI Handoff (current)

After installation and PATH setup, the GUI opens a new terminal and launches the tool's CLI directly. The CLI handles its own first-run experience (authentication, provider selection, API key input, daemon setup).

- **Claude Code**: Terminal runs `claude`, which starts interactive auth on first launch.
- **OpenClaw**: Terminal runs `openclaw onboard`, which handles provider selection, API key, and daemon setup interactively.

The GUI resolves the binary to an absolute path (via `shutil.which`) before launching, because the new terminal may not have the updated PATH yet.

See [ADR-0010](../decisions/ADR-0010-cli-handoff-onboarding.md) for the decision rationale.

## Historical modes (removed)

- **GUIDED**: Used for Claude Code browser-based OAuth. Removed in v0.1.0-rc21 because the CLI handles auth better.
- **AUTOMATIC**: Used for OpenClaw GUI-based provider/API key input. Removed in v0.1.0-rc22 because `openclaw onboard` provides a richer interactive experience.
