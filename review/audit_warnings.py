"""Locate every Magic extraction feedback marker in the final GDS hierarchy."""
from collections import Counter
from pathlib import Path
import gzip,os,re,runpy,pya
review=Path(__file__).resolve().parent
db=pya.Layout()
db.read(str(review/"inputs/tt_um_eleva_ccro_adc.gds"))
top=db.cell("tt_um_eleva_ccro_adc")
macro=db.cell("adc_readout")
placed=[i for i in top.each_inst() if i.cell_index==macro.cell_index()]
assert len(placed)==1
inst=placed[0]
cells=[(i.cell.name,i.bbox()) for i in macro.each_inst()]
src=gzip.open(review/"logs/magic_extraction_feedback.tcl.gz","rt").read()
rows=re.findall(r'box (-?\d+) (-?\d+) (-?\d+) (-?\d+)\nfeedback add "([^"]+)"',src)
categories=Counter()
outside=[]
for x,y,u,v,msg in rows:
    # The SKY130 Magic tech uses 0.5 centimicron per internal coordinate.
    x,y,u,v=map(int,(x,y,u,v))
    ctr=pya.Point(round((x+u)*2.5),round((y+v)*2.5))
    local=inst.trans.inverted()*ctr
    matches=sorted({name for name,box in cells if box.contains(local)})
    category=" ".join(msg.split()).split(" to node")[0]
    cell="/".join(matches) if matches else "(outside standard-cell boxes)"
    if not matches: outside.append(ctr)
    categories[(category,cell)]+=1
assert len(rows)==int(re.search(r"EXTRACTION_FEEDBACK (\d+)",(review/"logs/magic_tile.log").read_text())[1])
counts=Counter()
for (message,cell),n in categories.items(): counts[message]+=n
with (review/"logs/magic_warnings.txt").open("w") as f:
    print("Magic extraction feedback:",len(rows),file=f)
    for k,n in counts.items():print(n,k,file=f)
    print("\nCount | message | routed standard-cell master at marker center",file=f)
    for (k,cell),n in categories.most_common():print(n,k,cell,sep=" | ",file=f)
    os.chdir(review.parent)
    os.environ["ADC_IO_GDS"]=str(review/"inputs/tt_um_eleva_ccro_adc.gds")
    geom=runpy.run_path("verification/check_io.py")
    for pt in outside:
        cluster=geom["trace"](67,pt.x,pt.y)
        pins=[name for name,n in geom["ports"].items() if n==cluster]
        print(f"Top-level marker center ({pt.x*db.dbu:.3f}, {pt.y*db.dbu:.3f}) um; LI1 probed to {pins}",file=f)

