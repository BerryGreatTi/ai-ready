# ADR-0001: Documentation-first Workflow

## Status

Accepted

## Context

install-ai is a cross-platform installer project targeting beginners on Windows, Linux, and macOS. The project involves multiple output formats (GUI executables, shell scripts), platform-specific logic, and prerequisite management. As the project grows, design decisions about platform handling, prerequisite detection, and user experience will accumulate across code comments, commit messages, and conversations. Without a single authoritative source, definitions drift and sessions restart without shared understanding.

## Decision

Adopt `docs/` as the single authoritative source for design decisions, concept definitions, and specifications. Establish governance rules:

1. `docs/` contains authoritative design decisions, definitions, and specifications.
2. `docs/` is scoped to project-level knowledge. Development artifacts belong in `.dev/`.
3. Check `docs/glossary/` when a concept is ambiguous; create an entry if none exists.
4. Update `docs/` before changing implementation.
5. Glossary definitions are authoritative; code divergence means code is wrong.
6. Record all design/architectural decisions as ADRs in `docs/decisions/`.

## Consequences

Every session should read `docs/README.md` for orientation. Concepts and decisions cannot exist only in code or conversation. There is a small upfront cost to writing documentation before code, but this pays off as the project supports multiple platforms with distinct installation workflows.

## Alternatives Considered

- **Code-only documentation**: Relying on inline comments and README. Rejected because cross-platform logic makes it hard to capture decisions that span multiple platform-specific files.
- **Wiki-based**: External wiki for documentation. Rejected because it separates docs from the codebase, making them harder to keep in sync.
