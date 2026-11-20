#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
cd "$root"
svg=${NETLISTSVG:-$(command -v netlistsvg || true)}
if [ -z "$svg" ]; then svg=/tmp/ccro-review-svg/node_modules/.bin/netlistsvg; fi
if [ ! -x "$svg" ]; then
  npm install --prefix /tmp/ccro-review-svg --no-audit --no-fund netlistsvg@1.0.2
fi
python3 review/digital/hierarchy.py
"$svg" review/digital/module_tree.json -o review/digital/module_hierarchy.svg
"$svg" review/digital/pop15.json -o review/digital/pop15.svg
python3 review/digital/svg_background.py review/digital/module_hierarchy.svg review/digital/pop15.svg

