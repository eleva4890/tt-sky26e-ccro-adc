#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
work=$(mktemp -d)
ivl=()
if [[ -n "${IVL_DIR:-}" ]]; then ivl=(-B "$IVL_DIR"); fi
lib="$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/verilog"
iverilog "${ivl[@]}" -g2012 -s mixed_tb -DFUNCTIONAL '-DUNIT_DELAY=#0.1' -o "$work/mixed" \
  verification/mixed_tb.v layout/readout/adc_readout.nl.v "$lib/primitives.v" "$lib/sky130_fd_sc_hd.v"
for polarity in + -; do
  sign=1
  if [[ "$polarity" == "-" ]]; then sign=-1; fi
  vvp "$work/mixed" "+DATA=${ADC_TRACE_DIR:-results/audited/full_taps}/taps_${polarity}0.2000.txt" "+SIGN=$sign"
done
