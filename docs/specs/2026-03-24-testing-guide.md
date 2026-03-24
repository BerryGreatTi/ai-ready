# AIReady Testing Guide

## Pre-release Testing Procedure

### 1. Create a release candidate

```bash
git tag v0.1.0-rcN
git push origin v0.1.0-rcN
```

GitHub Actions builds Windows .exe and macOS .app automatically. Release appears at:
`https://github.com/BerryGreatTi/ai-ready/releases/tag/v0.1.0-rcN`

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

### 7. Release checklist

Before creating a final release (non-rc):

- [ ] All CI checks pass (Ubuntu/macOS/Windows)
- [ ] macOS GUI tested with Gatekeeper bypass
- [ ] macOS script tested: PATH persists in new terminal
- [ ] Windows GUI tested on clean Windows 10
- [ ] Windows BAT tested on Korean Windows
- [ ] Linux script tested on Ubuntu
- [ ] Landing page download links work
- [ ] Release notes include Gatekeeper bypass instructions
