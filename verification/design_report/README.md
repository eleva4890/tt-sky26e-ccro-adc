# Rebuilding the design and bench report

From the repository root, build the 29-page English PDF from the page-wise Markdown master, the release-gate evidence and the committed figures. Python requires ReportLab, Pillow and svglib (tested with svglib 1.6.0). The renderer defaults to the Bitstream Vera fonts distributed with ReportLab.

```sh
python verification/design_report/report29.py --out docs/ccro_adc_design_report.pdf
python verification/design_report/report29.py --tutorial --out docs/tutorial.pdf
```

Each page starts with its part, section, title, evidence tags and decision. Markdown comments specify tables, figures, schematic drawings and notes. The renderer wraps table cells and fails if content crosses the page frame. The tags identify physical signoff, extracted analog simulation, gate simulation, model estimates and silicon measurements still to be made.

Use the committed spectra, case JSON and figure files to inspect the evidence. Regenerating raw analog plots requires the corresponding waveform cache. KLayout produces the mask views, NumPy and Matplotlib produce the plots, and OpenSTA estimates digital power from post-route activity. The noise-model spectrum and the short, coherent routed-gate spectrum use different conditions. [Waveform guide](waveform_guide.md) · [Report source](report_sections.md) · [Rendered report](../../docs/ccro_adc_design_report.pdf)

The frozen submission includes the original-language records and historical release-packaging programs. Use a separate extraction of that archive when reproducing the historical Japanese package.

## Circuit figures

Pages 9–10 describe the analog connections and link to the full vector Xschem sheets on pages 25–28. Each A3 drawing retains device names, geometry and net labels, with a return link to its circuit description.

The committed SVGs rebuild the PDF without an EDA installation. To regenerate them with Xschem 3.4.4 and the review SKY130A PDK, run from the repository root under Bash:

```bash
source review/env.sh
(cd review/xschem && xvfb-run -a xschem --rcfile review.rc --script ../../verification/design_report/export_schematics.tcl front.sch)
```

The exporter sets a white print background and keeps net labels and conductors teal. [Verified schematics](../../review/xschem)

## Electrical characterization, pages 3–8

Run these commands at the repository root with NumPy and Matplotlib. The two figure reducers read the archived results. The amplitude, frequency and DC calculations repeat the A5 model against the original −1 dBFS reference.

```sh
python verification/design_report/characteristic_curves.py
python verification/design_report/pvt_results.py
python verification/design_report/step_figure.py
```

To repeat the physical measurements, set `PDK_ROOT` to a root containing the SKY130A simulation PDK revision `8afc8346a57fe1ab7934ba5a6056ea8b43078e71`. With ngspice 42, Icarus 12 and Python on PATH, run the following commands in order. Set `IVL_DIR` only if the compiler backend is installed separately.

```sh
python verification/design_report/pvt_characterization.py
python verification/design_report/input_admittance.py
python verification/design_report/latency_pex.py
python verification/design_report/step_spi.py
python verification/design_report/ideal_latency.py
```

The results retain all 23 PEX points, sampled tap words, decoded SPI frames, terminal-current window estimates, sparse transfer residuals, tone metrics and DC bin counts. The AC input measurement excludes the fixture, pad switch and package. Silicon measurements are required for pad leakage and the lock band. [Data tables](../../results/design_report/characterization)

## Operating principles, separate nine-page tutorial

The PDF builder draws the teaching figures as vectors and reconstructs 67 complete post-step words from the archived 30-tap samples. It checks each against its independently decoded routed SPI word. [Tap and word records](../../results/design_report/characterization)

## Final layout, pp. 12–13

The report shows the full tile and five functional detail panels. The companion KLayout atlas retains 19 detailed view windows. The generator reads the final GDS, the routed DEF, the analog PEX netlist and the formal state correspondence. It checks all 2,187 digital placements and writes tile-coordinate boxes for the colored cells to `results/design_report/figures/atlas_index.json`. The analog cell is flattened. The detailed atlas records the layer selections and coordinates for inspection. Cell boxes use micrometres from the tile’s lower left.

With KLayout’s Python module, Matplotlib, Pillow and NumPy installed, run the following command from the repository root. A report bundle uses `python report_source/layout_atlas.py`. The committed figures suffice to typeset the PDF.

```sh
python verification/design_report/layout_atlas.py
python verification/design_report/layout_summary.py
```

Open the final mask with the chapter’s KLayout marker database from the repository root. In the marker browser, choose a figure window, an analog device or a digital register group, then double-click an item. The 485 entries are navigation markers. In the report ZIP use `design/gds/` and `figures/` for the two input paths.

```sh
klayout -ne gds/tt_um_eleva_ccro_adc.gds -m results/design_report/figures/atlas_blocks.lyrdb
```

## Illustrated bench measurements, pp. 20–23

Page 20 identifies the ETR v3.2 (RP2350B) and AD2 connectors and shows the complete harness. Pages 21–23 cover power-up, WaveForms, the first signed code, a continuous FFT record, voltage calibration and safe shutdown. The equipment images are credited on page 20 and in NOTICE. Hardware measurements await first silicon.
