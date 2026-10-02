#!/bin/zsh
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <artifact> <NEW_EVIDENCE_DIR>" >&2
  echo "Legacy distribution-policy arguments are unsupported; migrate the caller." >&2
  exit 2
fi

TARGET="$1"
EVIDENCE_DIR="$2"
SCRIPT_DIR="${0:A:h}"

# Record before verification; never reuse a destination or alter the payload.
node "$SCRIPT_DIR/record-artifact.mjs" "$TARGET" "$EVIDENCE_DIR"
node "$SCRIPT_DIR/verify-artifact.mjs" "$TARGET" "$EVIDENCE_DIR/artifact-record.json"
echo "PASS: recorded artifact integrity only."
echo "host_load=NOT_RUN"
echo "installation=NOT_RUN"
echo "NOTE: selected-channel download, documented installation and actual host load require separate evidence."
