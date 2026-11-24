# Final-mask review

**Both LVS comparisons matched uniquely. All 572 RTL-to-routed equivalence checks passed.** The input was `gds/tt_um_eleva_ccro_adc.gds` from the Issue #1 submission revision. Its SHA-256 is `cbd199e4c27bd935dadd77fba74fee3222b007abc97d0b8967c3100e1abd0286`. [Verdict](logs/verdict.txt) · [Input hashes](logs/input_hashes.txt)

## Open the review

From the repository root on Windows, use WSLg with Ubuntu 24.04 and the review PDK installed.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\review\open.ps1
```

The launcher checks the mask and evidence hashes, then opens the tile schematic in Xschem, the final mask and 17 coordinate markers in KLayout, and the evidence index in a browser. PowerShell prints the verdict. [Offline index](index.html)

| Boundary | Matched | Evidence |
|---|---|---|
| Analog macro | 616 devices, 214 nets, 36 pins; zero property errors | [Netgen text](logs/lvs_core.txt) · [JSON](logs/lvs_core.json) |
| Full tile | 10,390 devices, 5,137 nets, 53 pins; zero property errors | [Netgen text](logs/lvs_tile.txt) · [JSON](logs/lvs_tile.json) |
| Digital readout | 235 flip-flops and four latches paired; 572 proven, zero unproven | [Yosys log](logs/formal_equivalence.log) · [State correspondence](digital/state_mapping.tsv) |
| Interconnect | 64/64 external and phase-tap connections; zero shorted external-port groups | [Probe table](klayout_checklist.md) · [Connectivity log](logs/connectivity.log) |

The last line of each LVS report is `Circuits match uniquely.` Device totals follow the official deck’s series/parallel reductions. Parameter comparisons use that deck’s property definitions and tolerances.

## Walk from schematic to mask

1. Select `Xana` in Xschem and press **e** to descend. **Ctrl+e** returns to the parent. Follow `vinp/vinn`, `sp/sn`, `mid` and `rp/rn` through `front`. Open `bias → beta_ref` for the reference and startup transistors or `tail → units4/15/20` for the selectable current sources. [Tile](xschem/tt_um_eleva_ccro_adc.sch) · [Input stage](xschem/front.sch) · [Reference](xschem/beta_ref.sch)
2. Descend through `dual → ring → bank → stage`. Each bank has 15 active stages and one dummy. Inspect the main inverters, weaker cross-couplers and MIM loads. The CVSL receiver shifts the tap to the digital supply. Matching net labels connect across each sheet. [Delay stage](xschem/stage.sch) · [Level shifter](xschem/cvsl.sch)
3. Double-click a KLayout marker to locate its conductor. Each analog pad and its macro pin reach the same extracted cluster. At four vertical positions the central met4 stripe, X = 92.800 µm, connects to tile ground. [Coordinates and layers](klayout_checklist.md)
4. `Xdig` is the 50-pin boundary of the digital macro. The hierarchy figure shows instances per parent; the popcount drawing shows the actual connections of 11 full adders. [Hierarchy](digital/module_hierarchy.svg) · [Popcount](digital/pop15.svg)

## What each comparison proves

Xschem netlisted 17 editable sheets with at most 20 devices or child blocks each. MOSFETs, high-resistance poly, MIM capacitors and protection diodes use SKY130 device symbols. The tile also uses the PDK tie-cell symbol. No raw analog SPICE is embedded. The digital transistor reference binds 2,187 named routed-Verilog instances to 71 PDK cell masters, including decaps, antenna diodes, taps and fillers. [Xschem analog SPICE](netlists/xschem.spice) · [Tile SPICE](netlists/xschem_tile.spice) · [Digital binding](logs/digital_binding.log)

Magic independently extracted the analog macro and the flattened tile from the same released GDS using `ext2spice lvs`. The flat extraction restores the 53 top-level GDS labels at their original coordinates. The installed Netgen setup was byte-identical to the published Ciel deck at revision `8afc8346a57fe1ab7934ba5a6056ea8b43078e71`. [Macro extraction](logs/magic_core.log) · [Tile extraction](logs/magic_tile.log) · [Deck provenance](logs/deck_provenance.txt)

Magic recorded 2,214 extraction warnings. All 2,160 missing-terminal warnings lie inside decap cells. Of 54 device-boundary warnings, 52 overlap antenna-diode cell boxes and two lie at the tile input-protection devices, where LI1 traces to `ui_in[3]` and `ui_in[4]`. The GDS import also reported three redefinitions of the analog cell boundary. [Warning breakdown](logs/magic_warnings.txt) · [Original markers](logs/magic_extraction_feedback.tcl.gz)

Yosys independently elaborated the behavioral RTL and routed gate netlist. For arbitrary shared binary inputs and corresponding prior state, the proof compares effective next data, clocks, latch gates, asynchronous resets and every output bit. Edge polarity, reset polarity and reset value also agree. Non-reset registers can start in any paired binary state. This establishes event-by-event correspondence; silicon metastability, propagation delay and analog SNDR require separate measurements. The clock-gate model preserves the PDK’s low-transparent latch and checks its UDP truth table. Other functional cells use TT Liberty. [Model](digital/clock_model.py) · [State proof](digital/prove.py) · [Yosys commands](digital/equivalence.ys)

Changing an A-side ring PMOS from 8.4 to 12.6 µm caused a Netgen property error. Inverting routed SDO caused `equiv_status -assert` to fail. Both defects were introduced in temporary copies. [LVS control](logs/control_lvs.txt) · [Formal control](logs/control_formal.txt)

## Repeat the checks

```bash
bash review/verify.sh
```

The repository includes the pinned ZIP under `release/`. The verifier reads the saved schematics; running `make_sheets.py` explicitly regenerates them. The tested environment used Xschem 3.4.4, Magic 8.3.684, Netgen 1.5.133, Yosys 0.33, NetlistSVG 1.0.2, KLayout 0.28.16, Python 3 and Xvfb. Set `REVIEW_PDK_ROOT` to the review PDK root and `NETLISTSVG` to a local executable if needed. [Xschem GUI check](logs/xschem_gui.log) · [KLayout GUI check](logs/klayout_gui.log)
