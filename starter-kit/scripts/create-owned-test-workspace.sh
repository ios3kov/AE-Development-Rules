#!/bin/zsh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$ROOT" ]] || { echo "ERROR: run inside a Git repository" >&2; exit 1; }

BASE="${AE_TEST_WORKSPACE_ROOT:-$ROOT/.ae-test-workspace}"
if [[ -L "$BASE" ]]; then
  echo "ERROR: refusing symlinked AE test workspace root: $BASE" >&2
  exit 4
fi

mkdir -p "$BASE"
[[ ! -L "$BASE" ]] || { echo "ERROR: workspace root became a symlink" >&2; exit 4; }

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SHORT="$(git -C "$ROOT" rev-parse --short HEAD)"
RUN_ID="AE-TEST-$STAMP-$SHORT-$$"
WORK="$BASE/$RUN_ID"

[[ ! -e "$WORK" ]] || { echo "ERROR: workspace collision: $WORK" >&2; exit 4; }
mkdir "$WORK"

{
  echo "run_id=$RUN_ID"
  echo "repo=$ROOT"
  echo "commit=$(git -C "$ROOT" rev-parse HEAD)"
  echo "pid=$$"
  echo "utc=$STAMP"
} > "$WORK/OWNERSHIP.txt"

echo "$WORK"
echo "NOTE: only this owned workspace may be automatically cleaned by the test that created it." >&2
