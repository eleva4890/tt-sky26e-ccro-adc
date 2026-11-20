#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
root=$PWD
export ANALOG_GDS=${ADC_ANALOG_GDS:-$root/layout/integration/final_analog.gds}
report=${ADC_REPORT_DIR:-$root/results}
work=$(mktemp -d)
cd "$work"
magic -dnull -noconsole -rcfile "$PDK_ROOT/sky130A/libs.tech/magic/sky130A.magicrc" "$root/verification/analog_core.tcl" >magic.log 2>&1
grep -E '^(FULL_DRC|VIOLATION)' magic.log | tee "$report/final_analog_drc.txt"
grep -q '^FULL_DRC_TYPES 0' magic.log
cp "$root/analog/adc_analog_physical_lvs.spice" reference.spice
netgen -batch lvs 'analog.spice eleva_adc_analog' 'reference.spice adc_analog' "$PDK_ROOT/sky130A/libs.tech/netgen/sky130A_setup.tcl" lvs.txt >netgen.log 2>&1
cp lvs.txt "$report/final_analog_lvs.txt"
tail -7 lvs.txt
grep -q 'Circuits match uniquely' lvs.txt
if grep -qi 'property errors' lvs.txt; then exit 1; fi
python3 "$root/verification/cap_audit.py" eleva_adc_analog.ext analog_c.spice "$report/final_analog_matrix.csv" --check
cp analog_c.spice "${ADC_ANALOG_PEX:-$root/layout/integration/final_analog_c.spice}"
