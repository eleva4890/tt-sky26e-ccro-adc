# Stress-test measurements on the released mask

The analog results use extracted devices and capacitances. Digital results use RTL and the routed functional gate model. The supplied raw records retain their original numerical settings. [Case records](../results/torture) · [Waveform guide](../verification/design_report/waveform_guide.md)

| Test | Verdict |
|---|---|
| T1 | PASS |
| T2 | PASS |
| T3 | Conditional |
| T4 | PASS |
| T5 | FAIL |
| T6 | FAIL |

## T1. Equal-node startup

All 60 internal nodes started at 0.35 V without a kick, at 1.8 V and 27 °C with zero differential input. Each stage had to span 20–80% of its ring rail, settle at 180° ±15° and remain within 15% of the final period. The time below includes two consecutive qualifying periods. The cross-coupled devices are one fifth of the main inverter width. These ten runs include extracted asymmetry.

| Corner | Bias | Maximum initial error (V) | Stages passing / 30 | Latest confirmation (periods) | Final phase error |
|---|---|---:|---:|---:|---:|
| TT | 00 | 5.55e-17 | 30 | 3.09 | 0.31° |
| TT | 01 | 5.55e-17 | 30 | 3.08 | 0.34° |
| SS | 00 | 6.11e-16 | 30 | 3.26 | 0.31° |
| SS | 01 | 5.55e-17 | 30 | 3.16 | 0.62° |
| FF | 00 | 5.55e-17 | 30 | 3.31 | 0.39° |
| FF | 01 | 2.22e-16 | 30 | 3.04 | 0.41° |
| SF | 00 | 5.55e-17 | 30 | 3.19 | 0.17° |
| SF | 01 | 5.55e-17 | 30 | 3.07 | 0.35° |
| FS | 00 | 5.55e-17 | 30 | 3.42 | 0.41° |
| FS | 01 | 5.55e-17 | 30 | 3.22 | 0.92° |

## T2. Power ramp, brownout and leakage

TT, 27 °C. The slow setting saw a 10 ms ramp to 1.8 V. The nominal setting saw a 50 µs hold at 0.6 V followed by a 10 ns recovery. Criteria were >1.5 Vpp on all taps and frequency and bias within 5% of the control.

| Condition | P (MHz) | N (MHz) | vb (V) | Minimum tap swing (Vpp) |
|---|---:|---:|---:|---:|
| 1 µs slow control | 0.24645 | 0.24644 | 0.68261 | 1.804 |
| 10 ms slow ramp | 0.24716 | 0.24718 | 0.68261 | 1.804 |
| Before dropout | 3.76876 | 3.76904 | 0.68262 | 1.813 |
| During dropout | 0.00000 | 0.00000 | 0.00010 | 0.000 |
| After recovery | 3.76873 | 3.76875 | 0.68262 | 1.812 |

Maximum ramp/control frequency or bias difference was 0.302%. The 10.1 ms extracted run used a maximum 50 ns step and reltol 0.003. Its 1 µs control was cross-checked at reltol 0.0005. At FF, 85 °C, 1.98 V, per-device current probes measured the signed mean over whole ring periods. Both the 25 nA and 5% limits apply.

| Bank | Sum of 39 off units (nA) | One on unit (nA) | Ratio |
|---|---:|---:|---:|
| P | 0.057 | 465.54 | 0.012% |
| N | 0.057 | 465.54 | 0.012% |

## T3. Simultaneous supply injection

Each rail included 5 Ω and 2 nH. Two 1 mA square waves ran at 20 MHz and 156.25 kHz. Input was 19.53125 kHz at −1 dBFS, sample rate 20 MHz, OSR 128. Local swing rose from 1.92 to 32.02 mVpp. At the 25 ns sample phase the coherent 16-word SNDR loss was 0.83 dB.

Eight relative phases covered 0–43.75 ns. Minimum injected SNDR was 64.26 dB and maximum paired loss was 3.267 dB. Adding the paired disturbance power to a 54 dB reference budget gave a worst loss of 0.536 dB against a 3 dB limit. These two comparisons yield different verdicts.

Routed SPI yielded 66.71 dB clean and 64.58 dB injected. The oracle matched over 2688 clocks per run. The first sticky flags occurred at ticks [12, 12]. From tick 512 the peak counts were [8, 8] against a threshold of 14.

| Rail modulation frequency (MHz) | Clean (Hz) | Injected (Hz) | Injected (dBc) |
|---:|---:|---:|---:|
| 0.0195312 | 1233622.7 | 1233384.2 | 0.00 |
| 0.15625 | 1316.9 | 78.4 | -83.94 |
| 20 | 2092.2 | 1777.8 | -56.82 |
| 19.8438 | 3092.7 | 1542.8 | -58.06 |
| 20.1562 | 2519.6 | 1140.8 | -60.68 |

For subharmonics 1/4 through 1/8 of 20 MHz and harmonics 16–33 of the output rate, the minimum excursion was 11.38 cycles over 102.4 µs. This rules out continuous locking at those ratios over that window. The short coherent record resolves spurs; device-noise SNDR requires a long silicon capture.

## T4. Overload, common-mode shift and input loading

After ±0.6 V differential overload the input returned to ±0.1 V. The slowest taps returned to within 5% of their final period after 0.99 and 1.01 periods. Limit 2 periods.

| Interval | P (MHz) | N (MHz) | Minimum swing (Vpp) |
|---|---:|---:|---:|
| +0.6 V | 5.6900 | 1.6583 | 1.810 |
| +0.1 V recovery | 4.1110 | 3.4204 | 1.814 |
| −0.6 V | 1.6587 | 5.6909 | 1.809 |
| −0.1 V recovery | 3.4201 | 4.1112 | 1.813 |
| Vcm 0.48 V | 3.4332 | 4.1147 | 1.813 |
| Vcm 0.78 V | 3.4067 | 4.1014 | 1.814 |
| Vcm 0.63 V recovery | 3.4201 | 4.1113 | 1.813 |

At TT, 27 °C, 50 kHz and ±0.20 V, 10 pF shunt per pin with 0 and 1.5 kΩ series resistance gave HD3 -63.297 and -63.753 dBc. Change -0.456 dB. A second test put the capacitor in series and added a 100 MΩ DC return to 0.63 V per pin. HD3 was -63.841 and -65.148 dBc. The linear input network omits voltage-dependent switch resistance.

## T5. Direct coupling and the 1 mV lock band

Direct extracted rail coupling is 4.1989 fF. The mask has no added midpoint capacitor. The comparison adds a 10 × 10 µm, 206.58 fF MIM to ground. For startup at +1 mV, a response below 10% of 6.9 kHz/mV in the full 13–25 µs window and both halves indicates lock-like behavior.

| Direct coupling change | Total fF | No midpoint MIM (kHz) | With MIM (kHz) | Lock-like, without / with |
|---|---:|---:|---:|---|
| Remove extracted capacitor | 0.0000 | +5.2367 | +5.7432 | False / False |
| +0 fF | 4.1989 | +5.3751 | +5.6237 | False / False |
| +1 fF | 5.1989 | +5.5293 | +5.2899 | False / False |
| +5 fF | 9.1989 | +5.5327 | +5.3567 | False / False |
| +20 fF | 24.1989 | +5.4166 | +5.3295 | False / False |
| +50 fF | 54.1989 | +5.4504 | +5.5732 | False / False |

The required 5× threshold is 20.9945 fF. A short-window sweep with the input present at startup cannot establish the physical threshold. For the long test, start at zero and apply +1 mV at 12 µs. Fit the relative phase over 18–178 µs. The expected linear beat is 1.104 cycles.

| Zero-input startup | Fitted difference (kHz) | Relative phase span (cycles) | Lock-like |
|---|---:|---:|---|
| As built | +0.0596 | 0.0081 | True |
| Midpoint MIM added | +0.0005 | 0.0014 | True |

With a supply-tracking input, changing only the solver step from 3 to 2 ns changed the 30-phase result from +5.35582 to +0.01819 kHz. The single-tap edge estimator gave +5.95147 and +0.01570 kHz. Startup history and timestep preclude a history-independent 5× claim. Locate the zero crossing on each die and sweep in both directions.

## T6. Bubble errors, reset release and live changes

Seed 260611. Both RTL and routed gates ran 27,200 clocks at 20 MHz with 53 one-clock bubbles and 1,022 debug changes. A triangular-weight CIC oracle compared each SPI clock. RTL and gate mismatches were 0 and 0. 16 frames changed within the bubble response and 0 after it.

The first integrator retained +2 after an isolated bubble. The second accumulated +762 over 381 clocks. Two decimated differences cancel the ramp under 21-bit modular arithmetic. Recovery of the output does not require a bubble-triggered reset.

| Operation | Events | Latest CS start (clocks) | Latest word complete | Two-frame limit |
|---|---:|---:|---:|---:|
| Reset release, OSR 128 | 3 | 162 | 226 | 256 |
| Reset release, OSR 256 | 1 | 293 | 357 | 512 |
| Live OSR change, OSR 128 | 12 | 415 | 479 | 256 |
| Live OSR change, OSR 256 | 12 | 415 | 479 | 512 |

All 151 frames were checked for 16 bits, 64 clocks of CS low and four clocks between rising SCLK edges. Reset was released 1 ps before the rising clock edge. Functional gates do not quantify physical metastability. A live change waits for old-frame phase 97. Set OSR under reset and keep it fixed for acquisition.

The analog model includes extracted capacitances, top-level tap coupling and 5 fF receiver loads. Distributed signal-net resistance and stochastic device noise remain outside these transient cases. The frozen archive contains the original per-case settings, wave hashes and comparison inputs.
