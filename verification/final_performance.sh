#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
py=${SIM_PYTHON:-python3}
unset ADC_DUAL ADC_TRACE_DIR ADC_INTERFACE_CAPS ADC_TEST_MID_SIDE ADC_STUDY_RAIL_COUPLING
export ADC_RING_CAP_SIDE=21.8 ADC_MID_CAP_SIDE=0 ADC_PAIR_STEP_NS=2 ADC_TRACE_FS=32000000
export ADC_FULL=layout/integration/final_analog_c.spice
r=results/audited
points=(-.20 -.16 -.12 -.08 -.04 0 .04 .08 .12 .16 .20)
"$py" verification/pair.py --cm .63 --vd "${points[@]}" --out "$r/final_tt.csv"
"$py" verification/pair.py --cm .63 --corner ss --vdd 1.62 --vd "${points[@]}" --out "$r/final_ss.csv"
"$py" verification/dynamic.py --step-ns 2 --out "$r/final_dynamic.csv"
"$py" verification/pair.py --cm .63 --vd -.01 -.003 0 .003 .01 --settle 24 --out "$r/final_small.csv"
ADC_PAIR_STEP_NS=8 "$py" verification/pair.py --cm .63 --vd 0 --corner sf --temp -20 --vdd 1.98 --mode 1 --settle 65 --out "$r/final_slow.csv"
for mode in 0 3; do
    name=final_fast
    if [[ "$mode" == 0 ]]; then name=final_ff_nom; fi
    "$py" verification/pair.py --cm .63 --corner ff --temp 85 --vdd 1.98 --mode "$mode" --vd .2 --out "$r/$name.csv"
done
ADC_TRACE_DIR="$r/final_taps" "$py" verification/pair.py --cm .63 --vd .2 -.2 --settle 16 --out "$r/final_mixed.csv"
ADC_TRACE_DIR="$r/final_taps" bash verification/test_mixed.sh > "$r/final_spi.txt"
ADC_RING=analog/osc_extracted.spice "$py" verification/a0.py --out "$r/a0_pvt.csv"
"$py" verification/fit_a0.py "$r/a0_pvt.csv" "$r/a0_pvt_fit.csv"
ADC_RING=analog/osc_extracted.spice "$py" verification/a0.py --corners tt --temps 27 --currents 5.80 6.15 13.85 14.20 --out "$r/a0_mismatch_range.csv"
"$py" verification/mismatch_front.py
"$py" verification/noise_budget.py --transfer final_tt.csv --output final_noise_budget.csv
export ADC_INTERFACE_CAPS="$r/interface_caps.spice"
"$py" verification/pair.py --cm .63 --vd -.01 -.003 -.001 0 .001 .003 .01 --settle 24 --out "$r/final_loaded_small.csv"
"$py" verification/dynamic.py --step-ns 2 --out "$r/final_loaded_dynamic.csv"
"$py" verification/pair.py --cm .63 --corner ff --temp 85 --vdd 1.98 --mode 3 --vd .2 --out "$r/final_loaded_fast.csv"
