#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
work=$(mktemp -d)
top=layout/integration/tt_um_eleva_ccro_adc.gds
analog=layout/integration/final_analog.gds
if [[ -n "${ADC_RAW_IO_GDS:-}" ]]; then raw=$ADC_RAW_IO_GDS
else
    raw="$work/io.gds"
    ADC_IO_DEST="$raw" klayout -b -r layout/route_io.py
fi
ADC_SOURCE_GDS="$raw" ADC_OUTPUT_GDS="$work/sized.gds" klayout -b -r layout/finalize_routes.py
ADC_SOURCE_GDS="$work/sized.gds" ADC_OUTPUT_GDS="$work/protected.gds" klayout -b -r layout/bias_antenna.py
ADC_SOURCE_GDS="$work/protected.gds" ADC_OUTPUT_GDS="$work/feeds.gds" klayout -b -r layout/space_mim_feeds.py
ADC_SOURCE_GDS="$work/feeds.gds" ADC_OUTPUT_GDS="$work/tile.gds" ADC_ANALOG_GDS="$work/analog.gds" klayout -b -r layout/enclose_lvtn.py
cp "$work/tile.gds" "$top"
cp "$work/analog.gds" "$analog"
mkdir -p gds
cp "$top" "gds/tt_um_eleva_ccro_adc.gds"
