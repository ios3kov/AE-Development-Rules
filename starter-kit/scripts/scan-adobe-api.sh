#!/bin/zsh
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <source-dir> [output-dir]" >&2
  exit 2
fi

SRC="$1"
OUT="${2:-.artifacts/compatibility-api}"
mkdir -p "$OUT"
[[ -d "$SRC" ]] || { echo "ERROR: source directory not found: $SRC" >&2; exit 1; }

USAGE="$OUT/adobe-api-usage.txt"
SYMBOLS="$OUT/adobe-api-symbols.txt"

grep -RInE --include='*.c' --include='*.cc' --include='*.cpp' --include='*.cxx' --include='*.h' --include='*.hpp' --include='*.r' --include='*.mm' '(PF_|AEGP_|SmartFX|SmartPreRender|SmartRender|PF_Cmd_|kPF|kAEGP)' "$SRC" > "$USAGE" || true

grep -RhoE --include='*.c' --include='*.cc' --include='*.cpp' --include='*.cxx' --include='*.h' --include='*.hpp' --include='*.r' --include='*.mm' '(PF_[A-Za-z0-9_]+|AEGP_[A-Za-z0-9_]+|PF_Cmd_[A-Za-z0-9_]+|kPF[A-Za-z0-9_]*|kAEGP[A-Za-z0-9_]*)' "$SRC" | LC_ALL=C sort -u > "$SYMBOLS" || true

echo "Usage evidence: $USAGE"
echo "Unique identifiers: $SYMBOLS"
echo "NEXT: map relevant identifiers/suite revisions to minimum documented AE/SDK versions."
echo "NOTE: this prepares evidence only; it does not assign Compatibility: VERIFIED or STATIC-COMPATIBLE."
