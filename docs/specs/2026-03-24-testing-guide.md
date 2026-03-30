# AIReady Testing Guide

## Pre-release Testing Procedure

### 1. Create a release candidate

```bash
git tag v0.1.0-rcN
git push origin v0.1.0-rcN
```

GitHub Actions builds Windows .exe and macOS .app automatically. Release appears at:
`https://github.com/BerryGreatTi/ai-ready/releases/tag/v0.1.0-rcN`

#### Local macOS build

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]" && pip install pyinstaller customtkinter
.dev/scripts/build-all.sh v0.1.0-rcN
```

The build script sets `AIREADY_VERSION` so the `.app` bundle's `Info.plist` contains the correct `CFBundleShortVersionString`. See [ADR-0011](../decisions/ADR-0011-pyinstaller-onedir-macos.md) for the onedir build mode.

### 2. Automated tests (CI)

Verified automatically on every push:

| Check | Platform | What it verifies |
|-------|----------|-----------------|
| pytest | Ubuntu/macOS/Windows | 313+ unit and integration tests |
| Coverage | Ubuntu | 80%+ (GUI excluded) |
| shellcheck | Ubuntu | Shell script warnings |
| bash -n | Ubuntu | Shell script syntax |

### 3. Manual test: macOS

#### GUI (.app)

1. Download `AIReady-ClaudeCode-Mac.zip` from release
2. Unzip
3. Run `xattr -cr ~/Downloads/AIReady-ClaudeCode-Mac.app` (Gatekeeper bypass)
4. Double-click to launch
5. Verify: language selection (Korean/English), tool selection, progress screen
6. Verify: Claude Code installs via native installer (not npm)
7. Verify: Browser opens for authentication
8. Verify: Complete screen shows `claude` command with copy button

#### Script (.sh)

```bash
curl -fsSL https://github.com/BerryGreatTi/ai-ready/releases/latest/download/AIReady-ClaudeCode.sh -o AIReady-ClaudeCode.sh
chmod +x AIReady-ClaudeCode.sh
./AIReady-ClaudeCode.sh
```

Verify:
- [ ] Language selection works
- [ ] Claude Code installs via `curl -fsSL https://claude.ai/install.sh | bash`
- [ ] PATH is permanently added to `~/.zshrc`
- [ ] `claude` command works in a NEW terminal
- [ ] Authentication guide displays correctly

### 4. Manual test: Windows

#### GUI (.exe)

1. Download `AIReady-ClaudeCode-Win.exe`
2. Double-click (may need "Run anyway" for SmartScreen)
3. Verify: language selection, tool selection
4. Verify: Git detected or installed (direct .exe, NOT winget)
5. Verify: Claude Code installs via `install.cmd` (NOT npm, NOT PowerShell)

#### Script (.bat)

1. Download `AIReady-ClaudeCode.bat`
2. Double-click or run from CMD
3. Verify on Korean Windows: no encoding errors (comments/commands not merged)
4. Verify: Git install uses direct download, not winget
5. Verify: Claude Code installs via `install.cmd`

#### Script (.ps1) - Secondary

1. Open PowerShell, run: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
2. Run `.\AIReady-ClaudeCode.ps1`
3. Verify: No PS7 syntax errors on PowerShell 5.1
4. Verify: Korean strings display correctly (from $Strings hashtable)

### 5. Manual test: Linux

#### Script (.sh)

```bash
curl -fsSL https://github.com/BerryGreatTi/ai-ready/releases/latest/download/AIReady-ClaudeCode.sh -o AIReady-ClaudeCode.sh
chmod +x AIReady-ClaudeCode.sh
./AIReady-ClaudeCode.sh
```

Verify on Ubuntu 20.04+:
- [ ] Claude Code installs via native installer
- [ ] PATH added to `~/.bashrc`
- [ ] Works in new terminal

Verify on Fedora (if available):
- [ ] Same as Ubuntu

### 6. Known issues and workarounds

| Issue | Workaround |
|-------|-----------|
| macOS Gatekeeper blocks .app | `xattr -cr` or use .sh script |
| Korean Windows encoding in PS1 | Use .bat script instead |
| winget unavailable on some Windows | Scripts use direct download, not winget |
| PATH not effective until new terminal | Success message instructs user to open new terminal |
| MSI install fails with error 1603 | Requires admin elevation (`Start-Process -Verb RunAs`) |
| PATH from registry has unexpanded %VAR% | Append known dirs, never replace from registry |
| Installer hangs (pipe buffer deadlock) | Use `run_process_uncaptured()` for long-running installers |
| Version parser fails on "git version X" | Use `re.search(r"(\d+(?:\.\d+)*)")` to extract numbers |
| Download URL returns 404 | Pin to specific version, verify before release |
| 120s timeout too short for installers | Use 600s for install commands |

### 7. Release checklist

Before creating a final release (non-rc):

- [ ] All CI checks pass (Ubuntu/macOS/Windows)
- [ ] macOS GUI tested with Gatekeeper bypass
- [ ] macOS script tested: PATH persists in new terminal
- [ ] Windows GUI tested on **clean VirtualBox Windows 10/11 VM**
- [ ] Windows GUI: Git, Node.js, UV all install with UAC prompt
- [ ] Windows GUI: Claude Code installs (3-tier fallback: CMD -> PS1 -> npm)
- [ ] Windows GUI: Already-installed tools are skipped (not reinstalled)
- [ ] Download URLs verified (no 404s)
- [ ] Release notes include Gatekeeper bypass instructions
- [ ] Log file (`%TEMP%\aiready\install.log`) contains DEBUG-level detail
