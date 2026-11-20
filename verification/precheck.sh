#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
project=$PWD
report_dir=${ADC_REPORT_DIR:-$project/results}
mkdir -p "$report_dir"
name=tt_um_eleva_ccro_adc
work=$(mktemp -d)
mkdir -p "$work/tools" "$work/submission"
cp -r "${TT_TOOLS:?Set TT_TOOLS to the checked out support tools}/precheck" "$work/tools/"
ln -s "$TT_TOOLS/tech" "$work/tools/tech"
cp "${ADC_IO_GDS:-layout/integration/$name.gds}" "$work/submission/$name.gds"
cp "layout/integration/$name.lef" "$work/submission/"
cp info.yaml "$work/submission/"
cp src/project.v "$work/submission/$name.v"
cd "$work/tools/precheck"
rc=0
"${PRECHECK_PYTHON:-python3}" precheck.py --gds "$work/submission/$name.gds" > "$work/precheck.log" 2>&1 || rc=$?
if [[ -s reports/results.md ]]; then
    cp reports/results.md "$report_dir/top_precheck.md"
    cat reports/results.md
    if [[ -s reports/drc_beol.xml ]]; then
        python3 "$project/verification/drc_summary.py" reports/drc_beol.xml > "$report_dir/top_beol.txt"
        cp reports/drc_beol.xml "$report_dir/top_beol_markers.xml"
    fi
    if [[ -s reports/magic_drc.txt ]]; then cp reports/magic_drc.txt "$report_dir/top_magic_markers.txt"; fi
else
    tail -30 "$work/precheck.log"
    exit 1
fi
if [[ $rc == 0 ]]; then
    sha256sum "$work/submission/$name.gds" | cut -d' ' -f1 > "$report_dir/top_precheck.sha256"
fi
exit "$rc"
