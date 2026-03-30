# ADR-0011: PyInstaller Onedir Mode for macOS Bundles

## Status

Accepted

## Context

macOS `.spec` files used PyInstaller's **onefile** mode: binaries and data were packed into a single EXE, which was then wrapped in a `.app` BUNDLE. This worked but produced a deprecation warning starting in PyInstaller 6.19:

> DEPRECATION: Onefile mode in combination with macOS .app bundles (windowed mode) don't make sense (a .app bundle can not be a single file) and clashes with macOS's security. Please migrate to onedir mode. This will become an error in v7.0.

The deprecation is scheduled to become a hard error in PyInstaller 7.0, which would break the macOS build pipeline.

## Decision

Migrate macOS `.spec` files from onefile to **onedir** mode:

- Remove `a.binaries` and `a.datas` from `EXE()`, add `exclude_binaries=True`
- Add a `COLLECT` step that gathers binaries and data into a directory
- Pass `coll` (COLLECT output) to `BUNDLE` instead of `exe`

Additionally, pass `version=VERSION` to BUNDLE using the `AIREADY_VERSION` environment variable (set by `build-all.sh`), so `CFBundleShortVersionString` in `Info.plist` reflects the actual build version instead of `0.0.0`.

Windows `.spec` files remain unchanged (onefile mode without BUNDLE has no deprecation).

## Consequences

- macOS `.app` bundles now contain a `Frameworks/` directory with shared libraries and data files, instead of packing everything into a single binary. The zip size is comparable.
- The PyInstaller deprecation warning is eliminated.
- The build will not break when upgrading to PyInstaller 7.0.
- `Info.plist` version is now accurate, improving macOS system integration (e.g., "Get Info" shows correct version).

## Alternatives Considered

- **Ignore the warning**: Defers the problem to PyInstaller 7.0 upgrade, where it becomes a blocking error. Rejected because the fix is trivial and the migration path is clear.
