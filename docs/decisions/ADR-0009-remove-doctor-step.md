# ADR-0009: Remove `claude doctor` Step from Installation Flow

## Status

Accepted

## Context

During v0.1.0-rc19 performance debugging, the `claude doctor` step was found to hang for 120 seconds when run from the GUI subprocess. `claude doctor` uses Ink (a React-based terminal UI framework) which requires raw mode TTY access. The GUI runs subprocesses with `stdin=DEVNULL` and piped stdout/stderr, so no TTY is available.

Measured impact: `claude doctor` consumed 120,081ms out of a total 120,296ms installation time (99.8%). The step was marked `required=False`, but the installer engine executes steps sequentially, so it blocked all subsequent steps until the 120-second timeout expired.

## Decision

Remove the `run_doctor` step entirely from `ClaudeCodeTool.get_steps()`. Do not attempt to run `claude doctor` from the GUI process.

Rationale:
- `claude doctor` is an interactive TUI command, not designed for non-TTY execution.
- The information it provides (health checks) is not needed during installation -- it is a post-install diagnostic tool.
- A short timeout would cause the step to fail rather than hang, but a failed non-required step adds confusion for beginners with no benefit.

## Consequences

- Installation flow reduced from 8 steps to 5 (after also removing auth steps in ADR-0010).
- Non-download steps complete in ~200ms instead of ~120s.
- Users who want to run `claude doctor` can do so manually in a terminal after installation.

## Alternatives Considered

- **Short timeout (5s)**: Would fail immediately with an error, confusing beginners for no benefit.
- **Allocate a PTY**: Overly complex for a non-essential diagnostic step.
- **Run with `--json` flag**: `claude doctor` does not support a non-interactive output mode.
