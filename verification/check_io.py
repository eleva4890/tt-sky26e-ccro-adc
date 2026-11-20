"""Trace TT pin shapes to physical macro/constant-cell terminals from the placed DEF."""
from collections import defaultdict
from pathlib import Path
import os,re,pya

root=Path("layout/integration")
db=pya.Layout()
db.read(os.environ.get("ADC_IO_GDS",str(root/"tt_um_eleva_ccro_adc.gds")))
top=db.cell("tt_um_eleva_ccro_adc")
cell=db.create_cell("io_geometry")
for m in range(67,72):
    ix=db.layer(m,20)
    cell.shapes(ix).insert(pya.Region(top.begin_shapes_rec(ix)))
    if m<71:
        cut=db.layer(m,44)
        shapes=pya.Region(top.begin_shapes_rec(cut))
        if m==70:shapes-=pya.Region(top.begin_shapes_rec(db.layer(89,44)))
        cell.shapes(cut).insert(shapes)
ext=pya.LayoutToNetlist(pya.RecursiveShapeIterator(db,cell,[]))
met={}
for m in range(67,72):
    met[m]=ext.make_layer(db.layer(m,20),f"m{m}")
    ext.connect(met[m])
for m in range(67,71):
    via=ext.make_layer(db.layer(m,44),f"v{m}")
    ext.connect(met[m],via)
    ext.connect(via,met[m+1])
ext.extract_netlist()
def trace(m,x,y):
    n=ext.probe_net(met[m],pya.DPoint(x/1000,y/1000))
    if n is None:raise ValueError((m,x,y))
    return n.cluster_id
ports={}
for s in top.shapes(db.layer(71,5)).each():
    if s.is_text():
        p=s.text.trans.disp
        ports[s.text.string]=trace(71,p.x,p.y)
assert len(ports)==53
groups=defaultdict(list)
for name,n in ports.items():groups[n].append(name)
shorts=[names for names in groups.values() if len(names)>1]
for names in shorts:print("SHORT",",".join(names))
def pin_centers(path):
    out={}
    for section in path.read_text().split("\n  PIN ")[1:]:
        name=section.split()[0]
        rx=re.search(r"LAYER met(\d) ;\s*RECT ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)",section)
        if rx:
            m,x,y,u,v=rx.groups()
            out[name]=(67+int(m),round(500*(float(x)+float(u))),round(500*(float(y)+float(v))))
    return out
positions=(root/"top_floorplan.def").read_text()
placements={n:(int(x),int(y),rot) for n,model,x,y,rot in re.findall(
    r"(?m)^- (\S+) (\S+) \+ FIXED \( (\d+) (\d+) \) (N|FS) ;",positions)}
pinmaps={"ANA":pin_centers(Path("layout/analog_cells/eleva_adc_analog.lef")),
         "DIG":pin_centers(Path("layout/readout/adc_readout.lef"))}
def terminal(inst,pin):
    dx,dy,rot=placements[inst]
    if inst in pinmaps:
        m,x,y=pinmaps[inst][pin]
    else:
        m,x,y={"LO":(67,1055,1530),"HI":(67,420,1210)}[pin]
    return trace(m,dx+x,dy+(2720-y if rot=="FS" else y))
body=positions.split("END SPECIALNETS")[1].split("END NETS")[0]
failed=[]
checked=0
for row in body.splitlines():
    if not row.startswith("- "):continue
    net=row.split()[1]
    pins=re.findall(r"\( (\S+) (\S+) \)",row)
    results=[ports[p] if inst=="PIN" else terminal(inst,p) for inst,p in pins]
    if len(results)>1:
        checked+=1
        if len(set(results))!=1:failed.append(net)
        print("OPEN" if len(set(results))!=1 else "CONNECTED",net,results)
print(f"TRACE SUMMARY {checked-len(failed)}/{checked} signal connections; {len(shorts)} shorted port groups")
if failed or shorts:raise ValueError(f"opens={failed} shorts={shorts}")
