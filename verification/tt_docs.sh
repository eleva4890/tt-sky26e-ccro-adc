#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH="${TT_TOOLS:?Set TT_TOOLS}" "${PRECHECK_PYTHON:-python3}" - <<'PY'
from project_checks import check_project_docs
check_project_docs(".", "sky130A")
print("SKY26e info.yaml and docs/info.md accepted by tt-support-tools")
PY
