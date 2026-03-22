# Tool Interface

An abstract base class (`tools/base.py`) that defines the installation and onboarding process for each target tool. Each tool (Claude Code, OpenClaw) has a concrete implementation.

The Tool interface returns a list of `Step` objects that the `Installer` engine executes sequentially. The GUI dynamically renders its progress screen based on this step list, so adding steps to a Tool automatically updates the UI.

## Key methods

- `get_prerequisites()` - List of prerequisites the tool needs
- `get_steps()` - Ordered list of installation steps
- `get_verify_commands()` - Commands to verify successful installation
- `get_onboarding_config()` - Configuration for the onboarding phase (AUTOMATIC or GUIDED)
