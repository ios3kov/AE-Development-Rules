#!/bin/zsh
set -euo pipefail

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

if [[ -f package.json ]]; then
  command -v node >/dev/null && command -v npm >/dev/null || { echo "BLOCKED: package.json requires Node/npm to determine project checks" >&2; exit 2; }
  HAS_CHECK="$(node -e 'const p=require("./package.json"); process.stdout.write(p.scripts&&p.scripts.check?"yes":"no")')"
  if [[ "$HAS_CHECK" == "yes" ]]; then
    echo "[preflight] npm run check"
    npm run check
  else
    echo "[preflight] package.json has no check script; skipping npm project check"
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
fi

if [[ -x scripts/project-preflight.command ]]; then
  echo "[preflight] scripts/project-preflight.command"
  scripts/project-preflight.command
fi

echo "[preflight] PASS"
echo "NOTE: runtime AE, compatibility, release and platform-specific gates remain separate unless project-preflight runs them explicitly."
