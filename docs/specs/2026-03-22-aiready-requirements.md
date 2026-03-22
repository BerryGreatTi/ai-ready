# AIReady - Requirements Specification

## Overview

AIReady is a cross-platform installer helper that automates the installation and onboarding of AI coding tools (Claude Code, OpenClaw) for beginners. The target audience is non-developers on Korean or English Windows, macOS, and Linux systems.

## Deliverables Matrix

| Platform | Claude Code | OpenClaw |
|----------|-------------|----------|
| Windows GUI (.exe) | Yes | Yes |
| Windows Script (.bat + .ps1) | Yes | Yes |
| macOS GUI (.app) | Yes | Yes |
| macOS Script (.sh) | Yes | Yes |
| Linux Script (.sh) | Yes | Yes |

**Total: 10 deliverables**

File naming: `AIReady-{Tool}-{Platform}.{ext}`

## Technology Stack

- **GUI**: Python 3.12+ with CustomTkinter
- **Packaging**: PyInstaller (single-file executables)
- **Scripts**: Bash (macOS/Linux), BAT primary + PS1 secondary (Windows)
- **Distribution**: GitHub Releases + landing page (GitHub Pages)
- **Release path**: `release/<version>/`

## Functional Requirements

### FR-1: Prerequisite Detection and Installation

The installer must detect and automatically install all prerequisites.

**Claude Code prerequisites:**
- Windows: Git for Windows
- macOS/Linux: None (native installer has zero dependencies)

**OpenClaw prerequisites:**
- All platforms: Node.js 22.16+ (24 recommended)

Detection must check:
- Whether the tool exists in PATH
- Version compatibility (not just presence)
- Whether PATH is correctly configured after installation

### FR-2: Target Tool Installation

**Claude Code:**
- Use native installer (recommended method)
  - macOS/Linux: `curl -fsSL https://claude.ai/install.sh | bash`
  - Windows: `irm https://claude.ai/install.ps1 | iex` or CMD equivalent
- Verify with `claude --version` and `claude doctor`

**OpenClaw:**
- Use installer script (recommended method)
  - macOS/Linux: `curl -fsSL https://openclaw.ai/install.sh | bash`
  - Windows: `iwr -useb https://openclaw.ai/install.ps1 | iex`
- Fallback to npm: `npm install -g openclaw@latest`
- Verify with `openclaw --version` and `openclaw doctor`

### FR-3: Onboarding Automation

**Scope: Fully automated (C) where possible, guided (B) where not.**

**Claude Code onboarding:**
- Automatic: Launch `claude` command
- Guided (B): Browser-based authentication requires user interaction. Open browser automatically and display step-by-step instructions in the installer UI.
- Account requirement notice: Inform user that Pro/Max/Teams/Enterprise plan is needed.

**OpenClaw onboarding:**
- Automatic: Run `openclaw onboard --install-daemon`
- Automatic: API key configuration via GUI input
  - AI provider selection with all supported providers
  - Top 3 (Anthropic, OpenAI, Google Gemini) displayed at top of list
  - Remaining providers + Ollama (local) below
- Guided (B): Any steps that require external service authentication

### FR-4: Internationalization (i18n)

- Language selection screen at startup: Korean / English
- All UI text, error messages, and instructions localized
- Language selection persisted for script versions via command-line flag

### FR-5: Error Handling

- Every operation must have clear, user-friendly error messages in the selected language
- Network failures: Retry with exponential backoff, then display instructions for manual download
- Permission errors: Attempt elevation (UAC on Windows, sudo on macOS/Linux) with clear explanation
- PATH issues: Automatically fix or provide exact copy-paste instructions

### FR-6: Progress Reporting

- GUI: Progress bar with step descriptions
- Scripts: Numbered step output with status indicators (OK/FAIL)

## Non-Functional Requirements

### NFR-1: Windows Compatibility

**Critical constraints (from real-world experience):**

1. **Korean encoding**: PowerShell on Korean Windows (cp949) causes comments and commands to merge on one line. Mitigation:
   - BAT (cmd) is the primary script format for Windows
   - PS1 is secondary/optional
   - Minimize non-ASCII characters in script files
   - Use UTF-8 with BOM where non-ASCII is unavoidable
2. **PowerShell version**: Target PowerShell 5.1 (ships with Windows 10). Do not use PS 7+ syntax.
3. **winget unavailable**: Do not depend on winget. Use direct download URLs for all prerequisites.
4. **Outdated systems**: Assume no Windows Update has been applied. Test on vanilla Windows 10 1809.

### NFR-2: Permission Handling

- Windows: Handle UAC elevation gracefully. Detect whether running as admin and request elevation if needed.
- macOS: Use `sudo` with clear explanation of why elevation is needed.
- Linux: Use `sudo` with clear explanation. Support both sudo and su.
- Never require running the installer as root/admin by default -- only elevate for specific operations.

### NFR-3: PATH Management

- After installing prerequisites, verify they are in PATH
- If not, add to PATH automatically:
  - Windows: Modify user-level PATH via registry (not system-level, to avoid admin requirement)
  - macOS/Linux: Append to `~/.bashrc`, `~/.zshrc`, or equivalent
- Notify user if shell restart is needed

### NFR-4: Download Handling

- All downloads to a temporary directory with proper permissions
- Verify download integrity where checksums are available
- Handle proxy/firewall environments: detect and use system proxy settings
- Timeout and retry logic for slow connections

### NFR-5: Result Size

- GUI executables: Target under 100MB each
- Total release bundle: Under 500MB

## Platform-Specific Notes

### Windows

- GUI (.exe) is the most important deliverable -- bypasses all shell encoding issues
- BAT script as primary script format (encoding-safe)
- PS1 script as secondary (may have encoding issues on Korean locale)
- Git for Windows detection: Check `git --version` and common install paths (`C:\Program Files\Git\`)
- Node.js detection: Check `node --version` and common install paths

### macOS

- GUI (.app) packaged via PyInstaller
- Gatekeeper: Unsigned app will show security warning. Provide instructions to bypass ("Open Anyway" in System Preferences)
- Homebrew detection: Check if `brew` exists, but do not require it
- Shell detection: Support both bash and zsh (macOS default since Catalina)

### Linux

- Script only (no GUI)
- Support major distributions: Ubuntu 20.04+, Debian 10+, Fedora, Arch
- Package manager detection: apt, dnf, pacman, apk
- Node.js installation via NodeSource repository or nvm

## GUI Wireframe (Text)

```
+------------------------------------------+
|            AIReady                        |
|          [Korean] [English]              |
+------------------------------------------+
|                                          |
|  Install: ( ) Claude Code                |
|           ( ) OpenClaw                   |
|                                          |
|  [Start Installation]                    |
|                                          |
+------------------------------------------+
|  Step 1: Checking system...        [OK]  |
|  Step 2: Installing Node.js...     [OK]  |
|  Step 3: Installing OpenClaw...    [..%] |
|  Step 4: Configuring API key...          |
|  Step 5: Running onboarding...           |
|                                          |
|  [=================         ] 60%        |
|                                          |
+------------------------------------------+
|  Status: Installing OpenClaw v2026.3...  |
+------------------------------------------+
```

## Script Flow (Pseudocode)

```
1. Detect OS and locale
2. Display welcome message
3. Check prerequisites
   - If missing: download and install
   - Verify installation and PATH
4. Install target tool
   - Download via official installer
   - Verify installation
5. Onboarding
   - Prompt for API key (if needed)
   - Run onboarding command
   - Verify setup (doctor/status check)
6. Display success message and next steps
```
