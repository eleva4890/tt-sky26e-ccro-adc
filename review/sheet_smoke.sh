#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
export SHEET_PREVIEWS=${SHEET_PREVIEWS:-$(mktemp -d)}
cd "$review/xschem"
xvfb-run -a xschem --rcfile review.rc --script "$review/gui_smoke.tcl" adc_analog.sch > "$review/logs/xschem_gui.log" 2>&1
test "$(find "$SHEET_PREVIEWS" -name '*.svg' -size +1k | wc -l)" -eq "$(find . -name '*.sch' | wc -l)"

