"""Size top-level via landings and fill spacing notches on each connected conductor."""
import os
from pathlib import Path
import pya

db = pya.Layout()
db.read(os.environ.get("ADC_SOURCE_GDS", "layout/integration/tt_um_eleva_ccro_adc.gds"))
top = db.cell("tt_um_eleva_ccro_adc")
base = pya.Layout()
base.read("layout/integration/power_assembly.gds")
power = base.cell("eleva_ccro_power_assembly")
for layer in (69, 70, 71):
    ix=db.layer(layer,20)
    inherited = {str(s) for s in power.shapes(base.layer(layer,20)).each()}
    changed = pya.Region()
    for shape in list(top.shapes(ix).each()):
        if not shape.is_box() or str(shape) in inherited: continue
        box=shape.box
        if box.width()==box.height() and box.width() in (640,680):
            pt=box.center()
            half=245 if layer>=70 else 195
            shape.box=pya.Box(pt.x-half,pt.y-half,pt.x+half,pt.y+half)
        changed.insert(shape.box)
    nearby=changed.sized(350)
    if layer==70:
        nearby-=pya.Region(top.begin_shapes_rec(db.layer(89,44))).sized(1800)
    conductors=pya.Region(top.begin_shapes_rec(ix)).merged()
    for poly in conductors.interacting(pya.Region(top.shapes(ix))).each():
        reg=pya.Region(poly)
        gap=70 if layer==69 else 150
        add=(reg.sized(gap).sized(-gap)-reg) & nearby
        if not add.is_empty(): top.shapes(ix).insert(add)

# Two coincident power feed vias overlap a macro via at each end of the analog bus.
analog=db.cell("eleva_adc_analog")
ix=db.layer(69,44)
for x in (700,82750):
    area=pya.Box(x-300,101400,x+300,101900)
    print("VIA",x,[(str(s.bbox()),s.is_box()) for s in analog.shapes(ix).each_overlapping(area)])
    child=pya.Region()
    for inst in analog.each_inst():
        child+=pya.Region(inst.cell.begin_shapes_rec(ix)).transformed(inst.trans)
    child=child & pya.Region(area)
    shapes=list(analog.shapes(ix).each_overlapping(area))
    for s in reversed(shapes):
        if not (child & pya.Region(s.bbox())).is_empty():
            print("drop redundant via",s.bbox())
            s.delete()
        else: child.insert(s.bbox())
opts=pya.SaveLayoutOptions()
opts.gds2_write_timestamps=False
db.write(os.environ["ADC_OUTPUT_GDS"],opts)
