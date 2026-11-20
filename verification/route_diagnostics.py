"""Relate signoff markers to electrical nets on the streamed tile (coordinates in nm)."""
from collections import Counter, defaultdict
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import pya

db = pya.Layout()
db.read(os.getenv("ADC_IO_GDS", "layout/integration/tt_um_eleva_ccro_adc.gds"))
top = db.cell("tt_um_eleva_ccro_adc")
flat = db.create_cell("diagnostic_conductors")
for layer in range(66, 72):
    metal = db.layer(layer, 20)
    flat.shapes(metal).insert(pya.Region(top.begin_shapes_rec(metal)))
    if layer < 71:
        cut = db.layer(layer, 44)
        region = pya.Region(top.begin_shapes_rec(cut))
        if layer == 70:
            region -= pya.Region(top.begin_shapes_rec(db.layer(89, 44)))
        if layer == 66:
            region &= pya.Region(top.begin_shapes_rec(metal))
        flat.shapes(cut).insert(region)
l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(db, flat, []))
metals = {}
for layer in range(66, 72):
    metals[layer] = l2n.make_layer(db.layer(layer, 20), str(layer))
    l2n.connect(metals[layer])
    if layer > 66:
        via = l2n.make_layer(db.layer(layer-1, 44), "via"+str(layer-1))
        l2n.connect(metals[layer-1], via)
        l2n.connect(via, metals[layer])
l2n.extract_netlist()

def probe(layer, x, y):
    net = l2n.probe_net(metals[layer], pya.DPoint(x/1000, y/1000))
    return net.cluster_id if net else 0

labels = defaultdict(set)
for layer in range(66, 72):
    itr = top.begin_shapes_rec(db.layer(layer, 5))
    while not itr.at_end():
        if itr.shape().is_text():
            label = itr.shape().text
            pt = itr.trans() * pya.Point(label.x, label.y)
            labels[probe(layer, pt.x, pt.y)].add(label.string)
        itr.next()

def name(net):
    return "/".join(sorted(labels[net]))[:100] or f"#{net}"

def antenna():
    counts = Counter()
    for ln in Path(os.getenv("ADC_ANTENNA", "results/top_antenna_markers.txt")).read_text().splitlines():
        if ln.startswith("box "):
            a,b,c,d = [5*int(v) for v in ln.split()[1:]]
            counts[name(probe(66,(a+c)/2,(b+d)/2))] += 1
    for k,v in counts.most_common():print("ANTENNA", k,v)

def markers():
    report=ET.parse(os.getenv("ADC_BEOL", "results/top_beol_markers.xml"))
    for item in report.findall(".//items/item"):
        cat=item.findtext("category").strip("'")
        cell=item.findtext("cell")
        value=item.findtext("values/value")
        coords=[round(1000*float(v)) for v in re.findall(r"[-\d.]+",value.split(":")[-1])]
        if len(coords)!=8 or cat[:1]!="m":continue
        layer=67+int(cat[1])
        trans=pya.Trans()
        if cell!=top.name:
            trans=next(i.trans for i in top.each_inst() if i.cell.name==cell)
        pts=[trans*pya.Point(*coords[i:i+2]) for i in range(0,8,2)]
        nets=[]
        for a,b in (pts[:2],pts[2:]):
            x,y=(a.x+b.x)/2,(a.y+b.y)/2
            nets.append(next((n for dx,dy in [(0,0),(2,0),(-2,0),(0,2),(0,-2)] if (n:=probe(layer,x+dx,y+dy))),0))
        yield cat, layer, pts, nets
if os.environ.get("ADC_DIAG_PRINT","1")=="1":
    antenna()
    counts=Counter()
    for cat,layer,pts,nets in markers():
        counts[cat, nets[0]==nets[1]]+=1
        print(cat,*(str(p) for p in pts),*(name(n) for n in nets))
    print("same-net classification",counts)
