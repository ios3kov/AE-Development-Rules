#!/bin/zsh
set -euo pipefail
setopt noclobber

if [[ $# -lt 1 || $# -gt 4 ]]; then
  echo "Usage: $0 <target> [NEW-evidence-file] [local|public] [required|na]" >&2
  exit 2
fi

BUNDLE="$1"
OUT="${2:-macos-bundle-verify.txt}"
MODE="${3:-local}"
STAPLING="${4:-required}"
[[ "$MODE" == "local" || "$MODE" == "public" ]] || { echo "ERROR: invalid mode" >&2; exit 2; }
[[ "$STAPLING" == "required" || "$STAPLING" == "na" ]] || { echo "ERROR: invalid stapling policy" >&2; exit 2; }
if [[ "$STAPLING" == "na" && "${AE_STAPLING_NA_REASON:-}" != *[^[:space:]$'\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff']* ]]; then
  echo "BLOCKED: N/A requires AE_STAPLING_NA_REASON" >&2; exit 2
fi
[[ ! -e "$OUT" && ! -L "$OUT" ]] || { echo "ERROR: evidence output exists" >&2; exit 2; }
[[ -e "$BUNDLE" ]] || { echo "ERROR: bundle not found: $BUNDLE" >&2; exit 1; }
case "$BUNDLE" in
  *.pkg) ASSESS_TYPE=install ;;
  *.dmg) ASSESS_TYPE=open ;;
  *.app) ASSESS_TYPE=execute ;;
  *) echo "BLOCKED: assess final app/pkg/dmg; native plugin alone needs a project-specific host/distribution test" >&2; exit 2 ;;
esac

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
    if [[ "$MODE" == "public" ]]; then FAIL=1; fi
  fi
  echo
  echo "## signature"
  if [[ "$ASSESS_TYPE" == "install" ]]; then
    if pkgutil --check-signature "$BUNDLE"; then
      echo "pkgutil=PASS"
    else
      echo "pkgutil=FAIL"
      FAIL=1
    fi
  else
    if codesign --verify --deep --strict --verbose=2 "$BUNDLE"; then
      echo "codesign=PASS"
    else
      echo "codesign=FAIL"
      FAIL=1
    fi
    codesign -dv --verbose=4 "$BUNDLE" 2>&1 || true
  fi
  echo
  echo "## stapler"
  if [[ "$STAPLING" == "na" ]]; then
    echo "stapler=N/A reason=$AE_STAPLING_NA_REASON"
  elif xcrun stapler validate "$BUNDLE" 2>&1; then
    echo "stapler=PASS"
  else
    echo "stapler=FAIL"
    FAIL=1
  fi
  echo
  echo "## Gatekeeper"
  ASSESS_ARGS=(--assess --type "$ASSESS_TYPE" --verbose=4)
  if [[ "$ASSESS_TYPE" == "open" ]]; then
    ASSESS_ARGS+=(--context context:primary-signature)
  fi
  if spctl "${ASSESS_ARGS[@]}" "$BUNDLE" 2>&1; then
    echo "spctl=PASS"
  else
    echo "spctl=FAIL"
    FAIL=1
  fi
} > "$OUT" 2>&1

cat "$OUT"
[[ "$FAIL" -eq 0 ]] || exit 1
echo "PASS: selected $MODE signing/stapling/Gatekeeper checks passed."
echo "NOTE: still requires real quarantined download -> install -> host launch smoke test."
