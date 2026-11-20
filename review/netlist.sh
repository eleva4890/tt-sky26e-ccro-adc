#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
cd "$review/xschem"
xschem -n -q -x -s --rcfile review.rc --tcl 'xschem set format lvs_format' -o ../netlists -N xschem.spice analog_review.sch >../logs/xschem.log 2>&1
grep -iq '^.subckt adc_analog ' ../netlists/xschem.spice
xschem -n -q -x -s --rcfile review.rc --tcl 'xschem set format lvs_format' -o ../netlists -N xschem_tile.spice tt_um_eleva_ccro_adc.sch >>../logs/xschem.log 2>&1
grep -iq '^.subckt tt_um_eleva_ccro_adc ' ../netlists/xschem_tile.spice

