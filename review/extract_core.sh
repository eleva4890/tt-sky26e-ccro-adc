#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
cd "$(mktemp -d)"
magic -dnull -noconsole -rcfile "$PDK_ROOT/$PDK/libs.tech/magic/sky130A.magicrc" "$review/analog_extract.tcl" > "$review/logs/magic_core.log" 2>&1
test -s analog_mask.spice
cp analog_mask.spice "$review/netlists/"

