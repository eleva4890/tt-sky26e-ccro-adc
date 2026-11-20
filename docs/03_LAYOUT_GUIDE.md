# Layout and area guide

The released tile occupies 161.00 × 225.76 µm. Its outline and external pins follow the SKY130A 1×2 analog template. Coordinates below are in micrometres from the lower-left corner at top-cell level. [Final GDS](../gds/tt_um_eleva_ccro_adc.gds) · [KLayout probe locations](../review/klayout_checklist.md)

## Floorplan and area

The analog macro occupies 161 × 121 µm starting at (0, 0). The input stage and reference sit below the oscillators, followed by their level shifters. The digital readout occupies 150 × 100 µm starting at (4.25, 125.76). Buffers drive 30 phase taps toward the digital boundary. The preliminary height allocation was 100 µm digital, 5 µm guard separation, 20 µm CVSL, 45 µm rings, 45 µm transconductor/reference and 10 µm reserve.

The first area estimate assumed about 227 flops, 5,150 µm² of sequential cells and 3,560 µm² of combinational logic. With clock-tree and hold repair the projected cell area was 9,100–9,600 µm². The routed implementation uses 8,964 µm² excluding filler against a 9,000 µm² budget. The digital macro reaches its 100 µm height limit. The independent state mapping covers 235 flops and four latches. [Formal and physical review](../review/SUMMARY.md)

## Supply, shielding and matching

Use the template met4 supply pins and keep routing below met5. The visible central vertical stripe is VGND, centered at X = 92.80 µm. The VDPWR stripe is centered at X = 0.60 µm. Both are 1.20 µm wide and span Y = 2–217 µm. The external clock stays above Y = 169.535 µm and the SPI signals above Y = 200.005 µm. The 30 phase-tap outputs cross the partition.

The floorplan aims for separate ring returns, local rail decoupling, short receiver routes and minimum parallel runs between opposite ring rails or oscillator nodes. The original planning rules called for a 3–5 µm central p+ guard structure, common device orientation, translated ring copies and matched interleaved stage routing. Guard geometry alone does not establish isolation. The extracted direct coupling between rp and rn is 4.1989 fF. [Extracted coupling and sensitivity test](torture_T1-T6.md)

Use the SKY130 M3 MIM option compatible with the met4 ceiling. Keep MIM access clear of template stripes. Use separate wells for source-tied PMOS input devices and inspect well spacing and contacts. Route input metal to the gate with antenna effects checked on the final mask. [Antenna report](../results/top_antenna.txt)

## Review on the final mask

1. Open the released GDS and the review markers. Follow both analog pads to the input gates and identify sp, sn, mid, rp, rn and vb.
2. Trace supply contacts and the central strap. Check the external clock and SPI route extents against the analog boundary.
3. Verify the top template, allowed layers, all external pin labels, LEF agreement and 64 signal paths. Check the extracted analog against the Xschem netlist and the full tile against the integration hierarchy. [Review commands](../review/SUMMARY.md)
