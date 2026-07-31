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
"$PYTHON_CMD" -m examples.scripts.lab04_retained_metadata.step_01_connect_topics "$@"
"$PYTHON_CMD" -m examples.scripts.lab04_retained_metadata.step_02_read_validate "$@"
echo "Lab 04 summary: all steps passed."