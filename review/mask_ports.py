"""Recover the tile's 53 original GDS pin labels before Magic flattens the hierarchy."""
from pathlib import Path
import pya
p=Path(__file__).resolve().parent
layout=pya.Layout()
layout.read(str(p/"inputs/tt_um_eleva_ccro_adc.gds"))
top=layout.cell("tt_um_eleva_ccro_adc")
ports={}
for shape in top.shapes(layout.layer(71,5)).each():
    if shape.is_text():
        name=shape.text.string
        assert name not in ports
        at=shape.text.trans.disp
        ports[name]=(at.x*layout.dbu, at.y*layout.dbu)
assert len(ports)==53
with (p/"inputs/ports.tcl").open("w") as out:
    for i,(name,(x,y)) in enumerate(sorted(ports.items()),1):
        print(f"box values {x:.3f}um {y:.3f}um {x:.3f}um {y:.3f}um\nlabel {{{name}}} c metal4\nport {{{name}}} make {i}",file=out)

