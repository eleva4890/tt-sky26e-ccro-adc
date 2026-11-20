"""Trace the two supply stripes and the external clock/SPI nets on the release mask."""
import json
import os
from pathlib import Path
import runpy

os.environ["ADC_IO_GDS"]="gds/tt_um_eleva_ccro_adc.gds"
check=runpy.run_path("verification/check_io.py")
top,db,extract,met=[check[k] for k in ("top","db","ext","met")]
import pya

result={}
for s in top.shapes(db.layer(71,5)).each():
    if not s.is_text():
        continue
    pin=s.text.string
    if pin not in ("VDPWR","VGND","clk","uio_out[0]","uio_out[1]","uio_out[2]"):
        continue
    pos=s.text.trans.disp
    net=extract.probe_net(met[71],pya.DPoint(pos.x*db.dbu,pos.y*db.dbu))
    if pin in ("VDPWR","VGND"):
        x=.6 if pin=="VDPWR" else 92.8
        for y in (2.1,51.39,120,216.9):
            assert extract.probe_net(met[71],pya.DPoint(x,y)).cluster_id==net.cluster_id
        result[pin]=dict(stripe_x_um=x,cluster_id=net.cluster_id)
    else:
        boxes=[extract.shapes_of_net(net,layer,True).bbox() for layer in met.values()]
        ymin=min(box.bottom*db.dbu for box in boxes if not box.empty())
        assert ymin>121
        result[pin]=dict(min_y_um=ymin,cluster_id=net.cluster_id)
assert len(result)==6
Path("results/design_report/route_extent.json").write_text(json.dumps(result,indent=2)+"\n")
