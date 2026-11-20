# SKY26e differential CCRO ADC

A 1×2-tile analog-to-digital converter for Tiny Tapeout SKY26e, built in SKY130A. Two 15-stage cross-coupled ring oscillators (CCROs) turn a differential input voltage into a frequency difference. The digital readout counts transitions across 30 phase taps, decimates the difference with a second-order CIC filter and transmits a signed 16-bit word over SPI.

The design team used **GPT-6.2 Astra + Codex** to design the circuit. **Claude 5.5 Opus, Gemini 4 Neon and human contributors** participated in specification development and design review.

## Prototype operating point

| Parameter | Value |
|---|---|
| Top cell and die area allocated to the tile | `tt_um_eleva_ccro_adc`, 161.00 × 225.76 µm |
| Nominal supply and input common mode | 1.80 V and 0.63 V |
| Differential input range | ±0.20 V peak |
| Sample clock and output rate | 20 MHz; 156.25 kS/s at OSR 128, 78.125 kS/s at OSR 256 |
| Third harmonic | −62.64 dBc in the loaded, extracted circuit at TT, 27 °C and 50 kHz. Design limit −62 dBc |
| First-silicon measurements | SNDR, sensitivity near the measured offset, and die-to-die spread |

For a first capture, select nominal bias and OSR 128 with `ui_in = 0`. Read `uio[0]` on the 16 rising edges of `uio[2]` while `uio[1]` is low. The datasheet gives wiring and startup instructions. The 29-page report gives the signoff decision on pages 1–2, the datasheet on pages 3–8, circuit and layout details on pages 9–13, and verification evidence on pages 14–19. Pages 20–24 cover the ETR v3.2 (RP2350B) and Analog Discovery 2 bench setup, capture and next-revision criteria. Full Xschem drawings and the evidence index occupy pages 25–29. The separate nine-page tutorial follows one input through to a signed SPI word. [Tiny Tapeout datasheet source](docs/info.md) · [Design and bench report](docs/ccro_adc_design_report.pdf) · [Operating-principles tutorial](docs/tutorial.pdf)

## Explore the design

| Material | What to look for |
|---|---|
| [GDS](gds/tt_um_eleva_ccro_adc.gds) · [LEF](lef/tt_um_eleva_ccro_adc.lef) · [Verilog interface](src/project.v) | The 53-terminal tile used by the SKY26e custom-GDS workflow |
| [Xschem top sheet](review/xschem/tt_um_eleva_ccro_adc.sch) · [KLayout probe coordinates](review/klayout_checklist.md) | Split-tail input stage, reference startup, ring supplies and level shifters |
| [RTL](rtl/adc_readout.v) · [Routed gates](layout/readout/adc_readout.nl.v) · [Module hierarchy](review/digital/module_hierarchy.svg) | Transition counting, CIC decimation, SPI and debug outputs |
| [Signoff results](docs/verification_status.md) · [Independent review](review/SUMMARY.md) | 15/15 prechecks passed. Tile LVS matched 10,390 devices, 5,137 nets and 53 pins, with zero property errors. All 572 digital equivalence checks passed. |
| [Stress tests T1–T6](docs/torture_T1-T6.md) | Startup, power recovery and overload recovery passed. Supply injection was conditional. The small-signal locking margin and live OSR-change deadline were missed. |
| [SPI spectrum](results/design_report/spectra/T3_fft_bins.csv) · [Noise-model spectrum](results/design_report/spectra/A5_fft_bins.csv) | Frequency bins from a 16-frame routed-gate capture and a separate long behavioral noise run |

Run the analog testbench interactively with Xschem and ngspice. It displays startup and both ring outputs and measures the signed frequency difference and supply current. [Open the manual simulation guide](review/bench/README.md)

## Reproduce the checks

From the repository root, verify the release files and review evidence. The publication manifest covers the staged repository files, including the frozen ZIP. The ZIP includes the original Japanese records, historical report generators and its own manifest. [Rebuild the English report](verification/design_report/README.md)

```bash
sha256sum --check --quiet release/SHA256SUMS
(cd review && sha256sum --check --quiet logs/review_files.sha256)
```

On Windows with the documented WSLg and SKY130A environment, open Xschem, KLayout and the log index together.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\review\open.ps1
```

Run `bash review/verify.sh` to repeat extraction, LVS, formal equivalence, connectivity and negative controls. The review guide specifies the tool versions, proof assumptions and extraction warnings. [Review guide](review/SUMMARY.md) · [Physical signoff procedure](verification/RELEASE.md)

## Shuttle files and license

The final GDS SHA-256 is `3d8a8502549ad4229debe27ae7c428059759af6e9657fcf2ff3c616e27a74d25`. To reproduce the historical submission packaging, extract the frozen archive into a separate working directory. [Frozen submission ZIP](release/SKY26e_CCRO_ADC_1x2_Submission_T1-T6.zip) · [Checksums](release/SHA256SUMS)

The GitHub workflows package the custom mask, run the shuttle precheck and build the Tiny Tapeout datasheet. [Local shuttle format check](docs/shuttle_format_check.md) [GDS and precheck workflow](.github/workflows/gds.yaml) · [Datasheet workflow](.github/workflows/docs.yaml)

The original circuit design, RTL, verification code and design documentation are licensed under Apache-2.0. The SKY130 standard cells and Tiny Tapeout DEF template carry their upstream attribution. [Project license](LICENSE) · [Third-party notices](NOTICE) · [Third-party license](LICENSE.third-party)
