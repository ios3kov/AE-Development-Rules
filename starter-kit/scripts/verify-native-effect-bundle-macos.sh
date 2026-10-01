#!/bin/zsh
set -euo pipefail

BUNDLE="${1:-}"
[[ -n "$BUNDLE" ]] || { echo "Usage: $0 <Effect.plugin>" >&2; exit 2; }
[[ "$(uname -s)" == "Darwin" ]] || { echo "ERROR: macOS only" >&2; exit 1; }
[[ -d "$BUNDLE" ]] || { echo "ERROR: bundle missing: $BUNDLE" >&2; exit 1; }

PLIST="$BUNDLE/Contents/Info.plist"
[[ -f "$PLIST" ]] || { echo "ERROR: Info.plist missing" >&2; exit 1; }

EXE=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$PLIST" 2>/dev/null || true)
[[ -n "$EXE" ]] || { echo "ERROR: CFBundleExecutable missing" >&2; exit 1; }
BIN="$BUNDLE/Contents/MacOS/$EXE"
[[ -f "$BIN" ]] || { echo "ERROR: binary missing: $BIN" >&2; exit 1; }

echo "[plist]"
plutil -lint "$PLIST"
/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$PLIST"
/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$PLIST"

echo "[binary]"
file "$BIN"
command -v lipo >/dev/null && lipo -archs "$BIN" || true

echo "[AE effect exports]"
SYMS="$(nm -gU "$BIN")"
echo "$SYMS" | grep -Eq '[[:space:]]_EffectMain$' || { echo "ERROR: EffectMain export missing" >&2; exit 1; }
echo "$SYMS" | grep -Eq '[[:space:]]_PluginDataEntryFunction2$' || { echo "ERROR: PluginDataEntryFunction2 export missing" >&2; exit 1; }
echo "$SYMS" | grep -E '_EffectMain$|_PluginDataEntryFunction2$'

echo "[PiPL/resources]"
RSRC_COUNT="$(find "$BUNDLE/Contents/Resources" -maxdepth 1 -type f -name '*.rsrc' 2>/dev/null | wc -l | tr -d ' ')"
[[ "$RSRC_COUNT" -gt 0 ]] || { echo "ERROR: no .rsrc/PiPL resource found" >&2; exit 1; }
find "$BUNDLE/Contents/Resources" -maxdepth 1 -type f -name '*.rsrc' -print

echo "[dynamic dependencies]"
otool -L "$BIN"

echo "[signature]"
codesign --verify --deep --strict --verbose=2 "$BUNDLE"
codesign -dv --verbose=2 "$BUNDLE" 2>&1 | grep -E 'Identifier=|TeamIdentifier=|Signature=' || true

echo "[hashes]"
shasum -a 256 "$BIN" "$PLIST"
find "$BUNDLE/Contents/Resources" -maxdepth 1 -type f -name '*.rsrc' -exec shasum -a 256 {} \;

echo "native effect bundle verification: PASS"
