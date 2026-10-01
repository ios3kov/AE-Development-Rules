#!/bin/zsh
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <artifact-path> [evidence-dir]" >&2
  exit 2
fi

ARTIFACT="$1"
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$ROOT" ]] || { echo "ERROR: run inside a Git repository" >&2; exit 1; }
[[ -e "$ARTIFACT" ]] || { echo "ERROR: artifact not found: $ARTIFACT" >&2; exit 1; }

COMMIT="$(git -C "$ROOT" rev-parse HEAD)"
SHORT="$(git -C "$ROOT" rev-parse --short HEAD)"
DIRTY="$(git -C "$ROOT" status --porcelain)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ID="AE-ARTIFACT-$STAMP-$SHORT"
OUT="${2:-$ROOT/.artifacts/evidence/$RUN_ID}"
mkdir -p "$OUT"

print -r -- "$COMMIT" > "$OUT/source-commit.txt"
git -C "$ROOT" status --short > "$OUT/source-state.txt"
print -r -- "$RUN_ID" > "$OUT/test-run-id.txt"
print -r -- "$ARTIFACT" > "$OUT/artifact-path.txt"

{
  echo "utc=$STAMP"
  echo "uname=$(uname -a)"
  command -v sw_vers >/dev/null && sw_vers
  command -v xcodebuild >/dev/null && xcodebuild -version
} > "$OUT/environment.txt" 2>&1

if [[ -f "$ARTIFACT" ]]; then
  shasum -a 256 "$ARTIFACT" > "$OUT/SHA256.txt"
elif [[ -d "$ARTIFACT" ]]; then
  : > "$OUT/SHA256-files.txt"
  while IFS= read -r file; do
    shasum -a 256 "$file" >> "$OUT/SHA256-files.txt"
  done < <(find "$ARTIFACT" -type f | LC_ALL=C sort)
else
  echo "ERROR: artifact must be a regular file or directory" >&2
  exit 1
fi

if [[ -n "$DIRTY" ]]; then
  echo "DIRTY" > "$OUT/source-cleanliness.txt"
else
  echo "CLEAN" > "$OUT/source-cleanliness.txt"
fi

echo "Test Run ID: $RUN_ID"
echo "Commit: $COMMIT"
echo "Evidence: $OUT"
