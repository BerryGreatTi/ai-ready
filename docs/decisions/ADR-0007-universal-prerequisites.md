# ADR-0007: Universal Prerequisites (Git, Node.js, UV) for All Tools

## Status

Accepted

## Context

Previously, prerequisites were tool-specific:
- Claude Code on Windows: Git only
- Claude Code on macOS/Linux: none
- OpenClaw: Node.js only

However, users who install AI coding tools will inevitably need Git (version control), Node.js (many AI tools depend on it), and UV (fast Python package manager, increasingly required by AI tooling). Installing these upfront avoids the common beginner experience of hitting "command not found" errors later.

## Decision

Install Git, Node.js, and UV as universal prerequisites for **all tools on all platforms**, before the main tool installation step.

**Prerequisites (in order):**
1. **Git** >= 2.0 - Version control, required by Claude Code on Windows, useful everywhere
2. **Node.js** >= 22.16 - JavaScript runtime, required by OpenClaw, useful for many AI tools
3. **UV** >= 0.1.0 - Fast Python package installer by Astral, increasingly used in AI tooling

**Installation flow:**
```
Check/Install Git -> Check/Install Node.js -> Check/Install UV -> Install Target Tool -> Onboarding
```

Each prerequisite is checked first (version + PATH). If already installed with a sufficient version, it is skipped.

**UV installation methods:**
- macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | bash`
- Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Consequences

- Longer initial setup time if all 3 need to be installed
- Beginners get a complete development foundation in one run
- No "command not found" surprises when following tutorials later
- UV is relatively new; the install URL may change (mitigated by version check + skip if installed)

## Alternatives Considered

- **Tool-specific only**: Minimal install, but beginners hit missing tool errors later.
- **Optional prerequisites**: Ask user which to install. Rejected because target audience (beginners) cannot make informed choices about which tools they need.
