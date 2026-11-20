# Part 0 | Prototype decision | SKY26e differential CCRO ADC | S P G M T
**Proceed to first-silicon characterization at nominal bias and fixed OSR. Near-zero resolution and live rate changes are the principal operating limits.**
<!-- draw | Released mask and nominal operating point | S P G M | cover | Seven layers of the final 161.00 × 225.76 µm mask. HD3 comes from the extracted circuit; SNDR is a model estimate. -->
<!-- table | Device identity | S P | 28,72 -->
| Item | Value |
| Top cell | tt_um_eleva_ccro_adc, SKY130A, 1×2 analog tile |
| Input | Two analog pins, two 15-stage pseudo-differential rings, 30 phase taps |
| GDS SHA-256 | {{gds_sha256}} |
| Analog PEX SHA-256 | {{analog_pex_sha256}} |
<!-- table | Where to start | S P G M T | 28,72 -->
| Task | Pages |
| Signoff decision | 1–2   Mask identity, signoff and operating limitations |
| Datasheet | 3–8   Supply, pin settings, timing and typical characteristics |
| Circuit and layout | 9–13   Input stage, CCRO, timing closure and final mask |
| Verification | 14–19   A1–A6, D1–D4 and T1–T6 results |
| First silicon | 20–24   Wiring, first code, FFT, calibration and revision plan |
| Schematics and data | 25–29   Four complete Xschem sheets, data index and references |

# Part 0 | Signoff | Verification decision and known limits | S P G M T
**The mask passed physical checks. First silicon must establish the lock band, hot-corner linearity, power sensitivity and measured SNDR.**
<!-- table | Signoff decision by evidence | S P G M | 21,15,64 -->
| Check | Verdict | Evidence and remaining condition |
| Physical / D4 | PASS | Precheck 15/15, DRC/antenna 0, unique LVS. 32 MHz setup/hold +6.11/+0.07 ns. |
| A2 / D1–D3 | PASS | All 30 duty cycles in range, CIC and serializer agree with reference. |
| T1 / T2 / T4 | PASS | 10/10 matched starts, ramp and dropout recovery, off leakage and overload recovery. |
| A1 / A3 / A4 | COND | Startup matrix incomplete. Hot-corner saturation and HD3 open. TT HD3 margin +0.64 dB. |
| A5 / T3 | COND | Nine noise cases above 60 dB. Supply-injection verdict depends on reference and phase. |
| A6 / T5 / T6 | FAIL | Near-zero sensitivity, 5× coupling margin and live 256-to-128 recovery miss criteria. |
<!-- table | Performance summary | S P G M T | 31,69 -->
| Metric | Value and scope |
| Area | Tile footprint 0.03635 mm² (161 × 225.76 µm). Analog macro 0.01948 mm². Routed digital cells excluding fillers 8,964 µm². |
| Core power | 361.10 µW at 1.80 V, 20 MHz, nominal bias, zero input, quiet outputs. Pad and board total awaits measurement. |
| Dynamic range / peak SNDR | 66.15 dB / 62.17 dB modeled. Peak among 11 amplitudes at −1 dBFS, OSR 128. |
| Silicon FoM | OPEN. For a measured Schreier FoM record SNDR, measurement bandwidth B in Hz and power P in W. Report SNDR + 10 log10(B/P) with the power boundary. |
<!-- note | Five conditions for first silicon | 1. Sweep around measured offset.  2. Keep OSR fixed.  3. Check hot FF distortion.  4. Measure noise and supply sensitivity.  5. Investigate marginal hold if SPI bits vary. See pp. 14–19 and 24. -->

# Part I | Electrical characteristics | Supply, inputs and current checks | P G M T
**Start at 1.80 V and 0.63 V common mode. The estimated room-temperature core current at zero differential input and 20 MHz is 201 µA.**
<!-- safe | Power sequence and pin voltages | Keep each ua pin between VGND and the instantaneous VDPWR to avoid forward biasing a well or protection junction. Fit 1 kΩ per input. Join grounds, disable the AWG, power the tile, verify the rails, then enable the AWG. Remove external drive before power-off. -->
<!-- table | Electrical conditions | P T | 28,32,40 -->
| Parameter | Value | Interpretation |
| Core supply | 1.80 V nominal; 1.62–1.98 V simulated | Corner values characterize operation. |
| Input | ±0.20 V differential peak at Vcm = 0.63 V | VIN_P/N = Vcm ± Vdiff/2. ±0.60 V was an overload test. |
| Absolute maximum | Breakdown, allowable injection current and ESD limits uncharacterized | Use the pin-voltage limits above on the bench. |
<!-- table | Core current at TT and 1.80 V | P G M T | 27,25,23,25 -->
| Condition | Analog + digital (µA) | Core (µA / µW) | Provisional range |
| Reset, clock low | 42.86 + 0.004 | 42.86 / 77.16 | 30–60 µA |
| 20 MHz, quiet, OSR 128 | 42.86 + 157.75 | 200.61 / 361.10 | 140–260 µA |
Digital current uses 128 µs of gate activity, Liberty internal/switching/leakage power and post-route SPEF. Across three libraries the reset and running estimates are 0.004–3.506 and 141.0–167.4 µA. Exclude pad and board current. On a shared rail compare the change from reset to running, about 158 µA at TT.
<!-- table | Nominal performance | P G M T | 27,32,41 -->
| Parameter | Result | Condition |
| HD2 / HD3 | −90.51 / −62.64 dBc | TT, 27 °C, 50 kHz, extracted external tap loads |
| SNDR | Model 60.04–63.12 dB | −1 dBFS, 20 MHz, OSR 128. Silicon target >56 dB |
| Timing | Setup +6.11 / hold +0.07 ns | Worst of three routed 32 MHz corners |
| Settled code | −4,239 / +4,236 at 20 MHz | ±0.20 V. Gain scales as 1/fs. Routed 32 MHz gives −2,649 / +2,647. |
Pad and board power on silicon is OPEN. A USB measurement includes the board baseline.

# Part I | Pin reference | Complete pin and operating-mode tables | P G T
**ui_in = 0x00 selects nominal bias, quiet debug outputs and OSR 128. Measure both divided oscillator outputs across the input range before collecting ADC data.**
<!-- table | Directions at tile boundary | S G | 29,17,54 -->
| Pins | Direction | Function |
| VDPWR, VGND | Power | 1.8 V rail and return; no VAPWR |
| ua[0], ua[1] | Analog in | VIN_P, VIN_N; ua[7:2] unused |
| clk, rst_n, ena | In | Sample clock, active-low reset, shuttle selection. ena does not gate the core. |
| ui_in[0], [2:1], [4:3] | In | OSR 0/1 = 128/256; DBG_MODE; BIAS_SEL |
| ui_in[5], [7:6] | In | ERR_CLR high ≥3 clocks, then low; drive unused inputs low |
| uo_out[7:0] | Out | Debug data, as below |
| uio[0], [1], [2], [3] | Out | SDO, CS_N, SCLK, WRAP_ERR. Release external drivers. |
| uio[7:4], uio_oe | High-Z / internal | uio_oe = 0x0F, uio_out[7:4] = 0; uio_in is unused |
<!-- table | Bias and sample-clock selection (MHz except input peak) | P T | 18,14,13,13,15,14,13 -->
| Mode / units | Input peak | TT f0 | Start fs | FF max | 2× max | 2.5× |
| 00 / 20 | ±200 mV | 3.769 | 20 | 4.645 | 9.30 | 11.62 |
| 01 / 1 | ±35 mV | 0.246 | 1 | 0.326 | 0.66 | 0.82 |
| 10 / 5 | ±95 mV | 1.072 | 5 | 1.444 | 2.89 | 3.61 |
| 11 / 40 | ±200 mV | 6.958 | 32 | 7.777 | 15.56 | 19.45 |
<!-- table | DBG_MODE; SPI runs in all modes | G | 27,73 -->
| Mode | uo_out[7:0] |
| 00 quiet | All bits zero, dividers stopped |
| 01 raw counts | [7:4] P and [3:0] N, each 0–15, masked during startup |
| 10 dividers | [0] P/64, [1] N/64, [7:2] zero |
| 11 quiet | All bits zero, dividers stopped |
<!-- note | Silent over-wrap and clock limits | Require fs > 2 fmax, preferably at least 2.5 fmax. WRAP_ERR latches at a sampled count of 14 or 15 on either side. Multiple toggles can cancel in XOR and evade the flag. Measure both /64 outputs first. FF maxima cover ±endpoints at 85 °C, 1.98 V. TT f0 is at 27 °C, 1.80 V, zero input. 32 MHz is the highest STA clock. -->

# Part I | Timing and interface | CIC2 response, settling, input loading and SPI | P G M T
**At 20 MHz the ADC delivers a signed word every 6.4 µs at OSR 128. A step can take several frames to settle.**
<!-- fig | Filter magnitude and a routed SPI word | G M | cic_bandwidth,spi_word_example | 117 | Left: normalized CIC2 gain at 20 MHz. Right: sixth clean T3 frame at TT, 27 °C, 1.80 V. Read SDO on rising SCLK while CS_N is low. -->
<!-- table | Timing at 20 MHz from sample to closed frame | P G M | 41,29,30 -->
| Quantity | OSR 128 | OSR 256 |
| Output rate / −3 dB bandwidth | 156.25 / 49.75 kHz | 78.125 / 24.87 kHz |
| Group delay / SPI active | 6.35 / 3.20 µs | 12.75 / 3.20 µs |
| Ideal tap step, exact word (all phases) | 17.65–24.00 µs | 30.45–43.20 µs |
| PEX step, settled within 1% | 17.325–22.125 µs | 31.875–41.475 µs |
PEX: 0 to +100 mV in 10 ns at TT, 1.80 V, 27 °C, 1.5 kΩ and 5 pF per pin. Four frame alignments per OSR. From step midpoint to closed SPI frame with at least three consecutive words within 1% of final median.
<!-- table | Input and output conventions | P G T | 24,76 -->
| Field | Definition |
| Macro load | Cin P/N = 26.5/27.0 fF (20 mV differential peak, 50 kHz), including 11.9/11.6 fF explicit PEX wiring. Package and switch add load. Gate leakage models are disabled. A DC simulation cannot bound pin leakage. |
| Code gain | Positive Vdiff increases fP−fN. Mean signed code ≈ 2,048 × 30(fP−fN)/fs. ±0.20 V gives about ±4,236 at 20 MHz and ±2,648 at 32 MHz. |
| Mode 0 frame | ADC drives SCLK = fs/4. First rise 100 ns after select at 20 MHz. D15 first, 16 bits. 0xF70D = 63,245 − 65,536 = −2,291. |
| ETR v3.2 (RP2350B) | PIO stores two samples per 32-bit little-endian record, earlier word in the upper half. Reframe at each falling CS_N. |

# Part I | Static performance | Linearity and DC code noise | P M T
**Across 11 TT transfer points, peak absolute residual is 4.49 codes against the endpoint line and 3.83 codes against a least-squares line. Resolution near zero needs a separate lock-band sweep.**
<!-- fig | Transfer residuals and the zero crossing | P | char_static | 143 | The left panel uses 11 PEX points spaced 40 mV apart, with 5 fF receiver loads. The right panel shows seven separately measured points with extracted tap wiring added, shown against the same endpoint slope through zero. -->
One output code corresponds to 47.20 µV using the 8,474.4-code nominal span at 20 MHz. The maxima correspond to 0.0530% and 0.0452% of that span. These are sampled frequency-to-code residuals before integer slicing. Sweep about measured Vos to resolve narrow features between points.
<!-- fig | DC output distribution at +50 mV | M | char_histogram | 115 | Central A5 model, OSR 128. The 32,761 settled words span codes 1,055–1,067. -->
<!-- table | DC noise referred to the usable analog range | M | 33,23,44 -->
| Quantity | Model value | Definition |
| RMS output / input noise | 1.476 codes / 69.65 µV | Standard deviation about the DC mean |
| Noise-free resolution | 9.77 bits | log2[span / (6.6 × rms noise)] |
| Dynamic range | 66.15 dB | 20 log10[span / (2√2 × rms noise)] |
The observed spread was 12 codes peak-to-peak. The 45.33 µV front-end noise estimate describes one source. On silicon, collect DC histograms both at +50 mV and around measured Vos to reveal code concentration from locking.
<!-- url | Analog Devices MT-004 · DC noise and noise-free resolution | https://www.analog.com/media/en/training-seminars/tutorials/mt-004.pdf -->

# Part I | Dynamic performance | Input amplitude and frequency sweeps | M T
**At 10.010 kHz the highest modeled SNDR among 11 amplitudes was 62.17 dB at −1 dBFS. The same point gave 64.24 dB SNR and 67.02 dB SFDR.**
<!-- fig | Amplitude sweep at 10.010 kHz | M | char_amplitude | 174 | Nominal TT fit, 20 MHz, OSR 128, common random sequence (seed 27) and assumed ring FoM of −155 dBc/Hz. 0 dBFS is 200 mV differential peak. -->
<!-- fig | Frequency sweep at −1 dBFS | M | char_frequency | 165 | Seven tones from 1 to 50 kHz. Each spectrum uses 32,761 samples, the four-term Blackman–Harris window and the same output Nyquist band (78.125 kHz). At 50 kHz, HD2 folds to 56.25 kHz and HD3 to 6.25 kHz. Harmonic bins include residual noise. -->
At 50 kHz the fundamental is 2,667 output codes peak versus 3,780 at 1 kHz (−3.03 dB). CIC2 also attenuates harmonics before aliasing. The 50 kHz modeled output HD3 and the 50 kHz PEX ring-frequency HD3 on page 3 measure different nodes. Use the latter for the −62 dBc analog criterion.
<!-- note | What the first silicon measurement must establish | The smooth static fit omits injection locking, frequency-dependent analog distortion and external supply coupling. Near zero, use the Vos sweep. At larger amplitudes, sweep the SPI output with a characterized sine source, holding the clock, OSR, input common mode and output bandwidth fixed. -->

# Part I | Environmental sensitivity | Gain, center frequency and common mode | P T
**At TT, gain falls on either side of 27 °C, down 2.13% at −20 °C and 1.65% at 85 °C. Supply sensitivity is −11.07 %/V. Calibrate DC measurements at the operating point.**
<!-- fig | Two independent sweeps at nominal bias | P | char_pvt | 225 | The center point is shared. Each gain uses differential frequency at −160 and +160 mV. f0 is the mean of the two ring frequencies at zero differential input. Lines join discrete simulations. -->
<!-- table | Gain relative to TT at 27 °C and 1.80 V | P | 21,21,24,18,16 -->
| Temperature | Supply | Gain (MHz/V) | Change | f0 (MHz) |
| 27 °C | 1.80 V | 6.900 | 0.00% | 3.769 |
| -20 °C | 1.80 V | 6.753 | −2.13% | 3.142 |
| 85 °C | 1.80 V | 6.786 | −1.65% | 4.209 |
| 27 °C | 1.62 V | 7.034 | +1.94% | 3.820 |
| 27 °C | 1.98 V | 6.759 | −2.05% | 3.660 |
At the reference condition, G = 6.900 MHz/V. Gain change is 100 × (G/Gref − 1). The end-to-end temperature slope is +0.00455%/°C. The lower and upper segments give +0.0454 and −0.0285%/°C, respectively. Supply sensitivity uses the 1.62 and 1.98 V endpoints. Absolute gain after manufacturing requires a reference input and calibration.
<!-- note | T4 common-mode sensitivity at −100 mV differential | Raising Vcm from 0.48 to 0.78 V changed differential frequency by −13.19 kHz, or −43.96 kHz/V. T4 measured differential gain of 6.908 MHz/V at Vcm = 0.63 V using ±100 mV. The resulting finite-swing rejection ratio is 43.93 dB. Gain modulation contributes at this input. Zero-input small-signal CMRR remains open near the lock band. -->

# Part II | Analog front end | Differential input and self-starting bias | P
**Each side has 40 PMOS units grouped 1 + 4 + 15 + 20. A startup branch senses vn and moves the beta multiplier away from its zero-current equilibrium.**
<!-- note | Split-tail input devices and degeneration | Minp0 and Minn0 each represent one of four parallel LVT PMOS. vinn drives the P ring; vinp drives the N ring. Rr0 connects sp to mid, and Rr1 continues to sn. -->
<!-- jump | Full schematic · front.sch · p. 25 | 25 -->
<!-- note | Beta multiplier and startup | Mp0 and Mn1 form the resistor-side leg. When vn is low, Mweak raises kick and Mkick pulls vb down. As vn rises, Msense discharges kick. -->
<!-- jump | Full schematic · beta_ref.sch · p. 26 | 26 -->
<!-- table | Nominal passive values and MOS W/L (µm) | P | 27,33,40 -->
| Device | W/L or geometry | Connection or value |
| Unit source / input | PMOS 1/2; LVT PMOS 6/1 ×4 | Source wells at VDPWR; input wells at sp/sn |
| Reference branches | P 2/2 ×2; N 8/2 and 2/2 | P wells at VDPWR, N bulk at VGND |
| Startup | Weak P 0.42/12, sense N 5/0.15, pull-down N 0.5/1 | Gates at VGND, vn and kick respectively |
| Degeneration / reference | High-R poly 0.69 wide, lengths 80 / 97.1 | TT: 39.70 / 48.10 kΩ per half; 79.40 / 96.21 kΩ total |
| Rail MIM | 21.8 × 21.8 µm | 0.965 pF per side at 1 kHz, TT; no added mid MIM on mask |
If both rings fail to oscillate, trace the vn–kick–vb startup path, then check that vb reaches each enabled source bank. Ramp and dropout evidence is on p. 16.

<!-- table | From bias voltage to frequency difference | P | 23,77 -->
| Node | Function |
| vb to sp/sn | One of 40 tail units is always connected. Gates in the other groups connect to vb or the supply to select 1, 5, 20 or 40 active units per side. |
| sp/sn to mid | Two degeneration resistors turn differential voltage into a current imbalance. Each isolated input well is tied to its local source. |
| rp/rn to phase | A positive input reduces current on the crossed N branch, increasing fP−fN. Local rail MIMs absorb transient charge at each ring supply. |

# Part II | Oscillator and tap receiver | Ring feedback and level shifting | P
**Fifteen main inverters form each odd ring. Weak same-stage cross-coupled inverters select complementary phases. CVSL shifts the low ring swing to the 1.8 V readout.**
<!-- note | Main inverter and local cross-coupling | a and b are the preceding stage outputs. The main pair shown drives y. Two weaker inverters cross-couple y and z within the stage. Stage 14 feeds stage 0 in the same orientation. -->
<!-- jump | Full schematic · stage.sch · p. 27 | 27 -->
<!-- note | CVSL receiver and tap buffer | a and b drive the LVT NMOS pair. Each PMOS gate senses the opposite drain. l drives the tap buffer; r drives an identical dummy load. -->
<!-- jump | Full schematic · cvsl.sch · p. 28 | 28 -->
<!-- table | Delay and receiver devices | P | 28,37,35 -->
| Location | Geometry | Electrical role |
| Main / cross inverters | P/N widths 8.4/4.2 and 1.68/0.84 µm; L = 0.55 µm | Weak-to-main width ratio 1/5 |
| A and B node loads | 4.5 × 4.5 µm MIM | 43.45 fF nominal per node |
| CVSL / buffer | Feedback P 0.42/2.4, input N 4/0.15, buffer P/N 0.84/0.42 wide, L 0.15 µm | Symmetric loads on L and R |
| External tap load | 5 fF receiver plus 3.09–8.11 fF of wiring | Incremental capacitance with adjacent terminals stationary |
Straight feedback from stage 14 to stage 0 preserves odd inversion on each main path. Swapping the final phases would change the differential loop into positive feedback and permit a static latch state. T1 tests startup within a ring. T5 tests unwanted synchronization between the two independent rings.

<!-- table | Circuit nodes and verification evidence | P G | 23,77 -->
| Observation | Check |
| Stage outputs a/b | T1 starts all 15 stages in common mode and checks recovery to complementary oscillation (p. 16). |
| Full-swing taps | A two-flop synchronizer feeds each XOR transition counter. Page 19 covers transient errors and bubbles in the sampled tap sequence. |
| Differential rate | At small input, parasitic coupling between the two rings can suppress the frequency difference. See the startup-dependent T5 result on p. 18. |

# Part II | Digital readout | Datapath and routed timing | G
**At 32 MHz, worst setup slack is +6.11 ns and worst hold slack is +0.07 ns. A slower clock does not resolve an internal hold violation.**
<!-- draw | Transition-count readout | G | digital | Synchronize each tap twice and XOR it with its previous sample. Two 21-bit integrators and two decimated combs supply the serializer. The sticky wrap output is independent of SPI. -->
A signed 5-bit count difference ranges from −15 to +15. Reset asserts asynchronously and releases synchronously. A four-clock validity mask allows the synchronizers and prior-sample registers to fill before accumulation.
<!-- verify | D4 area and timing | S G | 33,36,18,13 -->
| Cell area ≤9,000 µm² | 8,964 µm² excluding filler | +36 µm² | PASS |
| Macro height ≤100 µm | 150 × 100 µm | 0 µm | PASS |
| Setup / hold ≥0 ns | +6.11 / +0.07 ns at 32 MHz | Both positive | PASS |
Digital wiring uses distributed SPEF; top-level loads are extracted. The three timing libraries are FF −40 °C/1.95 V, TT 25 °C/1.80 V and SS 100 °C/1.60 V. Gate simulation does not resolve analog metastability duration.
<!-- note | If SPI bits disagree | First inspect SDO, SCLK and the receiver edge at the pins. On an independently adjustable core rail, compare 1.70, 1.80 and 1.90 V while holding input, clock and temperature constant. -->

# Part II | Physical implementation | Mask geometry and extracted coupling | S P
**The wide central vertical met4 stripe is VGND. External clock and SPI wiring stay above the analog area; 30 level-shifted phase taps cross the partition.**
<!-- fig | Whole tile and P-ring detail | S | gds_tile,gds_ring_detail | 202 | Tile coordinates are in µm from the lower left. Whole tile: X = 0–161, Y = 0–225.76. Inset: X = 1–28, Y = 86–114. Displayed layers are diff, poly, LI1 and met1–4. -->
<!-- table | Locations on the final mask | S P | 28,72 -->
| Structure | Coordinates or extraction |
| Digital / analog | Digital starts at (4.25,125.76) µm, size 150 × 100. Analog starts at (0,0), size 161 × 121. Input/reference below the rings and receivers. |
| Power and return | VGND X = 92.80 and VDPWR X = 0.60 µm; vertical stripes 1.20 µm wide from Y = 2 to 217 µm. |
| External high-speed nets | Clock Y ≥169.535 µm; SDO, CS_N and SCLK Y ≥200.005 µm. |
| Rail coupling | Extracted rp–rn capacitance 4.1989 fF. Guard contacts provide a return; geometry alone cannot establish locking margin. |
<!-- verify | Physical checks | S | 33,34,20,13 -->
| Precheck / DRC / antenna | 15/15, zero full DRC and antenna violations | 0 open | PASS |
| LVS / signal continuity | 10,390 devices, 5,137 nets, 64/64 paths | 0 mismatches | PASS |
The substrate wall at X = 80.25 µm carries 82 rows of three contacts (246). The separate VGND supply trunk is at X = 92.80 µm. The wall provides a local return path. The extracted rp–rn coupling and T5 remain the electrical checks of isolation. Use atlas_index.json for layer coordinates and atlas_blocks.lyrdb for individual cells.
<!-- jump | Inspect the extracted coupling result · p. 18 | 18 -->

# Part II | Analog mask details | Matching and phase order on the final mask | S P
**Read each panel in tile coordinates (µm, origin at lower left). P/N labels identify branches and numbers identify ring stages.**
<!-- fig | Front end, passives, folded ring and receiver bank | S | atlas_review | 368 | Geometry from the SHA-256-checked GDS. Layer colors are shared across panels. Both C views belong to the passives block. -->
<!-- table | What to inspect | S P | 23,77 -->
| Block | Mask detail and design intent |
| A · Tail array | One side shown. Four rows of ten implement groups 1 + 4 + 15 + 20. Shared diffusion and equal unit size set the ratios. |
| B · Input quad | Both diagonals have the same geometric centroid. Each isolated input well returns to its own source sp or sn. |
| C · Resistor / MIM | Four parallel resistor bodies implement degeneration and reference pairs. Large MIMs connect rp/rn to ground. The final layout has no dedicated mid MIM. |
| D · Folded P bank | Stage 0 feeds 1 above it, then 2 in the next column. Dual M2 returns carry stage 14 to 0. D marks the dummy site. |
| E · CVSL bank | Receiver pitch 4.925 µm. A paired small-swing input drives a full-swing digital tap. Equally loaded output branches preserve symmetry. |

# Part III | A4 and T4 | Harmonics, overload and input offset | P T
**The loaded nominal HD3 is −62.64 dBc, 0.64 dB inside the limit. After ±0.60 V overload the slowest tap recovers in 1.01 periods.**
<!-- fig | Input-loaded sinusoidal transient | P | dynamic | 142 | P/N frequencies reconstructed from 30 phases versus time. TT, 27 °C, 1.8 V, nominal bias. Input 50 kHz, ±0.20 V differential; each input has 1.5 kΩ series and 10 pF shunt. -->
<!-- verify | Static sweeps and dynamic tests | P T | 34,33,20,13 -->
| TT static HD3 ≤−62 dBc | −63.73 dBc; HD2 −78.46 | +1.73 dB | PASS |
| SS, 1.62 V static HD3 | −82.60 dBc; HD2 −75.06 | +20.60 dB | PASS |
| TT dynamic HD3 | −62.97 dBc; −62.64 with routed tap load | +0.97 / +0.64 | PASS |
| SS tail headroom ≥0.20 V | 0.261 V | +0.061 V | PASS |
| Static/dynamic agreement | HD3 0.76 dB, HD2 12.72 dB | Method-sensitive HD2 | COND |
| Overload recovery ≤2 cycles | +0.60 to +0.10 V: 0.99; negative: 1.01 | ≥0.99 cycles | PASS |
| HD3 loss with 1.5 kΩ <1 dB | −63.297 to −63.753 dBc | +1.456 dB | PASS |
| Full-scale hot FF HD3 | Vcm = 0.630–0.631 V not fully covered | Open | OPEN |
All taps operated at Vcm = 0.48 and 0.78 V. The switch uses fixed RC. Fifty extracted input-stage mismatch draws gave offsets of −11.04 to +13.02 mV. Ring-to-ring mismatch yield remains open.
<!-- note | Hot-corner diagnosis | Keep Vdiff fixed; raise Vcm by 50 then 100 mV and compare gain, both divided frequencies and HD3 on the same die. -->

# Part III | A5 | Long-record spectrum and noise budget | P M T
**The nominal model predicts 62.17 dB SNDR. Nine combinations of jitter figure of merit and seed span 60.04–63.12 dB. Silicon SNDR remains open.**
<!-- fig | Long noise-model output spectrum | M | budget_sndr_spectrum | 173 | −1 dBFS at 10.010 kHz, TT transfer, 20 MHz and OSR 128. Bin power is relative to integrated fundamental power. The model does not include T5 history-dependent locking. -->
Discard four of 32,765 words, leaving 32,761 at 156.25 kS/s (4.769 Hz/bin). Use a periodic four-term Blackman–Harris window, integrate the fundamental ±5 bins and exclude the lowest six bins. Analysis band approximately 28.6 Hz–78.125 kHz. Seed 27 gives SNR 64.24 dB, SFDR 67.02 dBc and HD3 −67.02 dBc.
<!-- table | Contributions in the same finite output record | P M | 26,36,19,19 -->
| Component | Basis | Input µV rms | Residual power |
| Front end and bias | Standalone flat-band integration 45.33 µV rms | 41.03 | 17.48% |
| Period jitter | 106.69 ps rms per side; assumed FoM −155 dBc/Hz | 52.70 | 28.84% |
| Quantization | Phase quantization and code truncation | 39.39 | 16.11% |
| Transfer distortion | Harmonics of noiseless fifth-order fit and window residual | 60.94 | 38.56% |
| Cross terms / total | Correlations in the finite record | — / 98.13 | −1.00% / 100% |
The standalone input-noise integration covers 10 Hz–78.125 kHz. The 41.03 µV value includes CIC and FFT weighting. Measure source harmonics, supply spurs and oscillator phase noise separately on the bench.

# Part III | A1–A3 and T1–T2 | Startup, supply recovery and corner limits | P
**All ten corner/bias combinations reached antiphase within 3.42 periods from 60 equal node voltages. The slow ramp and brownout recovered autonomously.**
<!-- fig | Equal-node startup and brownout recovery | P | startup_recovery | 154 | Left: P-ring A/B and supply after release at 1.80 V. Right: rail, bias and tap at restoration after 50 µs at 0.60 V. TT, 27 °C, nominal bias. -->
<!-- verify | Startup, leakage and limiting frequencies | P | 32,37,18,13 -->
| T1 settle in ≤10 periods, 180° ±15° | 0.35 V initial voltage, five corners, modes 00 and 01. Latest stage 3.04–3.42 periods | ≥6.58 | PASS |
| T2 slow ramp, within ±5% | 10 ms ramp, mode 01: 0.2472 MHz, vb 0.6826 V. Largest difference 0.302% | 4.698 points | PASS |
| T2 recovery swing >1.5 Vpp | Both stop at 0.6 V. After restoration ~3.7687 MHz, minimum 1.812 Vpp | 0.312 Vpp | PASS |
| T2 off leakage <25 nA and <5% | FF, 85 °C, 1.98 V. 39 units: 0.0569 nA; active unit 465.54 nA | 24.94 nA | PASS |
| A1 startup matrix | TT 1 µs starts, min differential swing 1.485 Vpp. Full ramp matrix remains open | Incomplete | COND |
| A2 slow-corner duty | SF, −20 °C, 1.98 V. Min 103.98 kHz; 30 taps at 50.06–50.17% | Within 45–55% | PASS |
| A3 nominal / fast limits | FF, 85 °C, 1.98 V, +0.20 V. 4.645 / 7.777 MHz versus 8.0 / 12.8 | 3.35 / 5.02 MHz | COND |
T1 confirms the first two consecutive valid periods that remain valid thereafter. The 10 ms ramp was integrated continuously. A separate numerical comparison of the 1 µs reference changed six measured quantities by at most 0.279%.

# Part III | T3 | Supply modulation and the SPI spectrum | P G M
**Local rail ripple rises from 1.92 to 32.02 mVpp. Routed-SPI SNDR falls from 66.71 to 64.58 dB; one relative sampling phase exceeds the 3 dB loss criterion.**
<!-- fig | Rail waveform and decoded SPI spectrum | P G | ssn | 194 | TT, 27 °C, 1.8 V, nominal bias, OSR 128. Each rail has 5 Ω + 2 nH. Two 1 mA bursts at 20 MHz and 156.25 kHz are injected together. -->
Replay 30 taps at 20 MHz with a 19.53125 kHz, −1 dBFS input. Decode words 5–20 from 20 frames. A 16-point rectangular window covers 102.4 µs, 9.765625 kHz/bin. Exclude DC, use bin 2 for the tone and count Nyquist once. Third and fifth harmonics fold to bin 6.
<!-- verify | Different reference conditions | P G M | 33,36,19,12 -->
| Routed quiet-to-injected loss ≤3 dB | 66.71 to 64.58 dB: loss 2.13 | +0.87 dB | PASS |
| Disturbance added to 54 dB budget | Maximum loss 0.536 dB over eight phases and gate replay | +2.464 dB | PASS |
| Direct loss relative to quiet ≤3 dB | Maximum paired loss 3.267 dB | −0.267 dB | FAIL |
| Continuous supply lock | Minimum relative phase excursion 11.38 cycles at tested ratios | >1 cycle | PASS |
Overall T3 is conditional. Quiet/injected residuals are 1.174 / 1.501 codes rms; SFDR is 71.19 / 67.65 dBc. This short record resolves discrete spurs. A broadband noise measurement needs a longer acquisition.

# Part III | A6 and T5 | Near-zero sensitivity and injection locking | P M T
**Starting directly at +1 mV can produce a frequency difference. Starting at zero before applying +1 mV gives only 0.0081 cycles of relative phase motion over 160 µs.**
<!-- fig | Relative phase after a zero-input start | P M | long_phase | 149 | Switch to +1 mV at 12 µs; plot phase relative to 18 µs. TT, 27 °C, 1.80 V, nominal bias. Compare the linear prediction, released mask and extra midpoint MIM. -->
<!-- table | Input history and numerical sensitivity | P | 27,73 -->
| Experiment | Observation |
| Loaded A6 sweep | At −10, −3, −1, 0, +1, +3, +10 mV: ∆f ≈ −69.241, −20.768, +0.007, +0.003, +0.001, +20.054, +68.693 kHz. |
| T5 short record | Remove direct coupling, or add 0, 1, 5, 20, 50 fF to 4.1989 fF. Each short-window case drifted with and without extra Cmid. |
| T5 long record | As built: +0.060 kHz fitted difference, 0.0081 cycles of motion. With 206.58 fF extra: +0.0005 kHz, 0.0014 cycles. Expected 1.104 cycles from 6.9 kHz/mV. |
| Timestep | Changing only the maximum step from 3 to 2 ns changed the tracking-input result from +5.35582 to +0.01819 kHz. |
A6 misses proportionality at 1 mV. T5 needs a locking threshold ≥20.9945 fF; a lock-like case already occurs at 4.1989 fF. At 3.769 MHz the added midpoint capacitor presents ~204 kΩ; at 20 MHz ~38.5 kΩ. The 39.70 kΩ half-resistors, transistor branches, direct rail coupling and supply/substrate paths all matter.

# Part III | D1–D4 and T6 | Digital transients and configuration changes | G
**All 151 stress-test frames had valid SPI timing. A single bubble clears from the output, but a live 256-to-128 OSR change can take 479 clocks to complete a new word.**
<!-- fig | Routed SPI frame in T6 | G | spi | 129 | Logic levels versus clocks since frame start; virtual phase taps at 20 MHz. The functional gate run has no analog bias or temperature parameter. -->
<!-- verify | Frame and code checks | G | 34,35,18,13 -->
| D1–D3 count / CIC / SPI | Each model ran 13,800 clocks, 70 frames, ±30,720, both rates and wrap clear | 0 mismatches | PASS |
| D4 area and timing | 8,964 µm²; positive setup and hold at 32 MHz | 36 µm² | PASS |
| T6 transient bubble | 53 insertions affected 16 words. No differences after response window | 0 residual | PASS |
| Reset to first complete word | R128: 226 clocks. R256: 357 clocks | +30 / +155 | PASS |
| Live 256 to 128 ≤256 clocks | First CS at 415, completion at 479 | −223 clocks | FAIL |
| Live 128 to 256 ≤512 clocks | Worst completion 479 clocks | +33 clocks | PASS |
T6 ran 27,200 clocks in each model, toggled debug 1,022 times and released reset 1 ps before the active edge. The first integrator retained +2 counts after 400 clocks; the second accumulated +762 in 381 clocks. Two decimated differences cancel the ramp under 21-bit modular arithmetic.
<!-- note | Keep OSR fixed during capture | The active frame accepts the new setting at phase 97. A later request waits for the next opportunity. Set the rate during reset, release reset and discard the first two frames. -->

# Part IV | Bench connections | Connect the ETR v3.2 and Analog Discovery 2 | T
**Match the ETR v3.2 (RP2350B) and the correct SKY26e breakout. Confirm analog header allocation for this project before connecting the source.**
<!-- draw | Connector landmarks and signal directions | T | bench_compact | 1 ANALOG, 2 BIDIR/J12, 3 USB-C, 4 AD2 flywire. Photographs and official schematic linked below. Ground is common. Leave AD2 V+ and V− disconnected. -->
<!-- table | Before power-up | T | 23,77 -->
| Path | Bench connection |
| Analog | W1 (yellow) and W2 (yellow/white) through separate 1 kΩ resistors adjacent to VIN_P and VIN_N. Verify the actual ANALOG contacts against this shuttle. |
| Digital | Use the verified 3.3 V side of the board-approved level translator. J12 can be directly wired to uio. Where no translator is fitted, insert a board-I/O-to-3.3 V receive buffer rated for the SPI rate. Enable after both rails are valid. |
| Shared pins | Set b0–b3 on the RP2350B to Hi-Z, disable pulls and AD2 Patterns/Static I/O/master. Leave input DIPs off when the board drives ui. Connect J13.1/o0 and J13.2/o1 through receive channels to DIO4/5 for P/64 and N/64. |
<!-- url | Board image · Tiny Tapeout / Psychogenic Technologies, documentation CC0 1.0 | https://github.com/TinyTapeout/tt-demo-pcb/blob/bbf3dd1f771d5aed249b07ddf130b3ddc8261d60/doc/img/tt-etr-dbv3p2-render.png -->
<!-- url | AD2 photograph · SparkFun Electronics, source and attribution | https://commons.wikimedia.org/wiki/File:Digilent_Analog_Discovery_2_(28784064755).jpg -->
<!-- url | AD2 photograph license · Creative Commons Attribution 2.0 | https://creativecommons.org/licenses/by/2.0/ -->
<!-- url | Tiny Tapeout ETR v3.2 · official schematic, J12/J13 on sheet 1 | https://github.com/TinyTapeout/tt-demo-pcb/blob/bbf3dd1f771d5aed249b07ddf130b3ddc8261d60/doc/tt-etr-dbv3.pdf -->

# Part IV | First power and first code | Power up, verify both rings and decode one word | P G T
**With USB power off, seat the breakout, join grounds, disable AWG and release shared digital drivers. Power the board, check the 1.80 V rail and select the actual shuttle design.**
<!-- benchcmd | from ttboard.demoboard import DemoBoard | from ttboard.mode import RPMode | tt = DemoBoard.get() | tt.mode = RPMode.ASIC_RP_CONTROL | tt.shuttle.tt_um_eleva_ccro_adc.enable() | tt.clock_project_stop() | tt.reset_project(True) | tt.uio_oe_pico.value = 0 | tt.ui_in.value = 0x04 -->
<!-- table | Reset, divider check and quiet operation | T P G | 24,76 -->
| Step | Action and expected observation |
| Measure | With the rail stable, W1 = W2 = 0.630 V DC. Check isolated reset current (30–60 µA). Run tt.clock_project_PWM(20_000_000), then tt.reset_project(False). |
| Check P/64 and N/64 | View DIO4/5 at 5 MS/s for 0.8 ms. Near zero expect about 58.9 kHz each at TT. Measure zero and both endpoints. Multiply by 64 and apply p. 4. |
| Quiet run | Return to zero input. Assert reset, set tt.ui_in.value = 0x00, release reset. Discard two complete frames. Running core screen 140–260 µA. On a shared rail compare the reset-to-run change (p. 3). |
<!-- table | WaveForms settings and first signed word | T G | 23,77 -->
| Instrument | Settings and expected observation |
| Wavegen / Scope | DC polarity: W1/W2 = 0.680/0.580 V, then swap. For sine: synchronized, 10 kHz, both offsets 0.630 V, amplitudes 0.100 V peak, phases 0°/180°. Probe after resistors, DC-coupled. Math CH1−CH2 gives Vdiff, (CH1+CH2)/2 gives Vcm. |
| Logic | Single, 100 MS/s, 4,096 samples. Trigger falling DIO1, pretrigger 20%. Mode 0, DIO2 clock, DIO0 data, D15 first. Sixteen rises per 3.2 µs frame, 6.4 µs cadence. DIO3 WRAP must be low. |
| First code | A positive DC step gives a positive settled word. Example 0x0849 = +2,121. For negative words subtract 65,536. With no trigger, check selection, reset, clock and J12 before the translator (p. 23). |

# Part IV | Long acquisition | Measure SNDR from a continuous 32,768-word record | T M
**At 156.25 kS/s the record lasts 209.7152 ms. Use Logic to validate the bus and the board’s PIO/DMA receiver to collect consecutive words. Separate short triggered captures lose the samples between triggers.**
<!-- table | Complete the run in this order | T G M | 24,76 -->
| Checkpoint | Procedure |
| Source baseline | First measure the differential source with the same amplitudes, common mode, fixture and probe loading. Record its harmonics and the measurement floor. A spur near the source/monitor floor limits attribution to the ADC. |
| Stable operating point | With reset released, fixed OSR 128 and quiet debug, wait at least two frames after a change. Set both AWGs to 0.630 V offset, 0.089125 V peak, phases 0°/180°, bin 2,099 at 10.008812 kHz nominal. Confirm clean frame spacing and WRAP low before and after the record. Record the measured output rate. |
| Capture on ETR v3.2 | Copy tools/tt_adc_pio_rx.py to the board before setup. With the p. 21 board settings active, use the REPL commands below. This mapping is specific to RP2350B ETR v3.2. Verify rp2.DMA and that PIO1 SM0 is free. Hardware validation of this capture path is pending. |
<!-- benchcmd | mpremote cp tools/tt_adc_pio_rx.py :tt_adc_pio_rx.py -->
After the PC copy, restore the p. 21 quiet setup if the board reset. At the active board REPL run:
<!-- benchcmd | import tt_adc_pio_rx as rx | rx.PIN_SDO, rx.PIN_CSN, rx.PIN_SCLK = 25, 26, 27 | rx.capture(156250, "/adc_raw.bin") -->
Expect 65,536 bytes. Keep the raw file. Check frame cadence, count, timeouts and overruns. Retake records with gaps or WRAP high. Decode little-endian sample pairs as on p. 5.
<!-- benchcmd | mpremote cp :adc_raw.bin . | python tools/analyze_sndr.py adc_raw.bin --fs-out 156250 --skip 0 --plot spectrum.png -->
Use the measured rate for both commands. Discard startup before acquisition. --skip 0 retains all 32,768 words. The analyzer removes the mean, applies a four-term Blackman–Harris window, excludes bins 0–5 and sums through the output Nyquist frequency. With independent AD2 and board clocks, dialing in 2,099 × fout / 32,768 alone does not ensure coherence. A rectangular-window comparison requires verified integer-cycle capture. Report window, band, fundamental, HD2/HD3, SFDR and SNDR. The analyzer’s dBFS16 scale uses 32,768 codes; the analog stimulus scale here uses a 0.200 V differential peak.
<!-- note | Voltage calibration | At ±0.16 V use mean codes C+ and C−: G=(C+−C−)/0.32, B=(C++C−)/2 and x=(code−B)/G. Fit Vdiff=a0+a1x+a2x²+a3x³ to 5–11 points outside the lock band; test correction on an independent sine wave. -->

# Part IV | Diagnosis and record | Localize an error before changing the setup | T P G
**A rail reading, two divider frequencies, three SPI traces and the measured differential input usually identify which stage of the bench needs attention. Keep these observations together.**
<!-- table | Start from the observed symptom | T P G | 26,40,34 -->
| Observation | Next measurement | Interpretation or action |
| No CS_N or free-running SCLK | Check board ID, enabled design, reset release and actual fs. Probe J12 b1 and b2 against GND before and after the translator. | A valid frame at J12 isolates the fault to the receive path or trigger. |
| Code sign reversed, or about twice expected | Set +100 mV DC, read W1/W2 after the resistors, then inspect the first SPI bit and byte order. | Check swapped VIN pins, peak versus peak-to-peak entry, or signed conversion. |
| A flat interval around zero | Start at ±20 mV, find the zero-code crossing or the edges of a plateau. Record its midpoint as Vos. Sweep Vos ±1, ±3 and ±10 mV in both directions. | Use equal dwell, e.g. 1 ms per step, then average 128 settled words. Log P/64 and N/64 in a separate fixed-debug run. |
| Unexpected harmonic or low SNDR | Repeat the source-only check, confirm common mode and word continuity, compare quiet and raw-debug captures under the same conditions. | A common spur points toward stimulus or pickup. A changing spur motivates a rail or debug-activity measurement. |
<!-- table | Minimum capture record | T | 28,72 -->
| Record with each file | Include |
| Identity / setup | Die and shuttle ID, board and breakout revisions, ua[0]/ua[1] header labels, translator, firmware and WaveForms version, temperature and measured supply. |
| Signal / acquisition | W1/W2 levels and phase, measured Vcm and Vdiff, scope loading, actual fs and fout, ui_in, reset history, divider rates, WRAP, sample count and gaps. |
| Files / results | Save workspace, source-only trace, raw Logic sample data or binary, decoded samples, spectrum and analysis options. Mark estimates, simulated references and bench readings separately. |
At shutdown stop the stimulus and confirm both analog leads have returned to a safe voltage or disconnect them. Disable the digital interface, remove board power and disconnect ground last.
<!-- jump | Return to board setup and first code · p. 21 | 21 -->

# Part IV | Next revision | Rev 2 candidates and closure criteria | S P G M T
**Select design changes after the first lot identifies which failure mechanisms dominate. Keep the GDS and PEX hashes with each comparison.**
<!-- table | Next mask changes | S P G M T | 25,34,41 -->
| Open item | First-silicon observation | Candidate change and acceptance test |
| T5 lock band | Measure bidirectional width, dwell and divided frequencies by die, bias, Vcm and temperature. | Separate bias/supply returns and compare MIM placements. Repeat R-C PEX with timestep convergence and both startup histories through 5× actual coupling. |
| T6 256-to-128 delay | Capture request and CS simultaneously, sorted by old frame phase. | Accept on idle CS and restart history. Verify every old phase completes 16 bits within two new frames with no malformed words. |
| HD3 and FF/85 °C | Sweep Vcm and temperature at fixed Vdiff. Log source residual, gain, frequency and HD3. | Check input/tail saturation and HD3 ≤−62 dBc using hot-corner R-C PEX; retune bias or degeneration if necessary. |
| +0.07 ns hold | Isolate receiver errors; compare three supply voltages at fixed clock. | Identify and delay the shortest path. Repeat all setup/hold corners and area check. |
| Silicon SNDR and SSN | Capture 32k words and rail waveform together. Compare spur frequencies with the injected sources. | Update noise budget with measured jitter. Recheck ≤3 dB loss using the same phase sweep. |
| Startup and current | Record board ramp, temperature, die, inrush, settled current and restarts. | Cover specified 1 µs/1 ms ramps and mismatch. Replace provisional windows with measured distributions. |
Passing physical layout checks, settling in one short transient and meeting a history-independent performance limit require different evidence. Repeat DRC, LVS and STA on any new mask.
<!-- sheet | front | Input stage and ring reservoir capacitors | Follow vinn through Minp0–3 to rp and vinp through Minn0–3 to rn. Rr0 and Rr1 join the source nodes through mid. Each rail has its own grounded MIM. One tail unit stays on vb. Enabled groups select vb and disabled groups select v. v = VDPWR, g = VGND. | Back to the circuit guide · p. 9 -->
<!-- sheet | beta_ref | Bias reference and startup branch | The two left columns form the beta multiplier. Rref0 and Rref1 are in series from rs to ground through refmid. The right column senses vn and drives the vb pull-down through kick. v = VDPWR, g = VGND. | Back to the circuit guide · p. 9 -->
<!-- sheet | stage | One CCRO delay stage | Read the four inverter columns from left to right: main a to y, main b to z, weak y to z, and weak z to y. Cca and Ccb load the two output nodes. rail is the local ring supply, well is the PMOS body and g is VGND. Swapping A/B at the final return would change the differential feedback sign and permit a static latch. Page 16 tests convergence from equal starting voltages in the extracted circuit. | Back to the circuit guide · p. 10 -->
<!-- sheet | cvsl | CVSL receiver, output buffer and dummy load | The first two columns resolve the small ring swing into complementary full-swing nodes l and r. The third column drives out; the fourth presents the matched load on r. v = VDPWR, g = VGND. | Back to the circuit guide · p. 10 -->

# Appendix B | Data and references | Data index, reproduction and references | S P G M T
**Identify each figure by evidence type and use the corresponding records, tool revision and input hash. Attach die ID and capture settings to future silicon results.**
<!-- table | Data in the publishing repository | S P G M T | 32,68 -->
| Location | Contents |
| docs and verification/design_report | English PDF and page-wise source. Use report29.py --out to rebuild. |
| gds, lef, rtl, layout | Final mask, abstract, RTL and routed netlist. Frozen archive has its own SHA256SUMS. |
| decks and results/torture | SPICE stimuli, measurements, solver settings and waveform hashes. Full raw CSV.gz traces are distributed separately. |
| results/design_report | FFT bins, A5 output codes, T3 frames, extracted figures and current estimates. |
| review | Independent analog/tile LVS, state-equivalence proof, connected mask markers and negative controls. |
Analyses used SKY130A model PDK 8afc8346a57fe1ab7934ba5a6056ea8b43078e71, ngspice 42, Icarus 12, OpenSTA 2.4.0 and KLayout. Independent review used KLayout 0.28.16, Xschem 3.4.4, Magic 8.3.684, Netgen 1.5.133 and Yosys 0.33. FFT processing used NumPy and plotting used Matplotlib. The analog model includes extracted capacitance and 5 fF receiver loads; distributed analog metal resistance and nonlinear pad behavior require further study.
<!-- table | Provenance | S P G M T | 30,70 -->
| Field | Interpretation |
| SIGN-OFF / PEX-SIM | Physical checks and connectivity / extracted-device and capacitance SPICE |
| GATE-SIM / MODEL-EST | Routed functional replay or STA / theoretical or behavioral estimate |
| SILICON-TBD | Quantity or procedure awaiting measurement |
| Final GDS / analog PEX | {{gds_sha256}} / {{analog_pex_sha256}} |
<!-- url | Saux et al. (2024): multiphase VCO readout, section IV-B and Fig. 15 | https://arxiv.org/html/2409.15066v1 -->
<!-- url | Texas Instruments ADS127L11: serial timing and output coding | https://www.ti.com/lit/ds/symlink/ads127l11.pdf -->
<!-- url | Texas Instruments ADS890xB: FFT test conditions, Fig. 5-21 | https://www.ti.com/lit/ds/symlink/ads8900b.pdf -->
<!-- url | Analog Devices: coherent sampling and window sampling | https://www.analog.com/en/resources/technical-articles/coherent-sampling-vs-window-sampling.html -->
<!-- url | Digilent Analog Discovery 2: digital voltage and drive modes | https://files.digilent.com/manuals/WaveForms/3.25.1/start3.html -->
<!-- url | Tiny Tapeout demo board: schematics and PMOD by revision | https://github.com/TinyTapeout/tt-demo-pcb -->
The complete layout coordinates are in atlas_index.json and the KLayout marker file atlas_blocks.lyrdb. For the separate nine-page operating-principles guide, open tutorial.pdf.
