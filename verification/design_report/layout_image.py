"""Render selected actual GDS layers at fixed scale. Run with klayout -b -r."""
from pathlib import Path
import os, sys, json, hashlib
import pya
if os.environ.get("REPORT_SITE"):sys.path.append(os.environ["REPORT_SITE"])
from PIL import Image, ImageDraw
root=Path.cwd()
out=root/"results/design_report/figures";out.mkdir(parents=True,exist_ok=True)
gds=root/"gds/tt_um_eleva_ccro_adc.gds"
layout=pya.Layout();layout.read(str(gds))
top=layout.cell("tt_um_eleva_ccro_adc")
assert top is not None
dbu=layout.dbu
layers=[(65,20,"#3d624e","diff"),(66,20,"#d86f57","poly"),(67,20,"#765987","li1"),
        (68,20,"#307391","met1"),(69,20,"#ddae56","met2"),(70,20,"#57a794","met3"),(71,20,"#9689ba","met4")]
def render(name,roi,scale):
    x0,y0,x1,y1=roi;w,h=round((x1-x0)*scale),round((y1-y0)*scale)
    bg=Image.new("RGB",(w,h),"#102331"); pen=ImageDraw.Draw(bg)
    area=pya.Box(*[round(v/dbu) for v in roi]);counts={}
    for num,dt,color,label in layers:
        it=top.begin_shapes_rec_overlapping(layout.layer(num,dt),area)
        n=0
        while not it.at_end():
            sh=it.shape()
            if sh.is_box():poly=pya.Polygon(sh.box)
            elif sh.is_polygon():poly=sh.polygon
            elif sh.is_path():poly=sh.path.polygon()
            else:it.next();continue
            poly=poly.transformed(it.trans())
            coords=[(round((p.x*dbu-x0)*scale),h-round((p.y*dbu-y0)*scale)) for p in poly.each_point_hull()]
            if len(coords)>2:pen.polygon(coords,fill=color)
            n+=1;it.next()
        counts[label]=n
    bg.save(out/(name+".png"))
    return dict(roi_um=roi,pixels_per_um=scale,drawn_shapes=counts)
stats={n:render(n,b,s) for n,b,s in [("gds_tile",[0,0,161,225.76],10),("gds_ring_detail",[1,86,28,114],40)]}
stats["gds_sha256"]=hashlib.sha256(gds.read_bytes()).hexdigest()
stats["layers"]=[dict(gds_layer=n,datatype=d,color=c,name=k) for n,d,c,k in layers]
(out/"geometry.json").write_text(json.dumps(stats,indent=2)+"\n")
print(stats)
