#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
project=$PWD
export ASSEMBLY_CELL=tt_um_eleva_ccro_adc CHANNEL_GDS="$project/${1:-layout/integration/tt_um_eleva_ccro_adc.gds}"
report=${2:-results/top_drc.txt}
work=$(mktemp -d)
cd "$work"
magic -dnull -noconsole -rcfile "$PDK_ROOT/sky130A/libs.tech/magic/sky130A.magicrc" "$project/verification/channel.tcl" >magic.log 2>&1
grep -E '^(FULL_DRC|VIOLATION)' magic.log | tee "$project/$report"
grep -q '^FULL_DRC_TYPES 0' magic.log
