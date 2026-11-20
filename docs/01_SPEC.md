# Prototype specification

The initial SKY26e release uses a SKY130A 1×2 analog tile with two dedicated analog inputs. Its operating point is 1.80 V, 27 °C, 0.63 V common mode, ±0.20 V differential peak, nominal bias, a 20 MHz clock and OSR 128. Revision 3.1 set the HD3 ceiling to −62 dBc. Revision 3.2 adopted these first-silicon conditions. The original v1–v3 development targets are retained in the frozen release. [Original submission](../release/SKY26e_CCRO_ADC_1x2_Submission_T1-T6.zip)

## Analog conversion

The continuous-time input drives independent-well PMOS gates. The split-tail transconductor steers current into two 15-stage pseudo-differential CCROs. Each ring produces 30 transitions per period across 15 buffered phase taps. Subtracting the observed transition counts rejects common frequency shifts. At the released operating point a positive differential voltage produces a positive word. [Circuit and pin tables](ccro_adc_design_report.pdf)

| Bias bits | Enabled units per side | TT zero-input frequency | Initial sample clock | Differential peak |
|---|---:|---:|---:|---|
| 00 nominal | 20 | 3.769 MHz | 20 MHz | 0.20 V |
| 01 slow | 1 | 0.246 MHz | 1 MHz | 35 mV, functional test |
| 10 intermediate | 5 | 1.072 MHz | 5 MHz | 95 mV, functional test |
| 11 fast | 40 | 6.958 MHz | 32 MHz | 0.20 V, characterize distortion |

Measure both divided frequencies across the input range. Keep the largest ring frequency at or below 0.4 times the sample clock. Above half the sample clock two transitions can cancel in the sampler, including cases where the wrap flag remains clear.

## Readout and interface

Two resetless flops synchronize each tap. XOR with its previous sample and a population count give two values from 0 to 15. Their signed difference ranges from −15 to +15. A four-clock startup mask keeps uninitialized phase history out of the two 21-bit CIC integrators. Two decimated differences cancel integrator initial conditions. The comb slices are bits 18:3 at OSR 128 and 20:5 at OSR 256. Both rates map a steady input of ±15 counts to ±30,720 output codes. At constant analog input and OSR the mean code scales inversely with the sample clock.

One conversion produces a signed two's-complement 16-bit word, MSB first. CS_N stays low for 64 sample clocks. SDO changes in the low SCLK phase and is sampled on the rising edge. A bit takes four sample clocks. At 20 MHz this gives 100 ns nominal setup and hold each. Between words CS_N is high for 64 or 192 clocks at OSR 128 or 256. The serializer drives idle SDO low.

| Terminal | Function |
|---|---|
| VDPWR, VGND, clk, rst_n, ena | Tile rails, sample clock, active-low reset and shuttle selection |
| ua[0], ua[1] | Positive and negative input. Use only the two allocated analog pins. |
| ui_in[0], [2:1], [4:3] | OSR (0 = 128), debug mode and bias select |
| ui_in[5], [7:6] | Synchronized, active-high ERR_CLR (hold ≥3 clocks) and unused bits |
| uo_out[7:0] | Modes 00 and 11 drive zero. Mode 01 exposes P count in the high nibble and N count in the low nibble. Mode 10 exposes P/64 on bit 0 and N/64 on bit 1, with bits 7:2 low. Dividers operate in mode 10. |
| uio[0], [1], [2], [3] | SDO, CS_N, SCLK and sticky WRAP_ERR. An observed count ≥14 on either side latches the warning. |
| uio[7:4], uio_oe | Upper four pins high impedance. Output enable mask is 0x0F. |

Set the bias and OSR under reset. Keep OSR fixed throughout the acquisition and discard the first two frames after reset. Debug modes leave the serial converter running.

## Acceptance for the first lot

| Item | Release criterion or evaluation |
|---|---|
| Physical | All official prechecks pass, zero full DRC and antenna violations, unique tile LVS, signal continuity and routed readout timing |
| Linearity | Static TT and SS, and dynamic TT at 50 kHz. HD2 ≤ −66 dBc and HD3 ≤ −62 dBc. TT static/dynamic HD3 difference ≤1 dB. |
| HD2 estimator | Report each amplitude limit and fit-order sensitivity. TT static/dynamic HD2 differs by 12.72 dB. The early 4 dB agreement target remains a bench question. |
| Small signal | Check polarity at ±10 mV and record the ±3 mV response. Locate each die's actual offset before measuring its dead band. |
| Noise and mismatch | Behavioral simulation goal >60 dB SNDR. First-silicon goal >56 dB at −1 dBFS. Measure oscillator jitter, complete-circuit spread and HD2 distribution on silicon. |
| End-to-end | Replay all 30 extracted taps through routed gates at both polarities and decode the serial words. |

The modeled 1.62–1.98 V characterization corners do not establish absolute maximum ratings. Keep every input between VGND and the instantaneous VDPWR. [First-day procedure and results](ccro_adc_design_report.pdf)

## Pre-silicon electrical characteristics

| Parameter | Typical result | Conditions and limits |
| --- | --- | --- |
| Sample clock | For biases 00 / 01 / 10 / 11, the 2.5× observed-peak screen gives 11.62 / 0.82 / 3.61 / 19.45 MHz | FF, 85 °C, 1.98 V, both endpoints of each mode. Verify shortest tap pulse and both divided outputs in situ. Routed timing checked to 32 MHz. |
| Input step to SPI complete | 17.325–22.125 µs (OSR 128), 31.875–41.475 µs (OSR 256) | TT, 0 to +100 mV, four alignments per rate, 20 MHz, 1% band and final CS rise. |
| Gain and drift | 6.900 MHz/V at 27 °C, 1.8 V. −2.13% at −20 °C and −1.65% at 85 °C. Supply slope −11.07%/V. | TT, ±160 mV two-point calibration at fixed Vcm. Supply sweep at 27 °C. |
| Core current and power | 42.86 µA / 77.16 µW (reset, clk low), 200.61 µA / 361.10 µW (quiet, 20 MHz) | PEX analog plus routed digital power model, nominal 1.8 V, zero input. Excludes pads and board. |
| DC output noise / dynamic range | 1.476 codes rms, 9.77 noise-free bits, 66.15 dB | +50 mV DC, 32,761 settled model words, OSR 128, usable analog span of 8,474 codes. |
| Sampled INL | 4.49 codes endpoint, 3.83 codes least squares | Maximum absolute residual over 11 TT points, ±200 mV, prior to word slicing. |
| Finite common-mode rejection | 43.93 dB at −100 mV differential | T4, 0.48 to 0.78 V common mode. Zero-input small-signal rejection requires silicon characterization. |
| Input capacitance P / N and leakage | 26.5 / 27.0 fF at 50 kHz. Pin DC leakage pending silicon. | Running macro, differential 20 mV peak, fixture excluded. Input model omits gate tunneling. |

For plot conditions, individual operating points and pin scope, see pages 23–27. [Design and bench report](ccro_adc_design_report.pdf) · [Measurement data](../results/design_report/characterization)
