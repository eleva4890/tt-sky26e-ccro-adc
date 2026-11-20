#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -n "${ADC_ROUTED_RUN:-}" ]]; then
    cmp layout/readout/adc_readout.gds "$ADC_ROUTED_RUN/results/signoff/adc_readout.gds"
    spef=$(realpath "$ADC_ROUTED_RUN/results/routing/mca/spef")
else
    (cd layout/readout && sha256sum -c spef/SHA256SUMS)
    spef=$(realpath layout/readout/spef)
fi
pdk=$(realpath "$PDK_ROOT/sky130A")
for rc in min nom max; do
    out="results/readout/tile_sta_$rc.log"
    docker run --rm --read-only --network none --env ADC_STA_RC="$rc" \
        -v "$PWD:/design:ro" -v "$pdk:/pdk:ro" -v "$spef:/spef:ro" \
        efabless/openlane:2023.09.07 sta -exit /design/verification/tile_timing.tcl > "$out" 2>&1
    if grep -q '^Error:' "$out"; then tail -16 "$out"; exit 1; fi
    grep -E '^(CORNER |SETUP |HOLD |worst slack)' "$out"
    awk '/^worst slack / {n++; if($3 < 0) exit 1} END {if(n != 2) exit 1}' "$out"
done
