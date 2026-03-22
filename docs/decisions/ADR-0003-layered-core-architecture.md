# ADR-0003: Layered Core Architecture (Approach A)

## Status

Accepted

## Context

AIReady produces 10 deliverables: 4 GUI executables and 6 native scripts across Windows, macOS, and Linux. The architecture must balance code reuse with the independence of native scripts.

Options evaluated:
1. **Layered Core (A)**: Shared Python core for GUI, independent native scripts
2. **Python Everywhere (B)**: Python core for both GUI and CLI, thin native wrappers that download CLI
3. **Configuration-Driven (C)**: Declarative YAML + Jinja2 templates to generate scripts

## Decision

Use Layered Core (Approach A).

- `src/aiready/core/` contains platform-agnostic installation logic used by the GUI.
- `src/aiready/platforms/` contains platform-specific implementations behind an abstract `Platform` interface.
- `src/aiready/tools/` defines tool-specific installation steps behind an abstract `Tool` interface.
- `scripts/` contains fully independent native scripts (BAT, PS1, SH) with no Python dependency.

## Consequences

**Benefits:**
- Scripts remain lightweight (few KB), inspectable, and can be curl-piped directly.
- GUI versions get full code reuse through the shared Python core.
- Each script is independently debuggable -- a Windows BAT bug cannot affect macOS scripts.
- New tools can be added by implementing the `Tool` interface (GUI auto-adapts).

**Trade-offs:**
- Some logic duplication between Python core and native scripts (both implement the same installation flow).
- Script changes must be manually kept in sync with the design spec.
- Mitigation: The design spec serves as the synchronization reference, and a `.dev/scripts/` verification tool can check consistency.

## Alternatives Considered

- **Python Everywhere (B)**: Maximum code reuse, zero logic duplication. But "scripts" become ~50MB executable downloads instead of lightweight text files, defeating the purpose of having script versions (easy to share, inspect, curl-pipe).
- **Configuration-Driven (C)**: Scripts generated from templates ensure consistency. But YAML cannot express complex edge cases (Korean encoding workarounds, distro-specific package manager logic), and generated scripts are harder to debug than hand-written ones. Over-engineered for 2 tools and 3 platforms.
