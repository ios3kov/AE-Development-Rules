#!/bin/zsh
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <bundle-or-binary> [evidence-file]" >&2
  exit 2
fi

TARGET="$1"
OUT="${2:-macos-binary-audit.txt}"

resolve_binary() {
  local target="$1"
  if [[ -f "$target" ]]; then
    print -r -- "$target"
    return
  fi
  local plist="$target/Contents/Info.plist"
  if [[ -f "$plist" ]]; then
    local exe
    exe=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$plist" 2>/dev/null || true)
    if [[ -n "$exe" && -f "$target/Contents/MacOS/$exe" ]]; then
      print -r -- "$target/Contents/MacOS/$exe"
      return
    fi
  fi
  echo "ERROR: could not resolve Mach-O binary from: $target" >&2
  exit 1
}

BIN="$(resolve_binary "$TARGET")"

{
  echo "# macOS binary compatibility evidence"
  echo "target=$TARGET"
  echo "binary=$BIN"
  echo
  echo "## file"
  file "$BIN"
  echo
  echo "## architectures"
  lipo -archs "$BIN" 2>&1 || true
  echo
  echo "## build / deployment target"
  if command -v vtool >/dev/null; then
    vtool -show-build "$BIN" 2>&1 || true
  else
    otool -l "$BIN" 2>&1 | grep -A5 -E 'LC_BUILD_VERSION|LC_VERSION_MIN_MACOSX' || true
  fi
  echo
  echo "## linked libraries"
  otool -L "$BIN" 2>&1 || true
  echo
  echo "## undefined external symbols"
  nm -u "$BIN" 2>&1 || true
  echo
  echo "## signing"
  codesign -dv --verbose=4 "$TARGET" 2>&1 || true
  codesign --verify --deep --strict --verbose=2 "$TARGET" 2>&1 || true
} > "$OUT"

echo "Evidence: $OUT"
