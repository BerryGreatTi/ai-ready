# Target User

A beginner (non-developer) who wants to use AI coding tools but lacks technical setup experience.

## Characteristics

- No development tools installed (no Node.js, no Git, no package managers)
- May be on outdated OS versions (no Windows Update applied)
- On Korean Windows: PowerShell encoding issues, potentially missing winget
- Cannot troubleshoot PATH errors, permission issues, or encoding problems
- Expects double-click-to-run experience

## Implications for design

- Every prerequisite must be detected and installed automatically
- Error messages must be user-friendly, in the selected language (Korean or English)
- GUI version is the primary delivery for Windows and macOS
- Script version must handle all edge cases without user intervention
- Never assume any tool or runtime is pre-installed
