# First-prototype signoff

The released SKY130A 1×2 tile is `tt_um_eleva_ccro_adc`, 161.00 × 225.76 µm with two analog inputs. Its GDS SHA-256 is `cbd199e4c27bd935dadd77fba74fee3222b007abc97d0b8967c3100e1abd0286`. The updated mask passed the full local precheck. [Issue #1 revision and scope of regression](../verification/RELEASE.md#issue-1-mask-revision) Silicon characterization and shuttle acceptance are separate milestones.

## Physical and digital checks

| Check | Result and evidence |
|---|---|
| Precheck and full DRC | 17/17 passed. Magic DRC and KLayout BEOL DRC each reported zero violations. All 53 terminals matched the template. No met5 was used. [Precheck](../results/top_precheck.md) · [Full DRC](../results/top_drc.txt) |
| Top LVS and antenna | Netgen uniquely matched 10,390 devices and 5,137 nets. Zero antenna violations. [Top LVS](../results/top_lvs.txt) · [Antenna](../results/top_antenna.txt) |
| Connectivity | All 34 external signals and 30 phase taps connected, with zero shorted external-port groups. [Connectivity](../results/top_connectivity.txt) |
| Routed timing | Three corners at 32 MHz with digital SPEF, tile lumped loads and opposite switching on adjacent nets. Worst setup +6.11 ns and hold +0.07 ns. [Tile loads](../results/tile_loads.csv) · [Setup](../results/readout/tile_sta_max.log) · [Hold](../results/readout/tile_sta_min.log) |
| Digital regression | RTL and routed gates each ran 13,800 clocks and 70 frames, covering both rates, ±30,720 codes, reset, wrap and dividers. [Regression](../results/readout/final_functional.txt) |
| Analog through SPI | Replayed all 30 extracted taps through routed gates at 32 MHz. The second and third words at ±0.20 V were +2647, +2647 and -2649, -2649. [SPI trace](../results/audited/final_spi.txt) |

## Harmonics

Nominal bias, Vcm = 0.63 V, ±0.20 V differential, 27 °C. The DC estimate uses a fifth-order Chebyshev fit on 11 points. The dynamic result uses the differential phase trajectory over two periods of a 50 kHz tone.

| Extracted condition | HD2 (limit −66 dBc) | HD3 (limit −62 dBc) |
|---|---:|---:|
| TT, 1.80 V, DC sweep | -78.46 dBc | -63.73 dBc |
| SS, 1.62 V, DC sweep | -75.06 dBc | -82.60 dBc |
| TT, 1.80 V, 50 kHz | -91.18 dBc | -62.97 dBc |
| Same sine with top-level tap coupling | -89.90 dBc | -63.40 dBc |

The first three conditions include a 5 fF receiver load per tap. At TT the HD3 static/dynamic difference is 0.76 dB against a 1 dB bound. The HD2 difference is 12.72 dB. A seventh-order fit to the same samples gives -93.19 dBc. First-lot HD2 acceptance uses the two amplitude limits. The last row adds 3.09–8.11 fF per tap with neighbors stationary and leaves 1.40 dB HD3 margin. [TT](../results/audited/final_tt.csv) · [SS](../results/audited/final_ss.csv) · [Loaded transient](../results/audited/final_loaded_dynamic.csv)

## Characterization limits

| Test | Evidence |
|---|---|
| A0 ring transfer | 189 points spanning TT/SS/FF, −20/27/85 °C and 6.5–13.5 µA. Each corner and temperature was fit independently. [Coefficients](../results/audited/a0_pvt_fit.csv) |
| A1 startup | Autonomous nominal 1 µs ramp. Zero-input mean 3.769 MHz and minimum internal differential swing 1.485 Vpp. The full 1 ms ramp matrix and board startup remain open. |
| A2/A3 speed | Slow bias at SF, −20 °C, 1.98 V reached 103.98 kHz minimum and 50.06–50.17% duty. FF, 85 °C maxima were 4.645 MHz nominal and 7.777 MHz fast, or 7.776 MHz fast with top-level coupling. [Slow](../results/audited/final_slow.csv) · [Fast](../results/audited/final_loaded_fast.csv) |
| A5 noise | At 20 MHz, OSR 128, −1 dBFS, nine model cases gave 60.04–63.12 dB SNDR with 45.33 µV rms front-end noise and assumed ring FoM. Measure oscillator jitter and actual SPI SNDR on silicon. [Noise](../results/audited/front_noise.txt) · [Budget](../results/audited/final_noise_budget.csv) |
| A6 small signal | For −10, −3, −1, 0, +1, +3 and +10 mV, respectively, loaded TT differences were -69.241, -20.768, +0.007, +0.003, +0.001, +20.054, +68.693 kHz. Correct sign at ±10 mV. Near-zero behavior depends on history. [Sweep](../results/audited/final_loaded_small.csv) |
| A7 mismatch | Fifty front-end mismatch draws using a common fitted ring transfer yielded -11.04 to +13.02 mV equivalent offset. 50/50 lay within the characterized current range. Full-circuit HD2 spread and yield remain open. [Draws](../results/audited/front_mismatch.csv) |

The extracted analog model includes the layout devices and mutual capacitances. Core metal is equipotential. Distributed wiring resistance, package parasitics and board supply feedback require additional characterization. Manufacturing PDK `6d4d11780c40b20ee63cc98e645307a9bf2b2ab8`. Analog model PDK `8afc8346a57fe1ab7934ba5a6056ea8b43078e71`. [Capacitance matrix](../results/final_analog_matrix.csv) · [Release gate](../results/release_gate.json) · [Bench manual](ccro_adc_design_report.pdf)
