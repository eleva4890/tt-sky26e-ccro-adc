# SKY26e custom-GDS format check

The local check uses the files selected by the GitHub workflow. The top cell is `tt_um_eleva_ccro_adc`. The GDS SHA-256 is `cbd199e4c27bd935dadd77fba74fee3222b007abc97d0b8967c3100e1abd0286`.

| Check | Result |
|---|---|
| Project metadata | The pinned support tools accepted `info.yaml` and `docs/info.md`. SKY130A analog, 1×2 tiles, 20 MHz, two analog inputs at ua[0] and ua[1], VDPWR and VGND. |
| Three physical inputs | The action copies the GDS from `gds/`, the matching abstract from `lef/` and the Verilog interface from `src/project.v` to the same top-cell basename in `tt_submission/`. The LEF and GDS pin and boundary checks passed. |
| Official precheck | All 17 checks passed, including Magic DRC, FEOL, BEOL, pin locations, template boundary, supply pins, allowed layers, analog pins and Verilog syntax. [Full checklist](../results/top_precheck.md) |
| OASIS | For the original mask, the action's KLayout 0.29.12 `strm2oas` converted the final GDS. All 41 layer/datatype pairs had empty geometry XOR. All 74 cell names, the 161.00 × 225.76 µm boundary and 14,552 distinct placed text labels matched. The transfer coalesces coincident duplicate objects. Strict multiplicities differ; `strmcmp -1` matched. |
| Official datasheet | `tt_tool.py --check-docs` passed. `--create-pdf` built three pages with Pandoc 3.6.4 and Typst 0.13.1. The local test supplied a reserved example.invalid URL in a temporary Git repository because the official renderer requires a Git remote. The hosted action supplies the eventual repository URL. |
| Independent review from the Git index | Re-extracted both LVS boundaries. Core and tile uniquely matched with zero property errors. Proved 572/572 RTL-to-routed obligations and checked 64/64 signal paths, 17 GUI sheets, 17 physical markers and both intentional-failure controls. [Review verdict](../review/logs/verdict.txt) |
| Distribution contents | The upstream artifact includes `info.yaml`, root `LICENSE`, `docs/*` and `tt_submission/*`. The project workflow also copies the third-party notice and license into the artifact. The root project license is Apache-2.0. [License](../LICENSE) · [Notice](../NOTICE) |
| Hosted milestones | GitHub Actions supplies the real repository URL, commit ID and workflow run URL. Publication, a hosted run and shuttle acceptance follow the first commit. |

The tag `ttsky26e` resolved to `395eedb3eeec3c2f4961c3b04ff2cf87f5525636`. The workflow pins support tools to `7d2d2ef5261eb1df16d0bc342834d48a8a276881`. The physical check used manufacturing PDK `6d4d11780c40b20ee63cc98e645307a9bf2b2ab8`. [SKY130A analog specification](https://tinytapeout.com/specs/analog/) · [Official packaging action](https://github.com/TinyTapeout/tt-gds-action/blob/395eedb3eeec3c2f4961c3b04ff2cf87f5525636/custom_gds/action.yml) · [Official documentation action](https://github.com/TinyTapeout/tt-gds-action/blob/395eedb3eeec3c2f4961c3b04ff2cf87f5525636/docs/action.yml)

## Repeat the checks locally

Use a physical-check environment with the release PDK and the dependencies of the pinned precheck. Create a fresh staging directory to give Verilog, LEF and GDS their artifact names. The support tools write reports under their precheck working directory.

```bash
top=tt_um_eleva_ccro_adc
stage=$(mktemp -d)
cp info.yaml "$stage/"
cp "gds/$top.gds" "lef/$top.lef" "$stage/"
cp src/project.v "$stage/$top.v"
(cd "$TT_TOOLS/precheck" && "$PRECHECK_PYTHON" precheck.py --gds "$stage/$top.gds")
strm2oas "$stage/$top.gds" "$stage/$top.oas"
strmcmp -1 "$stage/$top.gds" "$stage/$top.oas"
```

To build the official datasheet, check out the pinned support tools at `tt/` in a project checkout that has an origin. With the docs dependencies installed, run these commands from the project root.

```bash
python tt/tt_tool.py --check-docs
python tt/tt_tool.py --create-pdf
```

The independent electrical and formal checks are documented separately. [LVS and equivalence](../review/SUMMARY.md) · [Electrical characterization](verification_status.md)
