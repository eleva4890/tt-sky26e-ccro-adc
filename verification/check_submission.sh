#!/usr/bin/env bash
# Independently rerun the project gates and the official precheck from a clean ZIP extraction.
set -euo pipefail
cd "$(dirname "$0")/.."
root=$PWD
zip=${1:-"$root/../SKY26e_CCRO_ADC_1x2_Submission.zip"}
work=$(mktemp -d)
mkdir "$work/repo" "$work/checks"
unzip -q "$zip" -d "$work/repo"
cd "$work/repo"
sha256sum --quiet -c SHA256SUMS
"${SIM_PYTHON:-python3}" verification/release_gate.py > "$work/gate.log"
cmp results/release_gate.json "$root/results/release_gate.json"
bash verification/tt_docs.sh
export ADC_IO_GDS="$PWD/gds/tt_um_eleva_ccro_adc.gds" ADC_REPORT_DIR="$work/checks"
bash verification/precheck.sh
cmp "$work/checks/top_precheck.sha256" results/top_signoff.sha256
cmp "$work/checks/top_beol.txt" results/top_beol.txt
test "$(grep -c '✅' "$work/checks/top_precheck.md")" -eq 17
sha256sum "$zip"
echo "ZIP manifest, release criteria, documentation and 17/17 official prechecks verified from a clean extraction."
