# Native Installer

The officially recommended installation method for Claude Code (as of 2026). Unlike the deprecated npm method, the native installer:

- Requires **zero dependencies** -- no Node.js, no npm
- Auto-updates in the background
- Is distributed as platform-specific one-liners:
  - macOS/Linux: `curl -fsSL https://claude.ai/install.sh | bash`
  - Windows PowerShell: `irm https://claude.ai/install.ps1 | iex`
  - Windows CMD: `curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd`

AIReady uses the CMD variant on Windows to avoid Korean encoding issues with PowerShell.

## Note

OpenClaw also provides an installer script, but it installs Node.js as a prerequisite (not zero-dependency). OpenClaw's installer script is distinct from Claude Code's "native installer" concept.
