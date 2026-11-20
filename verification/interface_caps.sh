#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
root=$PWD
work=$(mktemp -d)
export EXT_TAP_LABELS="$work/pins.tcl" EXT_TAP_GDS="$work/mask.gds"
klayout -b -r verification/interface_geometry.py
cd "$work"
magic -dnull -noconsole -rcfile "$PDK_ROOT/sky130A/libs.tech/magic/sky130A.magicrc" "$root/verification/interface_extract.tcl" >magic.log 2>&1
python3 "$root/verification/interface_caps.py" interface.ext "$root/results/audited"
