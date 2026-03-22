# Platform Interface

An abstract base class (`platforms/base.py`) that defines all OS-specific operations the installer needs. Each supported OS has a concrete implementation: `WindowsPlatform`, `MacOSPlatform`, `LinuxPlatform`.

The core installation logic depends on this interface, not on specific platforms. This means core code never contains `if windows:` branches -- platform-specific behavior is encapsulated in the implementation.

## Key methods

- `check_command()` - Check if a tool exists in PATH and return its version
- `install_prerequisite()` - Install a prerequisite (Node.js, Git, etc.)
- `verify_prerequisite()` - Confirm installation succeeded and is in PATH
- `add_to_path()` - Add a directory to the user's PATH
- `request_elevation()` - Request admin/root privileges for a specific operation
- `run_command()` - Execute a shell command with output capture
