# Tool Interface

An abstract base class (`tools/base.py`) that defines the installation process for each target tool. Each tool (Claude Code, OpenClaw) has a concrete implementation.

The Tool interface returns a list of `Step` objects that the `Installer` engine executes sequentially. The GUI dynamically renders its progress screen based on this step list, so adding steps to a Tool automatically updates the UI.

## Key methods

- `get_prerequisites()` - List of prerequisites the tool needs (Git, Node.js, UV for both tools)
- `get_steps()` - Ordered list of installation steps (5 steps: check_system, install_prereqs, verify_prereqs, install_tool, verify_install)
- `get_verify_commands()` - Commands to verify successful installation
- `get_onboarding_config()` - Returns `OnboardingConfig(mode=OnboardingMode.AUTOMATIC)` (onboarding is handled by the CLI after the GUI launches it in a terminal)

## Post-install flow

After all steps complete successfully, the GUI navigates to `CompleteScreen` which auto-launches the tool in a new terminal for CLI-based onboarding. See [Onboarding Modes](onboarding-modes.md).
