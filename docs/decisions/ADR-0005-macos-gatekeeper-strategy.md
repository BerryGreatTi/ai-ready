# ADR-0005: macOS Gatekeeper Bypass Strategy

## Status

Accepted

## Context

macOS Gatekeeper blocks unsigned applications downloaded from the internet. AIReady GUI (.app) is built via PyInstaller and distributed unsigned through GitHub Releases. During v0.1.0-rc1 testing, the macOS .app was rejected with "cannot verify the developer" error, completely blocking beginners from using the GUI version.

Apple requires a paid Developer Program membership ($99/year) for code signing and notarization. This is not justified for an early-stage open-source project.

## Decision

Adopt a three-tier mitigation strategy for unsigned macOS builds:

**Tier 1 (Recommended): `xattr -cr` command**
- Release notes include a Terminal command to remove the quarantine flag:
  ```
  xattr -cr ~/Downloads/AIReady-ClaudeCode-Mac.app
  ```
- This is a single command that any user can copy-paste.

**Tier 2: Right-click -> Open**
- Standard macOS bypass: right-click the app, select "Open", then click "Open" on the warning dialog.
- If that fails: System Settings -> Privacy & Security -> "Open Anyway".

**Tier 3: Use the .sh script instead**
- The shell script version has no Gatekeeper issues.
- Users who cannot bypass Gatekeeper are directed to the script version.

All three tiers are documented in:
- GitHub Release notes (auto-generated via release.yml)
- Landing page (collapsible section)

**Future**: When the project matures, invest in an Apple Developer account for proper code signing and notarization.

## Consequences

- Beginners must perform one extra step before first launch (Tier 1 or 2).
- The shell script serves as a reliable fallback for users who cannot bypass Gatekeeper.
- Release notes are slightly longer due to bypass instructions.
- No cost incurred for code signing in early stages.

## Alternatives Considered

- **Apple Developer Program**: $99/year for code signing. Rejected for early-stage project.
- **Ad-hoc signing**: `codesign -s -` in CI. Does not satisfy Gatekeeper (still blocks unsigned apps from internet).
- **DMG with instructions**: Distribute as .dmg with a README inside. Adds complexity without solving the core issue.
