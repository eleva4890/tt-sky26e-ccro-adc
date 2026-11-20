#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
cd "$root"
lib="$PDK_ROOT/$PDK/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
python3 review/digital/clock_model.py
cat >review/digital/prepare.ys <<EOF
read_verilog rtl/adc_readout.v
hierarchy -check -top adc_readout
proc
write_json review/digital/hierarchy.json
flatten
techmap
opt -fast
rename adc_readout gold
design -stash gold
read_liberty -ignore_miss_func -ignore_miss_dir -ignore_miss_data_latch "$lib"
read_verilog review/digital/clock_model.v
read_verilog layout/readout/adc_readout.nl.v
delete adc_readout/t:sky130_fd_sc_hd__fill_* adc_readout/t:sky130_fd_sc_hd__decap_* adc_readout/t:sky130_fd_sc_hd__tapvpwrvgnd_* adc_readout/t:sky130_fd_sc_hd__diode_2
hierarchy -check -top adc_readout
proc
flatten
techmap
opt -fast
rename adc_readout gate
design -copy-from gold gold
write_rtlil review/digital/prepared.il
write_json review/digital/prepared.json
EOF
yosys -Q -l review/logs/formal_prepare.log -s review/digital/prepare.ys >/dev/null

