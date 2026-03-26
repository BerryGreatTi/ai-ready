# ADR-0006: Permanent PATH Setup in Shell Config

## Status

Accepted

## Context

During v0.1.0-rc1 testing on macOS, Claude Code installed successfully via the shell script, but the user could not run `claude` after opening a new terminal. The script only set PATH for the current session using `export PATH="$HOME/.local/bin:$PATH"`, which is lost when the terminal closes.

The target audience (beginners) does not know how to manually edit `~/.zshrc` or `~/.bashrc`. A "successful" installation that doesn't work in a new terminal is effectively a failure for this audience.

## Decision

All shell scripts (macOS and Linux) permanently add tool paths to the user's shell configuration file using the `add_to_path_permanently()` function:

1. **Detect shell**: Check `$ZSH_VERSION` or `$SHELL` basename for zsh vs bash.
2. **Set current session**: `export PATH="$dir:$PATH"` for immediate use.
3. **Set permanently**: Append `export PATH="$dir:$PATH"` to `~/.zshrc` (macOS default) or `~/.bashrc` (Linux default).
4. **Duplicate prevention**: Check if the path is already in the config file before appending.
5. **Comment marker**: Lines are prefixed with `# Added by AIReady installer` for identification.

The success message instructs the user to open a new terminal window, making the next step explicit.

## Consequences

- Users can run `claude` or `openclaw` immediately after opening a new terminal.
- Shell config files are modified (append-only, never destructive).
- If the user already has the path configured, no duplicate entries are added.
- The `# Added by AIReady installer` comment allows easy identification and removal.

## Alternatives Considered

- **Session-only PATH**: Rejected. Beginners cannot troubleshoot "command not found" after reopening terminal.
- **Modifying /etc/paths.d/**: Requires root/sudo. Rejected for being too invasive.
- **Instructing user to add PATH manually**: Rejected. Target audience cannot follow manual shell config instructions.

## Revision (2026-03-27)

The GUI installer now also calls `platform.add_to_path()` after `_verify_install` succeeds. Previously, only the shell scripts (`.sh`, `.bat`) performed permanent PATH setup. The GUI modified `os.environ["PATH"]` for the process only, which meant a new terminal opened after the GUI exited could not find the installed tool.

The fix: after `check_command()` locates the binary, its parent directory is passed to `platform.add_to_path()`, which writes to `~/.zshrc`/`~/.bashrc` (Linux/macOS) or `HKCU\Environment\Path` registry (Windows). This ensures the tool is findable in any new terminal session.
