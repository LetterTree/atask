#!/usr/bin/env bash
# Build atask binary for the current platform using PyInstaller.
# Usage: sh npm/scripts/build.sh [--platform linux|darwin|win32]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NPM_DIR="$REPO_ROOT/npm"

# Detect platform
case "${1:-}" in
  --platform)
    PLATFORM="$2"
    ;;
  *)
    case "$(uname -s)" in
      Linux*)  PLATFORM="linux" ;;
      Darwin*) PLATFORM="darwin" ;;
      MINGW*|MSYS*|CYGWIN*) PLATFORM="win32" ;;
      *) echo "ERROR: unknown platform $(uname -s)" >&2; exit 1 ;;
    esac
    ;;
esac

OUT_DIR="$NPM_DIR/packages/atask-${PLATFORM}-x64/bin"
mkdir -p "$OUT_DIR"

echo "Building atask for platform: $PLATFORM"
echo "Output dir: $OUT_DIR"

cd "$REPO_ROOT"
pyinstaller npm/atask.spec \
  --distpath "$OUT_DIR" \
  --workpath /tmp/atask-build \
  --noconfirm

if [ "$PLATFORM" = "win32" ]; then
  BINARY="$OUT_DIR/atask.exe"
else
  BINARY="$OUT_DIR/atask"
fi

if [ ! -f "$BINARY" ]; then
  echo "ERROR: binary not found at $BINARY" >&2
  exit 1
fi

echo "Built: $BINARY"
