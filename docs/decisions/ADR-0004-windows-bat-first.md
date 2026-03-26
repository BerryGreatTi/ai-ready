# ADR-0004: BAT as Primary Windows Script Format

## Status

Accepted

## Context

The target audience includes beginners on Korean Windows 10/11 systems. Real-world experience has revealed critical issues:

1. **PowerShell encoding bug**: On Korean locale (cp949), PowerShell scripts exhibit a bug where comments and commands merge on a single line, producing garbled output or execution errors.
2. **PowerShell version**: Non-developers rarely update PowerShell. Many systems run 5.1 (shipped with Windows 10). Latest PowerShell 7+ features are unavailable.
3. **winget unavailable**: Some Windows versions (especially un-updated ones) do not have winget, or it is broken.
4. **Execution policy**: PowerShell scripts require `Set-ExecutionPolicy` changes, which beginners cannot troubleshoot.

## Decision

Use BAT (cmd.exe) as the **primary** script format for Windows. PowerShell (.ps1) is provided as a **secondary** option.

**BAT constraints:**
- `chcp 65001` at script start for UTF-8 output (fail-safe, continues if unsupported)
- Minimize non-ASCII characters in source code -- use variable-based message branching
- Use `curl` (built into Windows 10 1803+) for downloads
- No dependency on winget, chocolatey, or any package manager
- Direct .msi/.exe download for all prerequisites

**PS1 constraints (when provided):**
- `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` at start
- No inline Korean -- all strings loaded from hashtable
- PowerShell 5.1 syntax only: no `??`, `?.`, `&&`, no pipeline chain operators
- `Invoke-WebRequest` with `-UseBasicParsing` (avoids IE engine dependency)

## Consequences

- BAT syntax is more verbose and less readable than PowerShell for complex logic.
- Some operations (JSON parsing, registry modification) are harder in BAT than PS1.
- However, BAT is encoding-safe, runs without execution policy changes, and works on every Windows 10+ system without modification.
- The GUI (.exe) remains the primary Windows deliverable and bypasses all shell issues entirely.

## Alternatives Considered

- **PS1 only**: Cleaner syntax, better tooling, but Korean encoding issues make it unreliable for the target audience.
- **PS1 with UTF-8 BOM**: Partially mitigates encoding issues, but does not solve them on all PowerShell 5.1 versions.
- **Python CLI executable**: Would work but defeats the purpose of having a lightweight script option.

## Revision (2026-03-27)

This ADR remains in effect for **standalone scripts** in `scripts/windows/`. However, the **GUI installer** (`src/aiready/tools/claude_code.py`) now uses PowerShell as the primary installation method, with CMD as fallback. This aligns with Anthropic's official recommendation (`irm https://claude.ai/install.ps1 | iex` is the documented primary command).

The GUI's install order: PS1 -> CMD -> npm. The rationale: the GUI runs in a controlled subprocess environment where the Korean cp949 encoding issue does not affect the `irm ... | iex` one-liner (the issue is with script *files* containing Korean comments, not with inline commands).
