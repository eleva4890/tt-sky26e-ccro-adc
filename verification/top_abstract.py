"""Match each of the 53 GDS port rectangles to its DEF location and emit the tile LEF."""
from pathlib import Path
import os,re,pya
root=Path("layout/integration")
name="tt_um_eleva_ccro_adc"
db=pya.Layout()
db.read(os.environ.get("ADC_IO_GDS",str(root/(name+".gds"))))
top=db.cell(name)
text=(root/"top_floorplan.def").read_text().split("PINS 53 ;")[1].split("END PINS")[0]
pins=pya.Region(top.shapes(db.layer(71,16)))
metal=pya.Region(top.begin_shapes_rec(db.layer(71,20)))
claimed=pya.Region()
lines=["VERSION 5.8 ;",'DIVIDERCHAR "/" ;','BUSBITCHARS "[]" ;',"MACRO "+name,
       "  CLASS BLOCK ;","  ORIGIN 0 0 ;","  SIZE 161.000 BY 225.760 ;"]
ports=[]
for n,d,u,l,b,r,t,x,y in re.findall(r"- (\S+) \+ NET \S+ \+ DIRECTION (\S+) \+ USE (\S+)\s+\+ PORT\s+\+ LAYER met4 \( (-?\d+) (-?\d+) \) \( (-?\d+) (-?\d+) \)\s+\+ PLACED \( (\d+) (\d+) \) N",text):
    l,b,r,t,x,y=map(int,(l,b,r,t,x,y))
    box=pya.Box(l+x,b+y,r+x,t+y)
    reg=pya.Region(box)
    if not (reg-metal).is_empty():raise ValueError(n)
    claimed+=reg
    coords=" ".join(f"{v/1000:.3f}" for v in (box.left,box.bottom,box.right,box.top))
    lines += ["  PIN "+n,"    DIRECTION "+d+" ;","    USE "+u+" ;","    PORT","      LAYER met4 ;","        RECT "+coords+" ;","    END","  END "+n]
    ports.append(n)
if len(ports)!=53 or not (claimed^pins).is_empty():raise ValueError("Port layers differ from DEF")
if not pya.Region(top.begin_shapes_rec(db.layer(72,20))).is_empty():raise ValueError("met5 present")
lines.extend(["END "+name,"END LIBRARY"])
(root/(name+".lef")).write_text("\n".join(lines)+"\n")
Path("lef").mkdir(exist_ok=True)
Path("lef",name+".lef").write_bytes((root/(name+".lef")).read_bytes())
print("Verified 53 physical met4 pins against 1x2 DEF, met5 empty")
