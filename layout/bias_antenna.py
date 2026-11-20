"""Protect the two metal4 bias-select inputs with substrate-to-N+ antenna diodes."""
import os
from pathlib import Path
import runpy
import pya

source=os.environ["ADC_SOURCE_GDS"]
os.environ.update(ADC_IO_GDS=source, ADC_DIAG_PRINT="0")
trace=runpy.run_path("verification/route_diagnostics.py")
db=pya.Layout()
db.read(source)
top=db.cell("tt_um_eleva_ccro_adc")

def region(layer,dt):
    return pya.Region(top.begin_shapes_rec(db.layer(layer,dt)))
def square(x,y,half):
    return pya.Box(x-half,y-half,x+half,y+half)

taps=(region(65,44)-region(64,20)) & region(94,20)
targets={}
for s in top.shapes(db.layer(71,5)).each():
    if s.is_text() and s.text.string in ("ui_in[3]","ui_in[4]"):
        targets[s.text.string]=trace["probe"](71,s.text.x,s.text.y)
assert len(targets)==2
def blocked(x,y):
    # Allow space for the N implant and tap, local interconnect and stacked vias.
    for layer,dt,pad in [(64,20,1400),(65,20,950),(65,44,850),(66,20,780),(93,44,610),(94,20,1050),
                         (67,20,640),(68,20,540),(69,20,540),(70,20,680),(89,44,1800)]:
        if not top.begin_shapes_rec_overlapping(db.layer(layer,dt),square(x,y,pad)).at_end():
            return True
    return False
def place(net,cluster):
    from collections import Counter
    attempts=Counter()
    candidates=[]
    for s in top.shapes(db.layer(71,20)).each():
        if not s.is_box(): continue
        box=s.box
        vertical=box.height()>3000 and box.width()<=500
        horizontal=box.width()>3000 and box.height()<=500
        if not (vertical or horizontal): continue
        if trace["probe"](71,box.center().x,box.center().y)!=cluster: continue
        start,end=(box.bottom,box.top) if vertical else (box.left,box.right)
        for pos in range(start+500,end-500,500):
            sx,sy=(box.center().x,pos) if vertical else (pos,box.center().y)
            for off in (0,-1250,1250,-2500,2500,-4000,4000,-6000,6000,-8000,8000):
                x,y=(sx+off,sy) if vertical else (sx,sy+off)
                if 1500<x<159500 and 1500<y<224000:
                    candidates.append((abs(off)*3+abs(y-115000),x,y,sx,sy))
    metal4=region(71,20).merged()
    for _,x,y,sx,sy in sorted(set(candidates)):
        attempts["on_net"]+=1
        if blocked(x,y): continue
        attempts["free"]+=1
        if taps.interacting(pya.Region(square(x,y,18000))).is_empty():continue
        attempts["near_tap"]+=1
        # Retain 0.30 um spacing on M4 to every other conductor.
        corridor=pya.Region(pya.Box(min(x,sx)-545,min(y,sy)-545,max(x,sx)+545,max(y,sy)+545))
        local=metal4 & corridor
        own=local.interacting(pya.Region(square(sx,sy,2)))
        if not (local-own).is_empty():continue
        def put(layer,dt,ax,ay,bx,by):
            top.shapes(db.layer(layer,dt)).insert(pya.Box(x+ax,y+ay,x+bx,y+by))
        for layer,dt in [(65,20),(81,23)]: put(layer,dt,-315,-345,315,345)
        put(93,44,-465,-475,465,475)
        for dx in (-185,185):
            for dy in (-170,170):
                put(66,44,dx-85,dy-85,dx+85,dy+85)
        put(67,20,-355,-315,355,315)
        for layer,half in [(67,85),(68,75),(69,100),(70,100)]:
            put(layer,44,-half,-half,half,half)
        for layer in (68,69,70,71):put(layer,20,-245,-245,245,245)
        top.shapes(db.layer(71,20)).insert(pya.Box(min(x,sx)-200,min(y,sy)-200,max(x,sx)+200,max(y,sy)+200))
        print("BIAS PROTECTION",net,x,y,"on",sx,sy,flush=True)
        return
    raise ValueError(f"No diode site for {net}, {attempts}")

for net,cluster in targets.items():place(net,cluster)
out=pya.SaveLayoutOptions()
out.gds2_write_timestamps=False
db.write(os.environ["ADC_OUTPUT_GDS"],out)
