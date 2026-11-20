# Electrical characterization

Pages 23–27 of the design report use the files below. The sample clock is 20 MHz for code-domain results. Input amplitudes are differential peak amplitudes. The analog macro uses the extracted capacitance deck in `layout/integration/final_analog_c.spice` and the SKY130A simulation model revision `8afc8346a57fe1ab7934ba5a6056ea8b43078e71`.

| Files | Quantity and interpretation |
| --- | --- |
| `pvt.csv`, `pvt_summary.json` | Fifteen TT points isolate temperature or supply. Gain is the symmetric ±160 mV secant of differential frequency. Eight FF, 85 °C, 1.98 V points screen 30 tap frequencies at the two operating endpoints for each bias. All 23 use the released receiver and tap-wire loads. |
| `step_taps.csv`, `step_spi_words.csv`, `step_latency.json` | 2,201 tap snapshots, spaced 50 ns. A 10 ns source step from 0 to +100 mV crosses its midpoint at 34.025 µs. The gate simulation releases reset at clock index 65 plus the recorded offset. Its SPI output is decoded at rising SCLK and time-stamped at the end of CS. The JSON records the first word that stays in a 1% band around the median of the last three words. Four sample-to-decimation alignments are covered per OSR. |
| `ideal_step.csv` | Directed RTL test at all 128 and 256 alignments. Time in clocks from the first capture of an eight-transition step to the rising CS edge of the first exact steady word. |
| `macro_input.csv`, `wire_caps_fF.json` | Per-pin 50 kHz quadrature admittance in the running TT macro using integer-period rectangular windows, reported for two adjacent 40 µs windows and the combined 80 µs record. The separate geometric sum counts explicit capacitors touching a given input, with the opposite terminal fixed. |
| `static_residual.csv` | Eleven TT frequency measurements converted by 2,048 × 30 × (fP − fN) / fs. The endpoint and least-squares residuals use the unrounded output-code estimate. The separate seven-point near-zero curve with routed tap wiring comes from `final_loaded_small.csv`. |
| `model_amplitude.csv`, `model_frequency.csv` | Central A5 transfer, input noise and assumed jitter, reuse of seed 27 across points. Each spectrum retains 32,761 settled output words, a four-term Blackman–Harris window and the output Nyquist band. The analyzer folds harmonics 2–5 and excludes six DC bins. |
| `dc_histogram.csv`, `model_summary.json` | DC distribution at +50 mV, usable analog span, noise-free resolution (6.6σ convention), full-scale-sine dynamic range, sparse linearity and finite-swing T4 common-mode rejection. |

The integrated-circuit pin leakage requires a guarded silicon measurement. The input PMOS TT and FF model files omit gate tunneling through the `igcmod` and `igbmod` selectors. The histogram and FFT model omit injection locking and external pad behavior. Reproduction commands are in `verification/design_report/README.md` in the repository and `analysis/README.md` in the report archive.
