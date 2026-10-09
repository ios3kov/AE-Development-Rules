#!/bin/zsh
set -euo pipefail

DOCS_ONLY=0
if [[ $# -eq 1 && "$1" == "--docs-only" ]]; then
  DOCS_ONLY=1
elif [[ $# -ne 0 ]]; then
  echo "Usage: preflight.sh [--docs-only]" >&2; exit 2
fi
SCRIPTS="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$ROOT" ]] || { echo "ERROR: run inside a Git repository" >&2; exit 1; }
cd "$ROOT"

echo "[preflight] git diff"
git diff --check
git diff --cached --check
if [[ -n "${AE_PREFLIGHT_BASE_REF:-}" ]]; then
  git rev-parse --verify "$AE_PREFLIGHT_BASE_REF^{commit}" >/dev/null
  git diff --check "$AE_PREFLIGHT_BASE_REF...HEAD"
fi

if [[ "$DOCS_ONLY" -eq 1 ]]; then
  command -v node >/dev/null || { echo "BLOCKED: documentation scope check requires Node" >&2; exit 2; }
  node "$SCRIPTS/lib/preflight-docs.mjs"
  echo "[preflight] PASS: documentation scope and Git whitespace only; code/AE checks: NOT RUN"
  exit 0
fi

CHECKS_RUN=0
if [[ -f package.json ]]; then
  command -v node >/dev/null && command -v npm >/dev/null || { echo "BLOCKED: package.json requires Node/npm to determine project checks" >&2; exit 2; }
  HAS_CHECK="$(node -e 'const p=JSON.parse(require("node:fs").readFileSync("package.json","utf8")); process.stdout.write(typeof p.scripts?.check === "string" && p.scripts.check.trim() ? "yes":"no")')"
  if [[ "$HAS_CHECK" == "yes" ]]; then
    echo "[preflight] npm run check"
    npm run check
    CHECKS_RUN=$((CHECKS_RUN + 1))
  else
    echo "[preflight] project npm check: NOT RUN (no nonempty scripts.check)"
  fi
fi

for hook in scripts/project-preflight.sh scripts/project-preflight.command; do
  if [[ -e "$hook" && ! -x "$hook" ]]; then
    echo "BLOCKED: present hook is not executable: $hook" >&2; exit 2
  fi
done
if [[ -x scripts/project-preflight.sh ]]; then
  echo "[preflight] scripts/project-preflight.sh"
  scripts/project-preflight.sh
  CHECKS_RUN=$((CHECKS_RUN + 1))
fi
if [[ -x scripts/project-preflight.command ]]; then
  echo "[preflight] scripts/project-preflight.command"
  scripts/project-preflight.command
  CHECKS_RUN=$((CHECKS_RUN + 1))
fi

if [[ "$CHECKS_RUN" -eq 0 ]]; then
  echo "[preflight] BLOCKED: no project checks ran; configure scripts.check or a project-preflight hook" >&2
  echo "NOTE: use --docs-only only for a verified documentation-only change." >&2
  exit 2
fi
echo "[preflight] PASS: $CHECKS_RUN configured project check command(s) completed"
echo "NOTE: command success does not establish acceptance coverage. Runtime AE, compatibility, release and platform-specific gates remain separate unless project-preflight runs them explicitly."
