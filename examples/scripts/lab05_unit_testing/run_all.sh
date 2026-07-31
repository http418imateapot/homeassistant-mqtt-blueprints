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
"$PYTHON_CMD" -m examples.scripts.lab05_unit_testing.step_01_arrange_act_assert
"$PYTHON_CMD" -m examples.scripts.lab05_unit_testing.step_02_run_suite
"$PYTHON_CMD" -m examples.scripts.lab05_unit_testing.step_03_run_single_param
"$PYTHON_CMD" -m examples.scripts.lab05_unit_testing.step_04_read_failure
echo "Lab 05 summary: all steps passed."