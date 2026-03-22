# ADR-0002: Python + CustomTkinter + PyInstaller Tech Stack

## Status

Accepted

## Context

AIReady needs to produce GUI executables for Windows and macOS that beginners can run without any prerequisites. The GUI must handle system automation tasks: subprocess execution, PATH manipulation, registry editing, file downloads, and permission elevation.

Options evaluated:
1. Electron - Web-based GUI, ~150MB output
2. Tauri - Rust backend + web frontend, ~10MB output
3. Python + CustomTkinter + PyInstaller - ~50MB output
4. Native per platform (C#/WinForms + Swift) - ~5MB output, two codebases

## Decision

Use Python 3.12+ with CustomTkinter for the GUI framework and PyInstaller for packaging into standalone executables.

**Rationale:**
- The core problem is **system automation** (subprocess, PATH, registry, permissions), not complex UI. Python excels at this with `subprocess`, `os`, `shutil`, `winreg`.
- PyInstaller produces zero-dependency single-file executables -- users double-click and it runs.
- Single codebase builds for both Windows (.exe) and macOS (.app).
- CustomTkinter provides modern dark/light theme UI sufficient for an installer (buttons, progress bars, text fields).
- ~50MB output is well within the 500MB limit.

## Consequences

- Python runtime is bundled in every executable (~40MB baseline).
- GUI will not look native -- CustomTkinter has its own visual style, not Win32/Cocoa native widgets.
- Build requires PyInstaller on each target OS (no cross-compilation).
- Team must know Python; no Rust (Tauri) or C#/Swift (native) required.

## Alternatives Considered

- **Electron**: Mature, best UI flexibility, but ~150MB, requires IPC layer for system operations, over-engineered for this use case.
- **Tauri**: Smallest output, but requires Rust toolchain, WebView2 dependency on Windows may be missing on some systems, higher development complexity.
- **Native per platform**: Smallest output, best native feel, but doubles the codebase and maintenance. Two completely different languages and frameworks.
