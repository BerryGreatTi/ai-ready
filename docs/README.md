# AIReady Documentation

Cross-platform installer helper for beginners to easily set up Claude Code and OpenClaw on Windows, Linux, and macOS.

## Directory Structure

| Directory | Purpose | When to use |
|-----------|---------|-------------|
| `glossary/` | Authoritative definitions of core concepts and terms | When introducing a new concept or when a term's meaning is ambiguous |
| `decisions/` | Architecture Decision Records (ADRs) | When making a design choice that affects the project's direction |
| `specs/` | Design specifications and technical designs | When designing a feature or system component before implementation |
| `plans/` | Implementation plans with phased steps | When breaking a spec into executable work |

## Documentation Governance

1. **Authoritative source**: `docs/` contains the authoritative design decisions, definitions, and specifications. Implementation follows documentation, not the other way around.
2. **Scope boundary**: `docs/` is for project-level knowledge -- concepts, processes, protocols, designs, and decisions that define the project's identity and direction. Development-time artifacts (test fixtures, smoke test docs, helper script notes, temporary analysis) belong in `.dev/`, not here.
3. **Concept lookup**: When a concept is ambiguous, check `docs/glossary/` before proceeding. If no entry exists, create one.
4. **Docs-first updates**: Update `docs/` before changing implementation. This prevents drift between what's documented and what's built.
5. **Glossary authority**: Glossary definitions are authoritative. If code behavior diverges from a glossary definition, the code needs to change.
6. **Decision records**: Every design or architectural decision must be recorded as an ADR in `docs/decisions/` using the format `ADR-NNNN-<slug>.md`. Check existing ADRs before making decisions that might conflict.

## ADR Index

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0001](decisions/ADR-0001-docs-first-workflow.md) | Documentation-first workflow | Accepted |
| [ADR-0002](decisions/ADR-0002-tech-stack.md) | Python + CustomTkinter + PyInstaller tech stack | Accepted |
| [ADR-0003](decisions/ADR-0003-layered-core-architecture.md) | Layered Core architecture (Approach A) | Accepted |
| [ADR-0004](decisions/ADR-0004-windows-bat-first.md) | BAT as primary Windows script format | Accepted |
| [ADR-0005](decisions/ADR-0005-macos-gatekeeper-strategy.md) | macOS Gatekeeper bypass strategy | Accepted |
| [ADR-0006](decisions/ADR-0006-permanent-path-setup.md) | Permanent PATH setup in shell config | Accepted |
| [ADR-0007](decisions/ADR-0007-universal-prerequisites.md) | Universal prerequisites (Git, Node.js, UV) for all tools | Accepted |
| [ADR-0008](decisions/ADR-0008-windows-installer-lessons.md) | Windows installer lessons learned (rc1-rc15) | Accepted |
| [ADR-0009](decisions/ADR-0009-remove-doctor-step.md) | Remove `claude doctor` step (TTY hang) | Accepted |
| [ADR-0010](decisions/ADR-0010-cli-handoff-onboarding.md) | Hand off auth/onboarding to CLI | Accepted |

## Specs Index

| Spec | Title |
|------|-------|
| [2026-03-22-aiready-requirements](specs/2026-03-22-aiready-requirements.md) | Requirements specification |
| [2026-03-22-aiready-design](specs/2026-03-22-aiready-design.md) | Architecture and design specification |
| [2026-03-24-testing-guide](specs/2026-03-24-testing-guide.md) | Pre-release testing procedure |
| [2026-03-25-virtualbox-test-setup](specs/2026-03-25-virtualbox-test-setup.md) | VirtualBox Windows 10/11 test environment setup |

## Plans Index

| Plan | Title |
|------|-------|
| [2026-03-22-aiready-implementation](plans/2026-03-22-aiready-implementation.md) | Implementation plan (42 tasks, 12 phases) |

## Glossary Index

| Term | Description |
|------|-------------|
| [AIReady](glossary/aiready.md) | Project name, brand, file naming convention |
| [Claude Code](glossary/claude-code.md) | Target tool: Anthropic's CLI coding assistant |
| [OpenClaw](glossary/openclaw.md) | Target tool: open-source AI personal assistant |
| [Target User](glossary/target-user.md) | Non-developer beginner persona and design implications |
| [Platform Interface](glossary/platform-interface.md) | Abstract OS abstraction layer |
| [Tool Interface](glossary/tool-interface.md) | Abstract tool installation definition |
| [Step](glossary/step.md) | Immutable unit of work in installation process |
| [Onboarding Modes](glossary/onboarding-modes.md) | CLI handoff model for post-install onboarding |
| [Native Installer](glossary/native-installer.md) | Claude Code's zero-dependency installation method |

## Reading Order

1. This README (governance and structure)
2. `glossary/` entries (understand the vocabulary)
3. `decisions/` (understand why things are the way they are)
4. `specs/` (understand current design)
5. `plans/` (understand what's being built)
