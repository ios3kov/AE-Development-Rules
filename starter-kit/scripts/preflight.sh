#!/bin/zsh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$ROOT" ]] || { echo "ERROR: run inside a Git repository" >&2; exit 1; }
cd "$ROOT"

echo "[preflight] git diff"
git diff --check

if [[ -f package.json ]] && command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
  HAS_CHECK="$(node -e 'const p=require("./package.json"); process.stdout.write(p.scripts&&p.scripts.check?"yes":"no")')"
  if [[ "$HAS_CHECK" == "yes" ]]; then
    echo "[preflight] npm run check"
    npm run check
  else
    echo "[preflight] package.json has no check script; skipping npm project check"
  fi
fi

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
