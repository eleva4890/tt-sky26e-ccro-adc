#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
work=$(mktemp -d)
python3 verification/stimulus.py "$work/vectors.txt"
# Relocatable Debian installations can point IVL_DIR at their lib/.../ivl.
ivl=()
if [[ -n "${IVL_DIR:-}" ]]; then ivl=(-B "$IVL_DIR"); fi
iverilog "${ivl[@]}" -g2012 -s readout_tb -o "$work/rtl" verification/readout_tb.v rtl/adc_readout.v
vvp "$work/rtl" "+DATA=$work/vectors.txt"
iverilog "${ivl[@]}" -g2012 -s divider_tb -o "$work/div" verification/divider_tb.v rtl/adc_readout.v
vvp "$work/div"
if [[ -n "${BUILD_DIR:-}" || -n "${GATE_NETLIST:-}" ]]; then
    lib="$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/verilog"
    gates=${GATE_NETLIST:-"$BUILD_DIR/adc_readout.v"}
    # A nonzero UDP clock-to-Q separates data updates from the delta-cycle
    # clock-buffer tree in functional cell models. Extracted STA checks timing.
    iverilog "${ivl[@]}" -g2012 -DFUNCTIONAL '-DUNIT_DELAY=#0.1' -s readout_tb -o "$work/gates" \
      verification/readout_tb.v "$gates" "$lib/primitives.v" "$lib/sky130_fd_sc_hd.v"
    vvp "$work/gates" "+DATA=$work/vectors.txt"
    iverilog "${ivl[@]}" -g2012 -DFUNCTIONAL '-DUNIT_DELAY=#0.1' -s divider_tb -o "$work/div_gate" \
      verification/divider_tb.v "$gates" "$lib/primitives.v" "$lib/sky130_fd_sc_hd.v"
    vvp "$work/div_gate"
fi
