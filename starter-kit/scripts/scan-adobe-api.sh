#!/bin/zsh
set -euo pipefail
command -v node >/dev/null || { echo "BLOCKED: Node.js required" >&2; exit 2; }
SCRIPT_DIR="${0:A:h}"
exec node "$SCRIPT_DIR/scan-adobe-api.mjs" "$@"
