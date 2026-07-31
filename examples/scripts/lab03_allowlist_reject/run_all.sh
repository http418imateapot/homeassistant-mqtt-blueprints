#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
PYTHON_CMD="${PYTHON:-}"
if [ -z "$PYTHON_CMD" ]; then
  for candidate in python3 python; do
    if "$candidate" -c "pass" >/dev/null 2>&1; then PYTHON_CMD="$candidate"; break; fi
  done
fi
if [ -z "$PYTHON_CMD" ]; then
  echo "No working Python interpreter found; set PYTHON to your interpreter." >&2
  exit 1
fi
"$PYTHON_CMD" -m examples.scripts.lab03_allowlist_reject.step_01_build_scenarios "$@"
"$PYTHON_CMD" -m examples.scripts.lab03_allowlist_reject.step_02_publish_observe "$@"
echo "Lab 03 summary: all steps passed."