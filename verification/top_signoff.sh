#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
root=$PWD
report_dir=${ADC_REPORT_DIR:-$root/results}
mkdir -p "$report_dir"
klayout -b -r verification/check_io.py | tee "$report_dir/top_connectivity.txt"
grep -q '^TRACE SUMMARY 64/64 signal connections; 0 shorted port groups' "$report_dir/top_connectivity.txt"
klayout -b -r verification/top_abstract.py
export ASSEMBLY_GDS="${ADC_IO_GDS:-$root/layout/integration/tt_um_eleva_ccro_adc.gds}"
hash=$(sha256sum "$ASSEMBLY_GDS" | cut -d' ' -f1)
work=$(mktemp -d)
export TILE_PORTS="$work/ports.tcl"
python3 - <<'PY'
import os,re
from pathlib import Path
src=Path("layout/integration/top_floorplan.def").read_text().split("PINS 53 ;")[1].split("END PINS")[0]
rows=re.findall(r"- (\S+) \+ NET [^;]+?\+ PLACED \( (\d+) (\d+) \) N",src)
assert len(rows)==53
with open(os.environ["TILE_PORTS"],"w") as f:
    for i,(name,x,y) in enumerate(rows,1):
        x=int(x)/1000
        y=100 if name in ("VDPWR","VGND") else int(y)/1000
        f.write(f"box values {x}um {y}um {x}um {y}um\nlabel {{{name}}} c metal4\nport {{{name}}} make {i}\n")
PY
cd "$work"
cat "$root/analog/adc_analog_physical_lvs.spice" "$root/layout/readout/adc_readout.gds.spice" "$root/analog/top.spice" >ref.spice
magic -dnull -noconsole -rcfile "$PDK_ROOT/sky130A/libs.tech/magic/sky130A.magicrc" "$root/verification/top_extract.tcl" > magic.log 2>&1
test -s tile_mask.spice
grep '^ANTENNA_FEEDBACK' magic.log | tee "$report_dir/top_antenna.txt"
if [[ -s antenna_feedback.txt ]]; then cp antenna_feedback.txt "$report_dir/top_antenna_markers.txt"; else echo "No antenna feedback." > "$report_dir/top_antenna_markers.txt"; fi
python3 "$root/verification/primitive_syntax.py" tile_mask.spice ref.spice
python3 "$root/verification/tile_loads.py" tile_mask.ext "$report_dir"
netgen -batch lvs 'tile_mask.spice tile_mask' 'ref.spice tt_um_eleva_ccro_adc' "$PDK_ROOT/sky130A/libs.tech/netgen/sky130A_setup.tcl" lvs.txt >netgen.log 2>&1
cp lvs.txt "$report_dir/top_lvs.txt"
tail -10 lvs.txt
grep -q 'Circuits match uniquely' lvs.txt
if grep -qi 'property errors' lvs.txt; then exit 1; fi
grep -q '^ANTENNA_FEEDBACK 0' magic.log
test "$hash" = "$(sha256sum "$ASSEMBLY_GDS" | cut -d' ' -f1)"
echo "$hash" > "$report_dir/top_signoff.sha256"
