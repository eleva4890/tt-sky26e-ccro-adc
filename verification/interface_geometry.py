"""Form the external capacitive load by removing the analog macro from the final GDS."""
from pathlib import Path
import os
import re
import pya
db=pya.Layout()
db.read("gds/tt_um_eleva_ccro_adc.gds")
top=db.cell("tt_um_eleva_ccro_adc")
insts=[i for i in top.each_inst() if i.cell.name=="eleva_adc_analog"]
assert len(insts)==1 and insts[0].trans==pya.Trans()
insts[0].delete()
tcl=[]
lef=Path("layout/analog_cells/eleva_adc_analog.lef").read_text()
for block in lef.split("\n  PIN ")[1:]:
    name=block.split()[0]
    if not re.fullmatch(r"[pn]\d+",name):continue
    m=re.search(r"LAYER met(\d) ;\s*RECT ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)",block)
    n,ax,ay,bx,by=m.groups()
    px,py=(float(ax)+float(bx))/2,(float(ay)+float(by))/2
    top.shapes(db.layer(67+int(n),20)).insert(pya.Box(*(round(1000*float(v)) for v in (ax,ay,bx,by))))
    tcl.extend([f"box values {px}um {py}um {px}um {py}um",f"label ext_{name} c metal{n}"])
assert len(tcl)==60
Path(os.environ["EXT_TAP_LABELS"]).write_text("\n".join(tcl)+"\n")
out=pya.SaveLayoutOptions()
out.gds2_write_timestamps=False
top.write(os.environ["EXT_TAP_GDS"],out)
