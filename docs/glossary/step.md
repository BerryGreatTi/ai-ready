# Step

An immutable data object (`core/installer.py`) representing a single unit of work in the installation process. Steps are defined by Tool implementations and executed sequentially by the Installer engine.

## Fields

- `id` - Unique identifier (e.g., "install_nodejs")
- `name_key` - i18n key for display name (e.g., "step.install_nodejs")
- `action` - Callable that performs the work and returns a StepResult
- `required` - If true, failure aborts the entire installation

## StepResult states

- `RUNNING` - Currently executing
- `SUCCESS` - Completed successfully
- `FAILED` - Failed (may abort or continue depending on `required`)
- `SKIPPED` - Not applicable (e.g., Git install skipped on macOS)
