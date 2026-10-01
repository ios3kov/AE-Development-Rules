#!/bin/zsh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$ROOT" ]] || { echo "ERROR: run inside a Git repository" >&2; exit 1; }

OUT="${1:-$ROOT/.artifacts/dependencies}"
mkdir -p "$OUT"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="$OUT/dependency-evidence-$STAMP.txt"

patterns=(
  "package.json"
  "package-lock.json"
  "npm-shrinkwrap.json"
  "pnpm-lock.yaml"
  "yarn.lock"
  "Cargo.toml"
  "Cargo.lock"
  "requirements.txt"
  "requirements-dev.txt"
  "poetry.lock"
  "Pipfile"
  "Pipfile.lock"
  "pyproject.toml"
  "vcpkg.json"
  "vcpkg-lock.json"
  "conanfile.txt"
  "conanfile.py"
  "conan.lock"
)

{
  echo "# Dependency evidence"
  echo "utc=$STAMP"
  echo "repo=$ROOT"
  echo "commit=$(git -C "$ROOT" rev-parse HEAD)"
  echo
  echo "## Manifest / lockfile hashes"
  found=0
  for name in "${patterns[@]}"; do
    while IFS= read -r path; do
      found=1
      shasum -a 256 "$path"
    done < <(find "$ROOT" -type f -name "$name" -not -path '*/node_modules/*' -not -path '*/target/*' -not -path '*/.git/*' | LC_ALL=C sort)
  done
  [[ "$found" -eq 1 ]] || echo "No known dependency manifest/lockfile found."

  echo
  echo "## Tool availability"
  for tool in npm cargo python3 pip pip-audit osv-scanner syft cyclonedx-py; do
    if command -v "$tool" >/dev/null 2>&1; then
      echo "$tool=$(command -v "$tool")"
    else
      echo "$tool=NOT_FOUND"
    fi
  done

  echo
  echo "## Notes"
  echo "This file inventories local dependency sources only."
  echo "Run an ecosystem-appropriate vulnerability scanner separately and record PASS/FAIL/BLOCKED/NOT RUN/N/A."
  echo "For public dependency-heavy products, generate an SPDX or CycloneDX SBOM where practical."
} > "$REPORT"

cat "$REPORT"
echo "Evidence: $REPORT"
