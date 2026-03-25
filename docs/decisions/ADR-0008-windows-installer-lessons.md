# ADR-0008: Windows Installer Lessons Learned (rc1-rc15)

## Status

Accepted

## Context

During v0.1.0 release candidate testing (rc1 through rc15) on VirtualBox Windows 10/11 VMs, a series of real-world issues were discovered that are not obvious from development on Linux/macOS. These lessons apply to all future Windows installer work.

## Lessons Learned

### 1. MSI installers require admin elevation (rc9-rc11)

`msiexec /i *.msi /qn` fails with **error 1603** without admin rights. The fix was `Start-Process -Verb RunAs` via PowerShell to trigger UAC elevation.

**Rule:** All MSI and EXE installers on Windows must use `Start-Process -Verb RunAs -Wait` with a non-elevated fallback.

### 2. PATH registry values contain unexpanded variables (rc6)

Reading PATH from `reg query HKCU\Environment` returns strings like `%USERPROFILE%\AppData\Local\...` which Python cannot resolve. Setting `os.environ["PATH"]` to these values breaks command resolution.

**Rule:** Never replace PATH from registry. Instead, append known install directories to the existing `os.environ["PATH"]`.

### 3. Installers produce large output that deadlocks pipes (rc12-rc14)

`subprocess.run(capture_output=True)` buffers stdout/stderr in memory. Large installers (Claude Code native installer) fill the 64KB pipe buffer and deadlock. The process hangs indefinitely.

**Rule:** Use `run_process_uncaptured()` for long-running installers. It redirects stdout/stderr to temp files instead of pipes, then reads the last 2000 characters after completion.

### 4. stdin must be DEVNULL for non-interactive installers (rc14)

Some installers prompt for input (e.g., "Press any key to continue"). Without `stdin=DEVNULL`, the process waits forever for keyboard input that never comes in a GUI context.

**Rule:** Always pass `stdin=subprocess.DEVNULL` to `subprocess.run()` for installer commands.

### 5. Version strings are not simple semver (rc15)

`git --version` returns `"git version 2.53.0.windows.2"`, not `"2.53.0"`. `uv --version` returns `"uv 0.11.1 (a6042f67f 2026-03-24 x86_64-pc-windows-msvc)"`. The naive parser (strip "v", split on non-digits) fails on these.

**Rule:** Use `re.search(r"(\d+(?:\.\d+)*)")` to extract the first numeric version pattern from any string format. Test parser with real-world version output.

### 6. verify_prerequisite receives full check_command string (rc4-rc5)

`Prerequisite.check_command` is `"git --version"` (full command), but `check_command()` expects just the command name `"git"`. Passing the full string caused lookup failures.

**Rule:** Always `prereq.check_command.split()[0]` to extract the command name before calling `check_command()`.

### 7. Default 120s timeout is too short for installers (rc13)

Claude Code native installer downloads ~100MB. On slow connections, 120 seconds is insufficient.

**Rule:** Use 600 seconds (10 minutes) for installer commands. Use default 120 seconds for quick checks (version, doctor, etc.).

### 8. Three-tier install fallback is essential (rc12)

A single installation method is fragile. Claude Code now uses:
1. CMD installer (`install.cmd`) - encoding-safe
2. PowerShell installer (`install.ps1`) - fallback
3. npm install (`@anthropic-ai/claude-code`) - final fallback (Node.js already installed)

**Rule:** Always provide at least 2 installation methods with automatic fallback.

### 9. Download URLs must be pinned and verified (rc8-rc9)

`nodejs.org/dist/latest-v20.x/node-v20.11.1-x64.msi` returned 404 because the specific version was removed. Dynamic URLs like `latest/` can break unexpectedly.

**Rule:** Pin to specific versions. Check URLs are valid before each release. Include version in the URL path, not just in the filename.

## Consequences

These rules are codified in the implementation. Future contributors must follow them for any Windows installer changes. The testing guide (`docs/specs/2026-03-24-testing-guide.md`) includes VirtualBox Windows VM testing as a required step.
