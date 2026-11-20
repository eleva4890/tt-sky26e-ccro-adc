# Analog circuit and design rationale

Start at the top sheet to trace the implemented circuit. The release report gives the component values and operating conditions used for verification. [Xschem hierarchy](../review/xschem/tt_um_eleva_ccro_adc.sch) · [Design report, pp. 6–7](ccro_adc_design_report.pdf)

## Transconductor and bias

Each side has a bank of 40 long-channel PMOS tail units in groups of 1, 4, 15 and 20. The bias decoder connects enabled gates to vb and disabled gates to VDPWR. Independent LVT input PMOS wells follow their respective sources. The P-ring branch senses VIN_N and the N-ring branch senses VIN_P. Two equal high-resistance poly segments link the sources at mid. At zero differential input the degeneration resistor has ideally zero DC drop. At finite current redistribution it reduces the input-stage transconductance and its cubic compression.

| Element | Released value or geometry |
|---|---|
| Tail / input devices | Unit PMOS W/L 1/2 µm. Four LVT PMOS of W/L 6/1 µm per input side. |
| Reference and startup | The NMOS branch uses a 4:1 width ratio. At low vn the weak PMOS raises kick, switching on the vb pull-down. As vn rises, the sense NMOS pulls kick low. |
| Degeneration and reference resistors | Poly width 0.69 µm. Degeneration uses two 80 µm segments, 39.70 kΩ each nominal. Reference uses two 97.1 µm segments, 48.10 kΩ each. The terminal models include end resistance. |
| Ring supply capacitance | One 21.8 × 21.8 µm MIM per rail, nominally 0.965 pF at TT. The mask has no added midpoint MIM. |
| Oscillator | Each of 15 stages has two main and two local cross-coupled inverters. P/N widths 8.4/4.2 and 1.68/0.84 µm respectively, common length 0.55 µm. Straight feedback through the odd stage count. Each node carries a 4.5 × 4.5 µm, 43.45 fF MIM. |
| CVSL receivers | LVT input NMOS 4/0.15 µm and feedback PMOS 0.42/2.4 µm. Matched buffer loads on both receiver outputs preserve symmetry. |

## Headroom and linearity

For differential peak amplitude A, the positive rail must accommodate Vcm + A/2 + VSG(input) + VSD(tail,min). At the other endpoint the ring voltage sets the input device's saturation margin. The early estimate used Vcm = 0.75 V and A = 0.25 V. Extraction established 0.63 V and 0.20 V for the nominal test. Measure hot-corner harmonics at fixed amplitude while increasing Vcm by 50–100 mV to diagnose input-stage headroom. The report records the measured SS tail margin and the open FF distortion test.

Expanding each ring's frequency as a polynomial of normalized current gives even and odd curvature. Even terms cancel for matched branches. With normalized quadratic coefficient c2, fractional gain mismatch ε and modulation x, HD2 amplitude is approximately |ε c2 x|/4. The sign of the cubic coefficient sets whether ring curvature compensates or compounds transconductor compression. A0 fits each current sweep independently at each PVT point. A4 compares the differential DC fit with a dynamic sinusoid. [A0 coefficients](../results/audited/a0_pvt_fit.csv) · [Loaded dynamic harmonics](../results/audited/final_loaded_dynamic.csv)

## Noise and coupling

The noise model combines integrated input noise, assumed oscillator phase noise, phase-count quantization and nonlinear transfer, followed by the actual CIC decimation. Report the bandwidth, window, input tone, seed and oscillator FoM alongside SNDR. Measured silicon phase noise and the PCB supply environment remain necessary to close the budget. [Noise budgets](../results/audited/final_noise_budget.csv)

Ring coupling can travel through rail-to-rail capacitance, the source network, shared return impedance and substrate. Each ring has local rail decoupling. A midpoint capacitor can shunt the resistor midpoint yet leave the other mechanisms active. T5 compares the as-built circuit, a 206.58 fF midpoint MIM variant, and artificial rail coupling. Simulation timestep and startup history affect the apparent lock band at 1 mV. [T5 measurements](torture_T1-T6.md)
