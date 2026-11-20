#!/usr/bin/env bash
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
source "$here/../env.sh"
cd "$here"
case "${1:-}" in
  '') exec xschem -r --rcfile xschemrc tb_ccro.sch ;;
  --batch)
    export CCRO_RUN_DIR
    CCRO_RUN_DIR=$(mktemp -d /tmp/ccro-adc.XXXXXXXX)
    xschem -n -q -x -s --rcfile xschemrc -o "$CCRO_RUN_DIR" tb_ccro.sch
    cd "$CCRO_RUN_DIR"
    python3 "$here/simulate.py" tb_ccro.spice
    printf 'Waveforms and log: %s\n' "$CCRO_RUN_DIR"
    ;;
  *) echo 'Usage: bash review/bench/open.sh [--batch]' >&2; exit 2 ;;
esac
