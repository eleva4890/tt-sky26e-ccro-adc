# Waveform data

The separate full-waveform archive stores gzip-compressed CSV files. The source ngspice traces are binary double precision; CSV time and value columns use nine significant digits. Time is in seconds, voltage in volts relative to simulator node 0, and current in amperes. Compute the T3 local rail as `v(vdd) - v(vg)`.

| Record | Signals and interpretation |
|---|---|
| T1 corner and bias | From release of the initial conditions; `xadc.pa0/pb0` are the first P-ring pair. All 60 A/B nodes are present. |
| T2 ramp/reference | 10 ms ramp through 10.1 ms, and 1 µs reference. The waveform index specifies saved intervals; case JSON records solver settings. |
| T2 brown/leak | 50 µs dropout and recovery; direct hot-FF current in the 39 off units and one active unit. |
| T3 clean/dirty/gate | All 30 taps under 5 Ω + 2 nH supply impedance, with and without burst currents. Gate replay captures SPI and decimation phase. |
| T4 step/ideal/series | Overload, common-mode and source-resistance comparisons. The literal-series test places the capacitor in series as well. |
| T5 coupling sweeps | Midpoint flag 0 is the mask, 1 adds a 10 × 10 µm MIM. Numeric suffixes are fF added to the extracted 4.1989 fF. The removed case eliminates only the direct coupling. |
| T5 hold/hold_mid/tracking | Compare startup at zero followed by +1 mV with input tracking the supply. Long-window phase is measured over 18–178 µs. Record timestep as well as history. |
| T6 | Digital tick, reset, modes, SPI and transition counts. Compare frame contents and completion latency independently. |

The per-case JSON and SPICE decks are in this repository. The large continuous analog traces are distributed separately. [Case records](../../results/torture) · [Decks](../../decks) · [Spectra](../../results/design_report/spectra)
