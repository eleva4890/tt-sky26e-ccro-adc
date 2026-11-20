#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$review"
sha256sum --quiet -c logs/review_files.sha256
cat logs/verdict.txt
palette="$PDK_ROOT/sky130A/libs.tech/klayout/tech/sky130A.lyp"
if [[ ${1:-} == --smoke ]]; then
  bash "$review/sheet_smoke.sh"
  xvfb-run -a klayout -z -nc -ne -l "$palette" "$ASSEMBLY_GDS" -m "$review/probe_points.lyrdb" -r "$review/klayout_smoke.py"
  exit
fi
(cd "$review/xschem" && xschem -r --rcfile review.rc tt_um_eleva_ccro_adc.sch) &
schematic_pid=$!
klayout -ne -t -l "$palette" "$ASSEMBLY_GDS" -m "$review/probe_points.lyrdb" &
mask_pid=$!
wait "$schematic_pid"
wait "$mask_pid"

