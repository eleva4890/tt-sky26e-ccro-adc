#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
export PYTHONDONTWRITEBYTECODE=1
cd "$root"
printf 'Review verification in progress\n' > "$review/logs/verdict.txt"
trap 'printf "Verification failed at line %s. Inspect the step logs.\n" "$LINENO" > "$review/logs/verdict.txt"' ERR
python3 review/inputs.py
bash review/netlist.sh
bash review/extract_core.sh
bash review/extract.sh
klayout -b -r review/audit_warnings.py > /dev/null
bash review/lvs.sh
bash review/formal_start.sh
python3 review/digital/prove.py > review/logs/state_mapping.log
yosys -Q -s review/digital/equivalence.ys > review/logs/formal_equivalence.log
bash review/diagram.sh
klayout -b -r review/layout_points.py > review/logs/connectivity.log
klayout -b -r review/make_checklist.py
bash review/sheet_smoke.sh
xvfb-run -a klayout -z -nc -ne -l "$PDK_ROOT/$PDK/libs.tech/klayout/tech/sky130A.lyp" "$ASSEMBLY_GDS" -m review/probe_points.lyrdb -r review/klayout_smoke.py > review/logs/klayout_gui.log 2>&1
python3 review/negative_controls.py
python3 review/check_results.py

