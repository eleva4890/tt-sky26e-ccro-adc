"""Make the reviewer's coordinate list and matching KLayout markers from GDS probes."""
from pathlib import Path
import csv,pya
review=Path(__file__).resolve().parent
with (review/"logs/gds_labels.tsv").open() as f:
    data=list(csv.DictReader(f,delimiter="\t"))
order=["rp","rn","sp","sn","mid","vb","ua[0]","vinp","ua[1]","vinn","VGND-stripe","VGND"]
desc={"rp":"P-ring supply","rn":"N-ring supply","sp":"P-side input source","sn":"N-side input source","mid":"Degeneration resistor midpoint","vb":"Reference gate bias",
      "ua[0]":"Positive tile input","vinp":"Positive input at analog macro","ua[1]":"Negative tile input","vinn":"Negative input at analog macro",
      "VGND-stripe":"Metal on central vertical stripe","VGND":"Ground terminal of the stripe"}
rows=[r for key in order for r in data if r["label"]==key and (key!="VGND" or r["cell"]=="tt_um_eleva_ccro_adc")]
assert set(r["label"] for r in rows)==set(order)
clusters={k:{r["metal_cluster"] for r in rows if r["label"]==k} for k in order}
assert all(len(v)==1 and "-" not in v for v in clusters.values())
assert clusters["VGND"]==clusters["VGND-stripe"] and clusters["vinp"]==clusters["ua[0]"] and clusters["vinn"]==clusters["ua[1]"]
assert len({next(iter(clusters[k])) for k in ("rp","rn","sp","sn","mid","vb","ua[0]","ua[1]","VGND")})==9
db=pya.ReportDatabase("CCRO review probes")
top=db.create_cell("tt_um_eleva_ccro_adc")
cats={}
table=[]
for r in rows:
    name=r["label"]
    x,y=float(r["x_um"]),float(r["y_um"])
    if name not in cats: cats[name]=db.create_category(name.replace("VGND-stripe","VGND central met4"))
    item=db.create_item(top.rdb_id(),cats[name].rdb_id())
    item.add_value(pya.DBox(x-.25,y-.25,x+.25,y+.25))
    item.add_value(f'{name}  ({x:.3f}, {y:.3f}) um   {r["layer"]}')
    report_name="VGND" if name=="VGND-stripe" else name
    table.append(f'| `{report_name}` | {desc[name]} | {x:.3f} | {y:.3f} | {r["layer"]} | {r["metal_cluster"]} |')
db.save(str(review/"probe_points.lyrdb"))
text="""# KLayout probe coordinates

Open the final GDS in read-only mode from the repository root in WSL. Select a net in the marker database and double-click a marker to zoom to its conductor.

```bash
source review/env.sh
klayout -ne -l "$PDK_ROOT/sky130A/libs.tech/klayout/tech/sky130A.lyp" "$ASSEMBLY_GDS" -m "$review/probe_points.lyrdb"
```

The top cell is `tt_um_eleva_ccro_adc`. Coordinates below are in micrometres relative to the tile origin. The analog macro placement transform has already been applied. Layers 70/5 and 71/5 are met3 and met4 labels. Layer 71/20 is met4 drawing. Each label was probed on its underlying conductor. Cluster IDs are local to this extraction.

| Net | Probe | X (µm) | Y (µm) | GDS layer/datatype | Cluster |
|---|---|---:|---:|---|---:|
"""+'\n'.join(table)+"""

1. Compare the met3 and met4 probes on each ring rail. They agree within each rail and distinguish the two rails.
2. Trace `sp`, `sn`, `mid` and `vb` separately. Cross-reference `front.sch` and `beta_ref.sch`.
3. Match each analog tile pin to the corresponding macro input by cluster ID.
4. Check the central met4 stripe at X = 92.800 µm. All four probes share the top-level VGND cluster.

The metal trace uses LI1 through met4, contacts and vias. A via covered by the MIM capacitor formation layer is excluded from metal connectivity. Magic/Netgen checks the complete transistor-level circuit. [Raw probes](logs/gds_labels.tsv) · [Connectivity](logs/connectivity.log) · [Tile LVS](logs/lvs_tile.txt)
"""
(review/"klayout_checklist.md").write_text(text)
