#!/bin/zsh
set -euo pipefail
setopt noclobber

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
[[ ! -e "$OUT" && ! -L "$OUT" ]] || { echo "ERROR: evidence output exists" >&2; exit 2; }
PARTIAL=0
probe() {
  local probe_exit=0
  "$@" 2>&1 || probe_exit=$?
  echo "probe_exit=$probe_exit"
  if [[ "$probe_exit" -ne 0 ]]; then PARTIAL=1; fi
}
file "$BIN" | grep -q 'Mach-O' || { echo "INCOMPLETE: target is not Mach-O" >&2; exit 2; }

{
  echo "# macOS binary compatibility evidence"
  echo "target=$TARGET"
  echo "binary=$BIN"
  echo
  echo "## file"
  file "$BIN"
  echo
  echo "## architectures"
  probe lipo -archs "$BIN"
  echo
  echo "## build / deployment target"
  if command -v vtool >/dev/null; then
    probe vtool -show-build "$BIN"
  else
    probe otool -l "$BIN"
  fi
  echo
  echo "## linked libraries"
  probe otool -L "$BIN"
  echo
  echo "## undefined external symbols"
  probe nm -u "$BIN"
  echo
  echo "## signing"
  probe codesign -dv --verbose=4 "$TARGET"
  probe codesign --verify --deep --strict --verbose=2 "$TARGET"
} > "$OUT"

{
  echo
  echo "## Collection status"
  if [[ "$PARTIAL" -eq 0 ]]; then echo "collection_status=COMPLETE"; else echo "collection_status=PARTIAL"; fi
  echo "audit_verdict=NOT_ASSIGNED"
} >> "$OUT"

echo "Evidence: $OUT"
echo "Evidence collection: see per-probe statuses"
[[ "$PARTIAL" -eq 0 ]] || exit 2
echo "NOTE: exit code 0 means evidence collection completed; individual probe failures remain evidence and do not mean Compatibility: PASS/VERIFIED."
