#!/bin/zsh
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <signed-bundle> [evidence-file]" >&2
  exit 2
fi

BUNDLE="$1"
OUT="${2:-macos-bundle-verify.txt}"
[[ -e "$BUNDLE" ]] || { echo "ERROR: bundle not found: $BUNDLE" >&2; exit 1; }

FAIL=0
{
  echo "# macOS release verification evidence"
  echo "bundle=$BUNDLE"
  echo
  echo "## quarantine"
  if xattr -p com.apple.quarantine "$BUNDLE" 2>/dev/null; then
    echo "quarantine=present"
  else
    echo "quarantine=missing"
    echo "WARNING: public distribution check must use the actually downloaded quarantined artifact."
  fi
  echo
  echo "## codesign"
  if codesign --verify --deep --strict --verbose=2 "$BUNDLE"; then
    echo "codesign=PASS"
  else
    echo "codesign=FAIL"
    FAIL=1
  fi
  codesign -dv --verbose=4 "$BUNDLE" 2>&1 || true
  echo
  echo "## stapler"
  if xcrun stapler validate "$BUNDLE" 2>&1; then
    echo "stapler=PASS"
  else
    echo "stapler=FAIL_OR_NOT_APPLICABLE"
  fi
  echo
  echo "## Gatekeeper"
  if spctl --assess --verbose=4 "$BUNDLE" 2>&1; then
    echo "spctl=PASS"
  else
    echo "spctl=FAIL"
    FAIL=1
  fi
} > "$OUT" 2>&1

cat "$OUT"
[[ "$FAIL" -eq 0 ]] || exit 1
echo "PASS: local signing/Gatekeeper checks passed."
echo "NOTE: still requires real quarantined download -> install -> host launch smoke test."
