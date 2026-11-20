# KLayout probe coordinates

Open the final GDS in read-only mode from the repository root in WSL. Select a net in the marker database and double-click a marker to zoom to its conductor.

```bash
source review/env.sh
klayout -ne -l "$PDK_ROOT/sky130A/libs.tech/klayout/tech/sky130A.lyp" "$ASSEMBLY_GDS" -m "$review/probe_points.lyrdb"
```

The top cell is `tt_um_eleva_ccro_adc`. Coordinates below are in micrometres relative to the tile origin. The analog macro placement transform has already been applied. Layers 70/5 and 71/5 are met3 and met4 labels. Layer 71/20 is met4 drawing. Each label was probed on its underlying conductor. Cluster IDs are local to this extraction.

| Net | Probe | X (µm) | Y (µm) | GDS layer/datatype | Cluster |
|---|---|---:|---:|---|---:|
| `rp` | P-ring supply | 90.100 | 44.460 | 71/5 | 13 |
| `rp` | P-ring supply | 20.450 | 67.200 | 70/5 | 13 |
| `rn` | N-ring supply | 88.900 | 45.450 | 71/5 | 12 |
| `rn` | N-ring supply | 102.500 | 67.200 | 70/5 | 12 |
| `sp` | P-side input source | 14.000 | 35.550 | 71/5 | 10 |
| `sn` | N-side input source | 64.000 | 36.540 | 71/5 | 11 |
| `mid` | Degeneration resistor midpoint | 62.000 | 41.490 | 71/5 | 7 |
| `vb` | Reference gate bias | 3.700 | 40.500 | 71/5 | 14 |
| `ua[0]` | Positive tile input | 152.260 | 0.500 | 71/5 | 17 |
| `vinp` | Positive input at analog macro | 85.300 | 46.440 | 71/5 | 17 |
| `ua[1]` | Negative tile input | 132.940 | 0.500 | 71/5 | 18 |
| `vinn` | Negative input at analog macro | 84.100 | 47.430 | 71/5 | 18 |
| `VGND` | Metal on central vertical stripe | 92.800 | 2.100 | 71/20 | 38 |
| `VGND` | Metal on central vertical stripe | 92.800 | 51.390 | 71/20 | 38 |
| `VGND` | Metal on central vertical stripe | 92.800 | 120.000 | 71/20 | 38 |
| `VGND` | Metal on central vertical stripe | 92.800 | 216.900 | 71/20 | 38 |
| `VGND` | Ground terminal of the stripe | 92.800 | 216.500 | 71/5 | 38 |

1. Compare the met3 and met4 probes on each ring rail. They agree within each rail and distinguish the two rails.
2. Trace `sp`, `sn`, `mid` and `vb` separately. Cross-reference `front.sch` and `beta_ref.sch`.
3. Match each analog tile pin to the corresponding macro input by cluster ID.
4. Check the central met4 stripe at X = 92.800 µm. All four probes share the top-level VGND cluster.

The metal trace uses LI1 through met4, contacts and vias. A via covered by the MIM capacitor formation layer is excluded from metal connectivity. Magic/Netgen checks the complete transistor-level circuit. [Raw probes](logs/gds_labels.tsv) · [Connectivity](logs/connectivity.log) · [Tile LVS](logs/lvs_tile.txt)
