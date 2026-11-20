"""Query recursive GDS label transforms and metal connectivity in tile coordinates."""
import os, runpy
from pathlib import Path
import pya
review = Path(__file__).resolve().parent
os.chdir(review.parent)
os.environ["ADC_IO_GDS"] = str(review / "inputs/tt_um_eleva_ccro_adc.gds")
env = runpy.run_path("verification/check_io.py")
top, db, ext, met = (env[k] for k in ("top","db","ext","met"))
names = {"rp","rn","sp","sn","mid","vb","ua[0]","ua[1]","VDPWR","VGND","vinp","vinn"}
with (review / "logs/gds_labels.tsv").open("w") as f:
    print("label\tcell\tlayer\tx_um\ty_um\tmetal_cluster", file=f)
    for li in db.layer_indexes():
        it=top.begin_shapes_rec(li)
        info=db.get_info(li)
        while not it.at_end():
            sh=it.shape()
            if sh.is_text() and sh.text.string in names and (sh.text.string not in ("VDPWR","VGND") or it.cell().name==top.name):
                pt=it.trans()*sh.text.trans.disp
                x,y=pt.x*db.dbu,pt.y*db.dbu
                net=ext.probe_net(met[info.layer],pya.DPoint(x,y)) if info.layer in met else None
                print(sh.text.string,it.cell().name,str(info),f"{x:.3f}",f"{y:.3f}",net.cluster_id if net else "-",sep="\t",file=f)
            it.next()
    for y in (2.1,51.39,120,216.9):
        net=ext.probe_net(met[71], pya.DPoint(92.8,y))
        assert net.cluster_id==env["ports"]["VGND"]
        print("VGND-stripe",top.name,"71/20",92.8,y,net.cluster_id,sep="\t",file=f)

