# Source from a review script.
review=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root=$(dirname "$review")
if [ -d /tmp/sky26e-bgr-integration-pdk/sky130A ]; then
  export PDK_ROOT=${REVIEW_PDK_ROOT:-/tmp/sky26e-bgr-integration-pdk}
else
  export PDK_ROOT=${REVIEW_PDK_ROOT:-${PDK_ROOT:?Set REVIEW_PDK_ROOT to the installed Ciel PDK root}}
fi
export PDK=sky130A
export PATH="$HOME/.local/bin:/tmp/sky26e-ccro-tools/usr/bin:$PATH"
export ASSEMBLY_GDS="$review/inputs/tt_um_eleva_ccro_adc.gds"
export TILE_PORTS="$review/inputs/ports.tcl"
export ADC_IO_GDS="$ASSEMBLY_GDS"

