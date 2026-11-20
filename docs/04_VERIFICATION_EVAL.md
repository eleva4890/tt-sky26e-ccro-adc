# Verification plan and bench evaluation

The initial plan gated layout on oscillator characterization and digital area. The released mask uses the first-lot acceptance criteria in the specification. Follow the results links for individual pass, conditional and open items. [First-lot specification](01_SPEC.md) · [Signoff record](verification_status.md) · [Stress tests](torture_T1-T6.md)

## Analog and digital coverage

| Test | Stimulus and observable |
|---|---|
| A0 | Sweep standalone oscillator current at 21 points, TT/SS/FF and −20/27/85 °C. Fit f(I), its second and third derivatives, and the rail response. |
| A1 | Start under zero differential input, check both rails and all differential stages. Planned 1 µs and 1 ms ramps. T1 adds identical node voltages; T2 covers a slow-bias 10 ms ramp and nominal-bias brownout. |
| A2/A3 | Check all CVSL swings and 45–55% duty under SF cold slow-bias operation. Check maximum frequency under FF hot, nominal and fast bias against 0.4 fs. |
| A4 | Sweep 11 input voltages under TT and SS, inspect saturation and fit harmonics. Compare with two periods of a 50 kHz sine in TT. Include extracted external tap capacitance. |
| A5 | Integrate input noise, vary oscillator FoM and seed, propagate sampled phases through CIC2. Report modeled and measured SNDR separately. |
| A6/A7 | Probe ±1, ±3 and ±10 mV, both polarities and startup histories. Evaluate input offset across 50 mismatch draws. Measure full-chip spread and near-zero behavior on silicon. |
| D1/D2 | Sweep 0–15 transitions per side, sticky flag at 14, synchronized clear, both OSRs and modular overflow. Compare with an independent CIC oracle. |
| D3 | Verify mode-0 SCLK, MSB first, 16 rising edges, 64-clock active CS and idle outputs. Decode the routed-gate stream. |
| D4 | Enforce 9,000 µm² non-filler cell budget, 100 µm macro height and 32 MHz setup and hold checks. |
| D5/D6 | Check startup with unknown phase history, reset and masking. Decode all four debug modes, including gated /64 clocks. |
| M1/M2 | Drive positive and negative analog DC inputs, replay the extracted phase taps, inspect the first three routed frames and confirm sign. |

## Physical closure

Run the official SKY26e precheck on the custom GDS, LEF and top-level Verilog. Check full DRC, antenna, all 53 terminals, connectivity and tile LVS. Repeat analog LVS from the Xschem source and final GDS, and prove RTL-to-routed equivalence. The review guide records negative controls and the exact properties covered. [Review guide](../review/SUMMARY.md)

## First bench session

1. Identify the board revision. With sources off, connect common ground and place 1 kΩ in series close to each analog pad. Use the board's level-shifted 3.3 V-compatible interface for AD2 digital signals and release any shared microcontroller drivers. Power the tile and verify 1.80 V before enabling the AWG at 0.63 V common mode.
2. Use a clean integer-divided sample clock, for example 120 MHz / 6. Select nominal bias and OSR 128 under reset. Measure each /64 output at zero and at both ends of the differential range. Check fVCO,max ≤0.4 fs, then return to quiet debug mode.
3. Decode positive and negative static words. Bracket each die's zero-code crossing. For a plateau, record its edges and midpoint. Sweep around the measured offset at ±1, ±3 and ±10 mV in both directions with identical dwell times.
4. For low-rate functional capture use slow bias, 1 MHz clock, OSR 128, ≤1 kHz tone and ±35 mV differential peak. Nominal precision evaluation uses 20 MHz, 128× decimation and −1 dBFS. Check generator harmonics at the pins before measuring converter harmonics. A pair of matched 7.50 kΩ/1.07 kΩ dividers referenced to buffered Vcm provides approximately 8:1 attenuation for low-level drive.
5. Record 32,768 consecutive signed words with a logic analyzer or PIO. At 156.25 kS/s an input of 2,099 coherent cycles is approximately 10,008.812 Hz. Use a rectangular window for coherent sampling or document the four-term Blackman–Harris analysis. Save the raw words, actual sample rate, rail voltage, bias, common mode, temperature and source residual. [First-day limits and spectrum definitions](ccro_adc_design_report.pdf) · [SPI receiver](../tools/tt_adc_pio_rx.py) · [Analysis](../tools/analyze_sndr.py)

A clock change can alter timing, but internal hold margin is independent of the clock period. For SPI errors first check receiver timing, pad loading and ground reference. Compare within the permitted supply sweep only where the core rail is independently adjustable. Disable external drive before cutting tile power.
