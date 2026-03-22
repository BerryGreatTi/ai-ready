# Onboarding Modes

The two modes that define how AIReady handles post-installation setup for each tool.

## AUTOMATIC (C)

The installer handles everything programmatically. The user provides input (e.g., API key) through the GUI/script, and the installer executes all onboarding commands.

**Used by:** OpenClaw -- API key can be set via environment variable, onboarding command can be run non-interactively.

## GUIDED (B)

The installer cannot fully automate the process because it requires external interaction (e.g., browser-based OAuth). Instead, the installer:
1. Opens the required external tool (browser, website)
2. Displays step-by-step instructions in the UI
3. Waits for the user to confirm completion
4. Verifies the result programmatically

**Used by:** Claude Code -- authentication requires browser-based OAuth flow that cannot be intercepted programmatically.
