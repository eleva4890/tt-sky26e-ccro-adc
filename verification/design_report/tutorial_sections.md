# Tutorial | The conversion chain | How a voltage becomes a time measurement | P G M
**A positive differential input makes one ring run faster and the other slower. The readout measures how much extra phase the faster ring accumulates during the same time interval.**
Apply VIN_P = 0.680 V and VIN_N = 0.580 V. Their average Vcm is 0.630 V and their difference v is +0.100 V. The rings run continuously at nominal bias. The example uses fs = 20 MHz and OSR 128.
<!-- draw | Follow the units from the pins to the word | P M | conversion | The arrows use the TT differential gain of about 6.90 MHz/V. An event is a change of state at one of the 15 observed taps on one ring. The values are steady-state averages. -->
<!-- eq | v = V<sub>IN,P</sub> − V<sub>IN,N</sub>　　V<sub>cm</sub> = (V<sub>IN,P</sub> + V<sub>IN,N</sub>)/2 | ∆f = f<sub>P</sub> − f<sub>N</sub> ≈ Gv　　T<sub>s</sub> = 1/f<sub>s</sub> = 50 ns -->
At zero input both rings run near 3.769 MHz at TT. Over one 50 ns clock interval each advances about 0.188 cycle. Observing 30 events per cycle turns this into about 5.65 events per ring per clock. Subtracting the two counts cancels most of this common activity. An input that speeds both rings equally changes the common frequency but contributes zero ideal differential signal.
In the unlocked linear range, G is the differential gain and Vos the measured zero. Page 6 derives the factor 2,048.
<!-- eq | C<sub>mean</sub> ≈ 2,048 × (30/f<sub>s</sub>) × G × (v − V<sub>os</sub>) -->
<!-- table | Quantities used in this chapter | M | 23,39,38 -->
| Symbol | What it counts | Where it is observed |
| fP, fN | Cycles/s of each complete ring | Divided tap outputs ×64 in debug mode 10 |
| dP, dN | Integer transitions since the preceding sample | Two 4-bit fields in debug mode 01 |
| x[n] = dP − dN | Signed events per sample clock | Input to the first digital accumulator |
| R, C[m] | Clocks per output word, signed output code | R = 128 or 256, one word per SPI frame |
<!-- note | Reading path | Follow voltage into phase on pp. 2–3, then into counts and codes on pp. 4–6. Reconstruct a word on p. 7 and test the operating limits on pp. 8–9. -->

# Tutorial | Voltage to current | How the crossed PMOS pair steers current | P M
**Two matched current-source banks feed the source nodes sp and sn. The resistor between these nodes lets a differential input redistribute current between the two oscillators.**
<!-- draw | Differential half-circuit variables | P M | differential | Each idealized bank supplies IB. The left PMOS gates sense VIN_N and feed rp. The right gates sense VIN_P and feed rn. The complete devices and their body connections are on report page 25. -->
Increase VIN_P and decrease VIN_N equally. On the P branch the gate falls, the PMOS source-to-gate voltage initially increases, and more current flows into rp. As sp falls relative to sn, current flows from sn through the resistor toward sp. That source motion reduces the original change in source-to-gate voltage. This local feedback is source degeneration.
<!-- eq | ∆I = I<sub>P</sub> − I<sub>N</sub> = (v<sub>sn</sub> − v<sub>sp</sub>)/R<sub>D</sub> | ∆I ≈ g<sub>m</sub>(v + v<sub>sp</sub> − v<sub>sn</sub>)　　 ∆I/v ≈ g<sub>m</sub>/(1 + g<sub>m</sub>R<sub>D</sub>) -->
Here RD = 39.70 kΩ is one half of the 79.40 kΩ source-to-source resistor. Each branch current changes by half of ∆I, which accounts for the factor of two. The gm is the combined small-signal transconductance of the four parallel devices on one side. The derivation assumes matched devices, constant bank currents and adequate saturation headroom. Higher RD reduces gain and its sensitivity to gm.
<!-- table | Where the operating current comes from | P M | 30,70 -->
| Element | Role in the bias loop |
| Reference, report page 26 | A PMOS mirror makes the two NMOS branch currents approximately equal. The wider 8/2 NMOS needs less VGS than the 2/2 NMOS. Their VGS difference appears across 96.21 kΩ, setting the finite-current operating point. |
| Startup branch | At low vn, Mweak raises kick. Mkick pulls vb down and turns on the PMOS mirror. As vn rises, Msense discharges kick and releases the startup pull-down. |
| Bias selection | The four settings 00, 01, 10 and 11 enable 20, 1, 5 and 40 units per side. Selection moves the ring working point. The current-to-frequency slope and linear input range must be checked there. |
<!-- note | Connecting the two gains | Differential voltage gain in Hz/V is the product of current steering in A/V and the local current-to-frequency slope in Hz/A under symmetric operation. The loaded PEX secant gives 6.900 MHz/V at TT for ±160 mV (report p. 8). -->

# Tutorial | Current to phase | Why the oscillator has 30 events per cycle | P M
**A ring of 15 inverting stages returns an edge to its starting node with opposite polarity after one trip. A second trip completes a cycle.**
A stage must move charge before its output crosses the following stage's threshold. With effective load Ceff, voltage excursion ∆V and effective charging current Ieff, moving Q ≈ Ceff × ∆V takes about Q/Ieff seconds. A larger drive current generally shortens the delay around the nominal working point. The local rail and the voltage swing also respond to the input.
<!-- eq | t<sub>d</sub> ≈ C<sub>eff</sub> ∆V/I<sub>eff</sub>　　T ≈ 2N t<sub>d</sub>　　f ≈ 1/(2N t<sub>d</sub>) -->
<!-- draw | Edge propagation in one idealized ring | M | ring_edges | a[0] and b[0] are complementary nodes of one stage. The next main inverter makes a[1] the delayed inverse of a[0]. One division between the first two nearby edges is one stage delay. The diagram assumes equal delays. -->
With N = 15 and f = 3.769 MHz, T ≈ 265.3 ns and average td ≈ 8.84 ns. Each of the 15 observed tap outputs rises once and falls once per period, giving 30 events. Their average spacing is T/30. Sustained oscillation also requires enough loop gain near startup. The 43.45 fF MIM at each stage loads a switching node. The separate 0.965 pF MIM on each ring supply reduces rail ripple. The event order interleaves rising edges from some stages with falling edges from others.
<!-- table | Two different uses of differential signals | P | 29,71 -->
| Signals | Physical meaning |
| a[k], b[k] within one ring | Two main paths propagate around the same 15 stages. A weak inverter pair at each stage reinforces complementarity. Weak-to-main device width is 1/5. T1 tests startup from equal initial voltages (report p. 16). |
| fP, fN across two rings | Two complete oscillators have separate local supplies rp and rn. Their relative phase is free to drift when their frequencies differ. This relative drift encodes the input voltage. |
Each CVSL receiver compares a and b. A high a pulls l down, the opposite PMOS drives r up, and the following inverter drives the tap high. The 1.8 V receiver provides a logic-level edge to the synchronizer. A matched dummy inverter on r balances the load. report Pages 27–28 give the complete Xschem sheets.

# Tutorial | Sampling phase | Reading an asynchronous ring on a clock edge | P G
**A tap vector is a set of logic levels. Comparing it with the preceding vector reveals the positions that changed during one sample interval.**
Each of the 30 full-swing tap signals passes through two flip-flops clocked by fs. The readout keeps the preceding synchronized vector. An XOR produces a one wherever the new and old values differ. A population count sums the ones on each 15-bit side. Two synchronization stages reduce the probability of propagating metastability. Different taps can still be assigned to adjacent sample intervals.
<!-- draw | Count the changed taps in a stored PEX trace | P G | tap_grid | Columns are tap indices 14 down to 0. Rows 958 and 959 are 50 ns apart in step_taps.csv. The XOR rows are aligned to the original tap samples before the two-clock digital delay. -->
At tick 959 the P side changes from 0x555A to 0x52AA. Its XOR mask 0x07F0 has seven ones. The N side changes from 0x2AAD to 0x2AD5. Its mask 0x0078 has four. The signed input x[959] is +3. The next tick gives six changes on each ring and x[960] = 0, even though the input voltage has remained fixed.
<!-- eq | d<sub>P</sub>[n] = popcount(P[n] XOR P[n−1])　　x[n] = d<sub>P</sub>[n] − d<sub>N</sub>[n] -->
<!-- note | When the count loses information | A single tap that goes from 0 to 1 and back to 0 between samples gives XOR = 0. Exactly two missed events can therefore resemble a quiet tap. For an ideal 50% duty cycle require fs > 2 fmax. In hardware Ts must be shorter than the shortest high or low pulse, allowing margin for clock and edge uncertainty. WRAP_ERR sets at observed dP or dN ≥14 and cannot detect every lost pair. -->
DBG_MODE=01 exposes the observed counts. DBG_MODE=10 exposes fP/64 and fN/64. Sweep the intended input range in divider mode first, then compare the mean raw count with 30 f/fs on each side. A discrepancy helps localize a problem before the CIC or serializer.

# Tutorial | Phase quantization | Where first-order noise shaping comes from | M
**The ring keeps the fractional part of its phase between samples. A transition assigned late to one interval can be counted in the next.**
Let q(t) be the unwrapped ideal phase of one ring in tap-event units. Every oscillator cycle advances q by 30. In the equal-spacing model the count of completed events is Q[n] = floor(q(nTs)). Define e[n] = Q[n] − q(nTs), so −1 < e[n] ≤ 0. Assume every intervening tap event is recovered.
<!-- eq | q(t) = q(0) + 30 ∫<sub>0</sub><super>t</super> f(u) du | d[n] = Q[n] − Q[n−1] = 30 ∫<sub>(n−1)Ts</sub><super>nTs</super> f(u) du + e[n] − e[n−1] -->
<!-- draw | A fractional advance generates integer counts | M | phase_steps | One ideal ring advances 5.25 events every clock. The straight line is continuous phase. The staircase holds the sampled integer phase. Successive differences are 5, 5, 5 and 6. Their mean is exactly 5.25. -->
Summing d[n] over L clocks cancels all interior error terms. Only e[L] − e[0] remains. Dividing by L bounds the single-ring average-count error below 1/L event per clock in this model. Subtracting two rings applies the same difference operator to eP − eN and gives a bound below 2/L.
<!-- eq | NTF(z) = 1 − z<super>−1</super>　　abs(NTF) = 2 abs(sin(πf/f<sub>s</sub>)) -->
This noise transfer function has a zero at DC. At low frequency its magnitude grows in proportion to f, so slowly varying phase-quantization error is suppressed. The floor example is periodic and can create discrete tones. A white error spectrum is an additional statistical assumption.
The derivation addresses phase quantization. Device noise and period jitter perturb the physical phase before quantization, and ring coupling can change the underlying frequency difference. These mechanisms need separate evidence, as in the spectral and locking tests on report pages 15 and 18.
<!-- url | M. A. Straayer, MIT · Noise shaping using voltage-controlled oscillators | https://dspace.mit.edu/entities/publication/3460fb83-7ac6-4f7f-80ba-5eb7d17b4c1a -->

# Tutorial | Decimation | Deriving the CIC2 weights and code scale | G M
**Two accumulators collect count differences at fs. At every Rth clock, two successive differences of the sampled accumulator recover a triangular weighted sum.**
For an input x[n], the first accumulator adds x on every clock. The second adds the previous first-accumulator value. At the low rate, each comb subtracts its previous input word. A single integrator followed by a delayed difference sums R consecutive inputs. Cascading that pair twice convolves two length-R rectangular windows. The expression below refers to the high-rate filter before decimation. A second-order CIC has two averaging stages. The first-order phase error on p. 5 comes from a single difference in the VCO readout.
<!-- eq | H(z) = [(1 − z<super>−R</super>)/(1 − z<super>−1</super>)]<super>2</super> = (1 + z<super>−1</super> + … + z<super>−(R−1)</super>)<super>2</super> | h[k] = R − abs(k − (R−1)),　0 ≤ k ≤ 2R−2 -->
<!-- draw | Unnormalized weights for the teaching case R = 4 | M | triangle | Two windows [1,1,1,1] produce seven weights with sum 16. The midpoint at k = 3 gives a delay of three input clocks. In the chip the corresponding midpoint is R−1. -->
For constant input x, the raw output is R²x. For a sinusoid at frequency f the normalized amplitude is [sin(πRf/fs)/(R sin(πf/fs))]². Zeros occur at nonzero multiples of fs/R below fs. Attenuation between the zeros is finite, so out-of-band energy can fold into the output band during decimation. report Page 5 plots the passband.
<!-- table | Exact scaling in the implemented readout | G M | 16,18,24,20,22 -->
| R | DC gain R² | Output slice | Scale per x | Group delay at 20 MHz |
| 128 | 16,384 | work[18:3], ÷8 | 2,048 | 6.35 µs |
| 256 | 65,536 | work[20:5], ÷32 | 2,048 | 12.75 µs |
The 21-bit accumulators can wrap modulo 2²¹. The comb subtracts in the same arithmetic. The largest settled raw magnitude is 15 × 256² = 983,040, inside the signed 21-bit range. The output slice discards low bits, equivalent to rounding down a signed value. A sustained x = −1 gives −2,048 at either OSR.
<!-- url | E. B. Hogenauer, IEEE (1981) · Cascaded integrator–comb filters | https://doi.org/10.1109/TASSP.1981.1163535 -->

# Tutorial | Worked conversion | Reconstruct one complete SPI word | P G M
**For the +100 mV input step, the saved tap samples predict +2,121. The routed serial output independently returns the same 16 bits.**
Start with the small-signal estimate. Differential gain G ≈ 6.90 MHz/V gives ∆f ≈ 0.690 MHz, or 30 × 0.690/20 = 1.035 extra P events per 50 ns clock. The DC conversion is 2,048 × 1.035 = 2,119.68 codes. The measured tap sequence lets us compute the integer result for a particular frame.
<!-- table | Follow the indexed data at OSR 128, reset delay 0 | P G | 27,73 -->
| Step | Calculation from step_taps.csv and step_spi_words.csv |
| 1. Locate the frame | CS_N falls at tick 995 and rises at 1059. The decimation terminal was 97 clocks before close. The taps took two clocks to reach the accumulator, so the newest raw interval is 1059 − 97 − 2 = 960. |
| 2. Build the window | Use ticks 706–960 inclusive. Compute all 255 signed XOR counts as on p. 4. Apply weights 1, 2, …, 128, …, 2, 1. The first and last weights are both 1. |
| 3. Slice the word | The integer weighted sum is 16,969. Divide by 8 and discard the remainder. The transmitted code is +2,121 with remainder 1. |
<!-- draw | Bits seen on successive rising edges of SCLK | G | serial_word | Select is active low. The receiver reads D15 first and D0 last. Grouping the actual result into nibbles gives 0x0849, which equals 2,121 in decimal. -->
At 20 MHz, SCLK = 5 MHz. The first rising edge is two input clocks after select. The sixteenth is at +62 clocks, and CS_N rises at +64. This frame therefore completes at 52.950 µs. Relative to the input midpoint at 34.025 µs the time is 18.925 µs. A different frame phase gives another settling time (report p. 5).
Using the nominal slope and Vos = 0, the inverse conversion gives 2,121 × 20 MHz / (2,048 × 30 × 6.90 MHz/V) = 100.06 mV. In the lab, use the measured offset and slope for that clock and bias.
For a negative example, the clean T3 capture in a different test gives 0xF70D. Its unsigned value is 63,245. Subtract 65,536 to recover −2,291. The decoded sign should reverse when the differential inputs are exchanged, outside the measured offset and lock region.
<!-- note | Independent arithmetic check | The report build recomputes every eligible post-step frame with a full post-reset window from the stored taps, then compares it with the decoded gate output. All 47 frames at OSR 128 and 20 at OSR 256 agree. The tapped data and the gate words share the same analog simulation. -->

# Tutorial | Conversion accuracy | Reading harmonics and noise at the output | P M T
**A small deviation from linear frequency gain can create a visible spectral line even when a DC transfer curve looks straight. Random timing variations spread energy around the lines.**
Around a chosen bias point write ∆f(v) ≈ a0 + a1v + a2v² + a3v³. In symmetric branches with their inputs exchanged, ideally ∆f(−v) = −∆f(v). The constant and even terms cancel in the differential output. Device mismatch, unequal loading and common-mode modulation can leave offset and HD2. Cubic compression survives the subtraction.
<!-- eq | u = 2πft　　v(t) = A sin(u)　　sin<super>3</super>(u) = [3 sin(u) − sin(3u)]/4 | HD3 ≈ 20 log<sub>10</sub>(abs(a<sub>3</sub>) A<super>2</super>/(4 abs(a<sub>1</sub>)))　dBc -->
The approximation assumes a small cubic term, negligible higher orders and a fundamental dominated by a1. Doubling the input amplitude multiplies the third-harmonic-to-fundamental ratio by four, about +12 dB. A CIC attenuates the two frequencies differently. After decimation the third harmonic can also alias, so compare spectra at the same node, amplitude and bandwidth.
<!-- table | What each observation says about the converter | P M | 26,74 -->
| Observation | Physical interpretation |
| HD3, −62.64 dBc | Loaded TT analog transient, 50 kHz at ±200 mV. The third-harmonic amplitude is about 0.074% of the fundamental. This is a property of the reconstructed differential frequency under that stimulus. |
| SNR / SNDR / SFDR | SNR compares the tone power with noise. SNDR includes harmonics in the residual. SFDR compares the tone with the largest spur. The FFT window, excluded bins and output bandwidth on report p. 15 define the reported model values. |
| DC code spread | At +50 mV the model gives 1.476 codes rms. With 47.20 µV/code this is 69.65 µV rms. A constant input has no fundamental, so a code histogram gives a direct measure of repeatability. |
Timing jitter changes the interval between physical crossings. Front-end noise perturbs instantaneous frequency. A source with nearly constant absolute voltage noise gives poorer relative SNR as the tone gets smaller. At larger amplitude deterministic harmonics can dominate. At 10.010 kHz the best of the 11 modeled amplitudes is −1 dBFS (report p. 7).
<!-- note | Interpreting the output word | Sixteen transmitted bits define a signed format. At nominal clock the usable ±200 mV span covers about 8,474 codes. Noise-free resolution depends on this span and the DC spread, while sinusoidal ENOB depends on an explicitly defined dynamic measurement. -->

# Tutorial | Limits and self-checks | When comparable frequencies conceal the input | P G M T
**The same zero code can arise from equal input voltages, oscillator locking or sampling too slowly. Observing both ring frequencies and the raw counts distinguishes these mechanisms.**
Let p(t) denote relative phase in radians. For independent rings its slope is 2π∆f. A simplified weak-coupling model adds a periodic correction with strength K in rad/s. If the natural frequency separation is small enough, the coupling can balance it. Then p(t) remains bounded and the two mean frequencies approach each other.
<!-- eq | dp/dt = 2π∆f<sub>free</sub> − K sin(p) -->
This model explains why a proportional response can flatten around zero. A stationary solution requires the magnitude of the free-running angular frequency difference to be at most K. K has not been fitted for this chip. At 1 mV, nominal gain predicts about 6.9 kHz of separation. One long T5 trajectory with the extracted coupling of 4.1989 fF gave only about 0.060 kHz. The result depends on startup history and numerical timestep (report p. 18). On silicon, find the measured zero Vos and sweep around it in both directions while recording the two dividers.
<!-- table | Three checks using the equations | P G M | 38,62 -->
| Predict before reading the answer | Answer and bench implication |
| Keep the voltage fixed and change fs from 20 to 32 MHz. What happens to the DC code? | The scale is proportional to 1/fs. A nominal +2,120 at 20 MHz becomes about +1,325 at 32 MHz for the same differential frequency. Recalibrate codes per volt after changing the clock. |
| Keep fs fixed and change R from 128 to 256 between captures. Does DC gain double? | Both slices give the same DC gain, 2,048 per mean event/clock. Output rate falls from 156.25 to 78.125 kS/s and the triangular window length grows from 255 to 511 raw intervals. Discard startup frames after reconfiguration. |
| One positive count error enters the first accumulator. How long does its effect last? | Its raw-rate impulse response has 2R−1 weights and can reach at most two decimated output samples. The first accumulator may retain a constant difference and the second a ramp. Two comb differences cancel that ramp once the finite response has passed. |
<!-- note | Choose the observation that addresses the symptom | Nearly equal divided frequencies during a Vos sweep point toward locking or offset. Normal, separated ring frequencies with low observed transition counts point toward sampling loss. Correct raw counts and incorrect serial words call for checking frame alignment, signed decoding and the clock at the receiver. -->
<!-- url | R. Adler, Proceedings of the IRE (1946) · Oscillator phase locking | https://ieeexplore.ieee.org/document/1697085/ -->
