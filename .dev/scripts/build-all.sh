#!/usr/bin/env bash
set -euo pipefail

# AIReady Build Script
# Usage: .dev/scripts/build-all.sh <version>
# Builds GUI executables for the current platform and collects scripts

VERSION="${1:?Usage: build-all.sh <version>}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RELEASE_DIR="$ROOT/release/$VERSION"

echo "Building AIReady v$VERSION..."
echo "Root: $ROOT"

# Clean
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"/{gui,scripts/{windows,macos,linux}}

# Detect platform
OS="$(uname -s)"

# Build GUI (platform-specific)
cd "$ROOT"
source .venv/bin/activate 2>/dev/null || true

case "$OS" in
    Darwin)
        echo "Building macOS GUI..."
        pyinstaller build/pyinstaller/macos-claude.spec --distpath "$RELEASE_DIR/gui" --workpath /tmp/aiready-build -y
        pyinstaller build/pyinstaller/macos-openclaw.spec --distpath "$RELEASE_DIR/gui" --workpath /tmp/aiready-build -y
        # Zip .app bundles
        cd "$RELEASE_DIR/gui"
        for app in *.app; do
            zip -r "${app%.app}.zip" "$app" && rm -rf "$app"
        done
        cd "$ROOT"
        ;;
    Linux)
        echo "Linux: No GUI build (scripts only per design spec)"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        echo "Building Windows GUI..."
        pyinstaller build/pyinstaller/windows-claude.spec --distpath "$RELEASE_DIR/gui" --workpath /tmp/aiready-build -y
        pyinstaller build/pyinstaller/windows-openclaw.spec --distpath "$RELEASE_DIR/gui" --workpath /tmp/aiready-build -y
        ;;
esac

# Copy scripts
echo "Copying scripts..."
cp scripts/windows/* "$RELEASE_DIR/scripts/windows/" 2>/dev/null || true
cp scripts/macos/* "$RELEASE_DIR/scripts/macos/" 2>/dev/null || true
cp scripts/linux/* "$RELEASE_DIR/scripts/linux/" 2>/dev/null || true

# Generate checksums
echo "Generating checksums..."
cd "$RELEASE_DIR"
find . -type f -not -name "CHECKSUMS.txt" | sort | xargs sha256sum > CHECKSUMS.txt 2>/dev/null || \
find . -type f -not -name "CHECKSUMS.txt" | sort | xargs shasum -a 256 > CHECKSUMS.txt

echo ""
echo "Release v$VERSION built at: $RELEASE_DIR"
ls -la "$RELEASE_DIR"
