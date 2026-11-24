# SKY26e physical signoff and reproduction

The submitted top cell is `tt_um_eleva_ccro_adc`. It integrates one analog macro, one routed digital readout, 34 external digital/tile signals and 30 phase taps in the connectivity test. The GitHub GDS workflow packages the tile through the SKY26e custom-GDS action. Its precheck job consumes that artifact. The project's GitHub run ID and shuttle acceptance are assigned by those services.

## Toolchain and inputs

Use the SKY130A manufacturing PDK at `6d4d11780c40b20ee63cc98e645307a9bf2b2ab8` and Tiny Tapeout support tools at `7d2d2ef5261eb1df16d0bc342834d48a8a276881`. Set `PDK_ROOT` to the parent of `sky130A/`, `TT_TOOLS` to the support-tools checkout, and `PRECHECK_PYTHON` to a Python with the official precheck dependencies. Put Magic, KLayout, Netgen and yowasp-yosys on PATH.

```bash
bash verification/finalize_tile.sh
bash verification/top_signoff.sh
bash verification/io_drc.sh
bash verification/precheck.sh
bash verification/tt_docs.sh
bash verification/final_analog.sh
bash verification/interface_caps.sh
bash verification/tile_timing.sh
```

Final routing starts with the power/tap assembly. It adds external connections, adjusts via metal dimensions, protects two bias controls with diodes and moves 64 MIM bottom-plate feeds. Top signoff checks external continuity, LEF, flattened LVS, antenna and lumped I/O RC. The LVS reference uses the extraction deck's native two-terminal device syntax. Timing uses routed digital SPEF, lumped tile loads and OpenSTA from `efabless/openlane:2023.09.07`.

## Electrical characterization

### Issue 1 mask revision

The revised tile encloses the four low-Vt implant regions by 0.45 µm at their upper and lower edges. KLayout polygon XOR against the archived mask identified eight additions on N-well (64/20), totaling 10.36 µm², with 32 connected well regions before and after. All other polygon layers matched. A clean tile rebuild produced the same tile and macro hashes. [Issue #1](https://github.com/eleva4890/tt-sky26e-ccro-adc/issues/1) · [Rebuilt masks](../results/rebuilt_masks.sha256)

The official lvtn.10 deck reported eight violations on the archive and zero on the revision. All 17 official prechecks passed. Both Xschem-to-GDS LVS comparisons matched uniquely with zero property errors. [Precheck results](../results/top_precheck.md) · [Independent review](../review/SUMMARY.md)

At TT, 27 °C, 1.8 V and 0.63 V input common mode, a 1 µs power ramp started both loaded rings at 3.769 MHz with zero differential input. Average analog supply current was 43.56 µA. At 50 kHz and 0.20 V differential peak, the extracted and loaded simulation yielded HD2 of −89.90 dBc and HD3 of −63.40 dBc (limit −62 dBc). The broader PVT and torture-test results in the frozen archive characterize the original mask. [Startup](../results/audited/issue1_startup.csv) · [Harmonics](../results/audited/final_loaded_dynamic.csv)

Use ngspice with the model PDK `8afc8346a57fe1ab7934ba5a6056ea8b43078e71`, NumPy under `SIM_PYTHON`, Icarus Verilog and the PDK standard-cell models. Configure `IVL_DIR` if needed.

```bash
GATE_NETLIST=layout/readout/adc_readout.nl.v bash verification/test.sh
bash verification/final_performance.sh
python3 verification/release_gate.py
```

The `results/audited/final_*` records use the extracted analog macro with 5 fF receiver load per tap. `final_loaded_*` adds top-level ground and mutual capacitances. Board, package, distributed analog interconnect resistance and silicon oscillator jitter need separate evaluation. The input mismatch run combines the PDK mismatch model with the standalone ring transfer. [Verification results](../docs/verification_status.md)

To reproduce historical packaging and its original document hashes, expand the frozen submission ZIP in a separate directory, run `sha256sum -c SHA256SUMS`, and use its included packaging procedures. In this English checkout the root README documents the publication checksums. [Final GDS](../gds/tt_um_eleva_ccro_adc.gds) · [LEF](../lef/tt_um_eleva_ccro_adc.lef)
