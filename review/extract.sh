#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
klayout -b -r "$review/mask_ports.py"
scratch=$(mktemp -d)
cd "$scratch"
magic -dnull -noconsole -rcfile "$PDK_ROOT/$PDK/libs.tech/magic/sky130A.magicrc" "$review/tile_extract.tcl" > "$review/logs/magic_tile.log" 2>&1
test -s tile_mask.spice
cp tile_mask.spice "$review/netlists/"
gzip -c extraction_feedback.tcl > "$review/logs/magic_extraction_feedback.tcl.gz"

