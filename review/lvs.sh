#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
setup="$PDK_ROOT/$PDK/libs.tech/netgen/sky130A_setup.tcl"
cd "$review/netlists"
test "$(sha256sum "$setup" | cut -d' ' -f1)" = 7a33f3f54fab57a9d9b0887ac7b7b64ce6c454110e8b7f01f3cfb90a1282dc94
netgen -batch lvs 'analog_mask.spice eleva_adc_analog' 'xschem.spice adc_analog' "$setup" ../logs/lvs_core.txt -json >../logs/netgen_core.log 2>&1
python3 "$review/digital/spice.py" > ../logs/digital_binding.log
cat digital_reference.spice xschem_tile.spice >tile_reference.spice
netgen -batch lvs 'tile_mask.spice tile_mask' 'tile_reference.spice tt_um_eleva_ccro_adc' "$setup" ../logs/lvs_tile.txt -json >../logs/netgen_tile.log 2>&1

