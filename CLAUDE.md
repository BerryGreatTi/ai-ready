# AIReady (install-ai)

Cross-platform installer helper for beginners to easily set up Claude Code and OpenClaw on Windows, Linux, and macOS.

## Project Overview

- **Brand**: AIReady
- **Tech stack**: Python 3.12+ / CustomTkinter / PyInstaller
- **Target users**: Non-developer beginners (Korean and English)
- **Requirements spec**: [docs/specs/2026-03-22-aiready-requirements.md](docs/specs/2026-03-22-aiready-requirements.md)

### Deliverables

| Platform | Claude Code | OpenClaw |
|----------|-------------|----------|
| Windows GUI (.exe) | Yes | Yes |
| Windows Script (.bat + .ps1) | Yes | Yes |
| macOS GUI (.app) | Yes | Yes |
| macOS Script (.sh) | Yes | Yes |
| Linux Script (.sh) | Yes | Yes |

### Critical: Korean Windows

- BAT (cmd) is primary script for Windows. PS1 is secondary.
- Target PowerShell 5.1. No PS 7+ syntax.
- Do not depend on winget.
- Minimize non-ASCII in script files. Use UTF-8 BOM where unavoidable.
- See [Korean Windows issues memory](docs/glossary/target-user.md) for details.

## Documentation

This project follows a documentation-first workflow. The `docs/` directory is the authoritative source of truth for design decisions, concept definitions, and specifications.

### Rules

1. **Scope boundary**: `docs/` is for project-level knowledge -- concepts, processes, protocols, designs, and decisions. Development-time artifacts (test fixtures, smoke test docs, helper script notes) belong in `.dev/`, not here.
2. **Concept lookup**: Check `docs/glossary/` when a concept is ambiguous. Create an entry if none exists.
3. **Docs-first updates**: Update `docs/` before changing implementation.
4. **Glossary authority**: Glossary definitions are authoritative. Code divergence means code is wrong.
5. **Decision records**: Record all design/architectural decisions as ADRs in `docs/decisions/` (`ADR-NNNN-<slug>.md`). Check existing ADRs before making potentially conflicting decisions.

### Key Documents

| Document | Purpose | When to read |
|----------|---------|--------------|
| [docs/README.md](docs/README.md) | Documentation index and governance | Session start |
| [docs/glossary/](docs/glossary/) | Concept definitions | When terms are ambiguous |
| [docs/decisions/](docs/decisions/) | Architecture Decision Records | Before making architectural changes |
| [docs/specs/](docs/specs/) | Design specifications | When understanding system design |
| [docs/plans/](docs/plans/) | Implementation plans | When executing features |

## Development Workspace

`.dev/` contains development-time artifacts that support the coding process but are not part of the shipped product.

### Rules

1. **No production imports**: Production code must never import from `.dev/`. If something becomes production-worthy, move it to the appropriate project directory.
2. **Ephemeral tmp**: `.dev/tmp/` is scratch space. Anything there can be deleted at any time without consequence.
3. **Docs boundary**: Persistent documentation belongs in `docs/`, not `.dev/`. Transient notes are acceptable, but anything referenced across sessions should be moved to `docs/`.

### Structure

| Directory | Purpose |
|-----------|---------|
| `.dev/scripts/` | Helper scripts, validators, one-off automation |
| `.dev/tmp/` | Ephemeral scratch files, simulation outputs |

## Release

Release artifacts are stored in `release/<version>/` directories. This folder is gitignored -- release builds are generated, not tracked.
