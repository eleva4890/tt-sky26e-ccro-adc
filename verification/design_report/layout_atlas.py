"""Render circuit-by-circuit views of the frozen GDS and locate routed logic in DEF."""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import klayout.db as k
from klayout.rdb import ReportDatabase
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Patch, Rectangle
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BUNDLE = (HERE.parent / "design/gds").is_dir()
ROOT = HERE.parent / "design" if BUNDLE else HERE.parents[1]
OUT = HERE.parent / "figures" if BUNDLE else ROOT / "results/design_report/figures"
TOP = "tt_um_eleva_ccro_adc"
EXPECTED = "3d8a8502549ad4229debe27ae7c428059759af6e9657fcf2ff3c616e27a74d25"
GDS = ROOT / "gds" / (TOP + ".gds")
DEF = ROOT / "layout/readout/adc_readout.def"
MAPPING = ROOT / "review/digital/state_mapping.tsv"
PALETTE = {
    "NW": (64, 20, "#d8e5f7"), "ACT": (65, 20, "#55ad92"), "TAP": (65, 44, "#8a5b98"),
    "POLY": (66, 20, "#e09773"), "CONT": (66, 44, "#374c56"), "R-ID": (66, 13, "#ce6954"),
    "M1": (68, 20, "#aac6d4"), "M2": (69, 20, "#598bb2"), "M3": (70, 20, "#8e86ae"),
    "M4": (71, 20, "#348b8b"), "CAPM": (89, 44, "#dfb45b"),
}
FE = ("NW", "ACT", "TAP", "POLY", "CONT")
UP = ("M2", "M3", "M4", "CAPM")
COLORS = ("#177d75", "#b75534", "#5c63a2", "#aa7a0a")
plt.rcParams.update({"font.size": 12, "axes.titlesize": 14, "axes.titleweight": "bold",
                     "axes.edgecolor": "#a9b8bf", "text.color": "#233d48",
                     "xtick.color": "#526573", "ytick.color": "#526573", "font.family": "DejaVu Sans"})

def digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def coords(box):
    return [v / 1000 for v in (box.left, box.bottom, box.right, box.top)]

def rect(ax, box, text=None, color="#204b65"):
    x,y,u,v = box
    ax.add_patch(Rectangle((x,y),u-x,v-y,fill=False,edgecolor=color,linewidth=1.35))
    if text:
        label(ax,(x+u)/2,(y+v)/2,text)

def label(ax,x,y,text):
    ax.text(x,y,text,ha="center",va="center",fontsize=11,fontweight="bold",color="#183843",
            bbox=dict(boxstyle="round,pad=.13",fc="#ffffff",ec="#8099a0",lw=.65,alpha=.94))

class Atlas:
    def __init__(self):
        assert digest(GDS) == EXPECTED
        self.layout = k.Layout()
        self.layout.read(str(GDS))
        assert self.layout.dbu == .001
        self.top = self.layout.cell(TOP)
        self.analog = self.layout.cell("eleva_adc_analog")
        self.digital = self.layout.cell("adc_readout")
        assert coords(self.top.bbox()) == [0,0,161,225.76] and not list(self.analog.each_inst())
        placements = {i.cell.name:i.trans for i in self.top.each_inst()}
        assert placements[self.analog.name] == k.Trans()
        self.dx = placements[self.digital.name].disp.x
        self.dy = placements[self.digital.name].disp.y
        assert placements[self.digital.name] == k.Trans(4250,125760)
        self.views = {}
        self.groups = defaultdict(list)
        self.cells = {}
        self.probes = {}
        self.geometry = {}
        self.load_cells()
        self.check_analog()

    def layer(self,name):
        layer,dt,_ = PALETTE[name]
        return self.layout.layer(layer,dt)

    def load_cells(self):
        # The standard-cell boundary excludes well or implant overhang outside a placement site.
        boundary = self.layout.layer(236,0)
        def cell_box(cell):
            b = cell.bbox(boundary)
            return cell.bbox(self.layout.layer(81,4)) if b.empty() else b
        outlines = Counter()
        for inst in self.digital.each_inst():
            b = cell_box(inst.cell).transformed(inst.trans)
            outlines[(inst.cell.name,b.left,b.bottom,b.right,b.top)] += 1
        src = DEF.read_text().replace("\\","")
        pattern = r"^\s*- (\S+) (sky130_\S+) .*?\+ (?:PLACED|FIXED) \( (\d+) (\d+) \) (\w+) ;"
        orients = {"N":k.Trans.R0,"S":k.Trans.R180,"FN":k.Trans.M90,"FS":k.Trans.M0}
        transforms = Counter((i.cell.name,i.trans.rot,i.trans.disp.x,i.trans.disp.y) for i in self.digital.each_inst())
        for name,master,x,y,orient in re.findall(pattern,src,re.M):
            x,y = int(x),int(y)
            base = cell_box(self.layout.cell(master))
            trans = k.Trans(orients[orient],0,0)
            b = base.transformed(trans)
            key = (master,x,y,x+b.width(),y+b.height())
            placement = (master,trans.rot,x-b.left,y-b.bottom)
            assert outlines[key] and transforms[placement], (name,master,x,y,orient)
            outlines[key] -= 1
            transforms[placement] -= 1
            self.cells[name] = [v/1000 for v in (x+self.dx,y+self.dy,x+self.dx+b.width(),y+self.dy+b.height())]
            if master.endswith(("__fa_1","__fa_2")):
                group = name.split(".")[0]
                if group in ("pn","pp","add1","add2"):
                    self.groups[group].append(name)
        assert len(self.cells) == 2187 and sum(outlines.values()) == sum(transforms.values()) == 0
        with MAPPING.open() as f:
            for row in csv.DictReader(f,delimiter="\t"):
                alias = row["RTL alias"].split("[")[0]
                if alias.endswith(".latched"):
                    # Yosys gives the latch inside each ICG a generated name.
                    name = alias.removesuffix(".latched") + ".cg"
                    assert f"- {name} sky130_fd_sc_hd__dlclkp_1 " in src
                else:
                    name = row["routed cell"].split("\\",1)[1].split(".$",1)[0]
                assert name in self.cells, name
                self.groups["work" if alias == "a" and name=="bit_store[0].ff" else alias].append(name)
        expected = dict(meta=30,sync=30,prev=30,acc1=21,acc2=21,add1=21,add2=21,
                        pp=11,pn=11,work=21,delay1=21,delay2=21,sdo=1,cs_n=1,sclk=1)
        assert all(len(self.groups[g])==n for g,n in expected.items())

    def check_analog(self):
        def boxes(name):
            return [s.bbox() for s in self.analog.shapes(self.layer(name)).each()]
        def region(name):
            return k.Region(self.analog.shapes(self.layer(name)))
        gates = region("POLY") & region("ACT")
        def gates_in(box):
            roi = k.Box(*(round(v*1000) for v in box))
            return [p.bbox() for p in (gates & k.Region(roi)).each()]
        wells = [b for b in boxes("NW") if 88000 < b.center().x < 111000 and b.top<34000]
        assert len(wells)==4 and all((b.width(),b.height())==(10100,6950) for b in wells)
        assert all(len(gates_in(coords(b)))==2 for b in wells)
        tail = [[1.1,11.25,39.50,34.75],[40.95,11.25,79.35,34.75]]
        assert all(len(gates_in(b))==40 for b in tail)
        beta = gates_in([4,36,106,48])
        assert any((b.width(),b.height())==(12000,420) for b in beta)
        plates = boxes("CAPM")
        assert Counter((b.width(),b.height()) for b in plates)=={(4500,4500):64,(21800,21800):2}
        resistors = sorted(boxes("R-ID"),key=lambda b:b.bottom)
        assert [(b.width(),b.height()) for b in resistors]==[(80000,690)]*2+[(97100,690)]*2
        wall = max(boxes("TAP"),key=lambda b:b.height())
        assert coords(wall)==[78.75,54.3,81.75,120.4]
        assert sum(1 for b in boxes("CONT") if wall.contains(b.center()))==246
        for layer in (69,70,71):
            for shape in self.analog.shapes(self.layout.layer(layer,5)).each():
                if shape.is_text():
                    t = shape.text
                    self.probes[f"{t.string}:M{layer-67}"]=[t.x/1000,t.y/1000]
        for i in range(15):
            for prefix,dx in (("p",0),("n",82.05)):
                assert abs(self.probes[f"{prefix}{i}:M3"][0]-(4.57+dx+4.925*i))<1e-6
        pex=(ROOT/"layout/integration/final_analog_c.spice").read_text()
        assert re.search(r"^C\d+ (?:rp rn|rn rp) 4\.1989f$",pex,re.M)
        self.geometry=dict(input_wells=[coords(b) for b in wells], tail_wells=tail,
                           reference_gates=[coords(b) for b in beta if b.width()>=2000],
                           resistor_id=[coords(b) for b in resistors],rail_mim=[coords(b) for b in plates if b.width()>4500],
                           small_mim_count=64,tap_wall=coords(wall),wall_contacts=246,
                           stripes=[coords(s.bbox()) for s in self.top.shapes(self.layer("M4")).each() if s.bbox().height()>200000])

    def mask(self,ax,title,roi,layers,top=False):
        self.views[title]=dict(box_um=roi,layers=layers,source=TOP+" (direct)" if top else self.analog.name)
        x,y,u,v=roi
        scale=min(1750/(u-x),950/(v-y))
        w,h=round((u-x)*scale)+1,round((v-y)*scale)+1
        canvas=Image.new("RGB",(w,h),"#f8fafb")
        draw=ImageDraw.Draw(canvas)
        def pixel(point):
            return (round((point.x/1000-x)*scale),round((v-point.y/1000)*scale))
        box=k.Box(*(round(i*1000) for i in roi))
        source=self.top if top else self.analog
        for name in layers:
            color=PALETTE[name][2]
            for shape in source.shapes(self.layer(name)).each_overlapping(box):
                if shape.is_text(): continue
                if shape.is_box():
                    b=shape.box
                    draw.rectangle([pixel(k.Point(b.left,b.top)),pixel(k.Point(b.right,b.bottom))],fill=color)
                else:
                    poly=shape.polygon.to_simple_polygon()
                    draw.polygon([pixel(p) for p in poly.each_point()],fill=color)
        ax.imshow(np.asarray(canvas),extent=roi_to_extent(roi),origin="upper",interpolation="nearest")
        axes(ax,title,roi)

    def digital_map(self,ax,title,group_sets):
        def patches(names):
            for name in names:
                x,y,u,v=self.cells[name]
                yield Rectangle((x,y),u-x,v-y)
        ax.add_collection(PatchCollection(list(patches(self.cells)),facecolor="#e4e9ec",edgecolor="white",linewidth=.22))
        handles=[]
        for i,(title_key,groups) in enumerate(group_sets):
            names=[n for g in groups for n in self.groups[g]]
            ax.add_collection(PatchCollection(list(patches(names)),facecolor=COLORS[i],edgecolor="white",linewidth=.34))
            handles.append(Patch(color=COLORS[i],label=title_key))
        axes(ax,title,[4.25,125.76,154.25,225.76])
        ax.legend(handles=handles,loc="upper center",bbox_to_anchor=(.5,-.16),ncol=2,fontsize=10,frameon=False)
        self.views[title]=dict(box_um=[4.25,125.76,154.25,225.76],groups=group_sets)

def write_markers(atlas):
    """Create switchable KLayout marker categories in the same coordinate system as the PDF."""
    db = ReportDatabase("CCRO circuit blocks")
    db.description = f"Report pp. 37–45. Coordinates in µm from the lower left. Final GDS SHA-256 {EXPECTED}"
    cell = db.create_cell(TOP)
    categories = {}
    count = 0
    def add(category, name, bounds):
        nonlocal count
        if category not in categories:
            categories[category] = db.create_category(category)
        item = db.create_item(cell.rdb_id(), categories[category].rdb_id())
        item.add_value(k.DBox(*bounds))
        item.add_value(name)
        count += 1
    for title, panel in atlas.views.items():
        add("Figure windows", title, panel["box_um"])
    geom = atlas.geometry
    for group,key in (("Bias gates","reference_gates"),("Tail banks","tail_wells"),
                      ("Input wells","input_wells"),("Resistors","resistor_id"),
                      ("Rail capacitors","rail_mim"),("Power stripes","stripes")):
        for box in geom[key]:
            add(group, f"{key} {box}",box)
    add("Substrate", "Three-column grounded substrate contact wall", geom["tap_wall"])
    for net,xy in atlas.probes.items():
        x,y = xy
        loc = "Receiver terminals" if re.match(r"^[pn][ab]?[0-9]+:",net) else "Analog route labels"
        add(loc,net,(x-.20,y-.20,x+.20,y+.20))
    for pos in range(16):
        for bank,origin in (("P",.15),("N",82.20)):
            x,y = origin+(pos//2)*9.85,56.40+21*(pos%2)
            add("Ring sites",f"{bank} / "+("dummy" if pos==15 else f"stage {pos}"),(x,y,x+9.2,y+19.9))
    for group,names in sorted(atlas.groups.items()):
        for name in names:
            add("Digital - "+group,name,atlas.cells[name])
    output = OUT/"atlas_blocks.lyrdb"
    db.save(str(output))
    check = ReportDatabase("readback")
    check.load(str(output))
    assert check.num_items() == count
    return count

def roi_to_extent(roi):
    x,y,u,v=roi
    return x,u,y,v

def axes(ax,title,roi):
    x,y,u,v=roi
    ax.set(xlim=(x,u),ylim=(y,v),aspect="equal",title=title,xlabel="X  (µm)",ylabel="Y  (µm)")
    ax.tick_params(labelsize=10,length=3,pad=2)
    ax.locator_params(axis="both",nbins=5)

def pair():
    fig,axs=plt.subplots(1,2,figsize=(11.8,4.9))
    fig.subplots_adjust(left=.064,right=.984,bottom=.24,top=.89,wspace=.24)
    return fig,axs

def save(fig,name,layers=()):
    if layers:
        handles=[Patch(color=PALETTE[l][2],label=l) for l in layers]
        fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.5,.035),ncol=len(handles),
                   frameon=False,handlelength=1.1,columnspacing=1.25,fontsize=11)
    fig.savefig(OUT/("atlas_"+name+".png"),dpi=180,facecolor="white",bbox_inches="tight",pad_inches=.08)
    plt.close(fig)

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    a=Atlas()
    fig,(left,right)=pair()
    a.mask(left,"Analog macro",(0,0,161,121),("NW","POLY","TAP","CAPM"))
    for box,t in [((1,11,79,35),"I"),((88,12,110.4,28.3),"II"),((4,36,158,52),"III"),
                  ((.15,54,78.3,98),"P"),((82.2,54,160.35,98),"N"),((.15,100.85,74,120.75),"RX")]:
        rect(left,box,t)
    a.digital_map(right,"Readout above the analog macro",[("sampler",("meta","sync","prev")),("integrators",("acc1","acc2"))])
    save(fig,"floorplan")
    fig,(l,r)=pair()
    a.mask(l,"PMOS mirror and startup device",(4.5,36,32.5,48.5),FE)
    label(l,8.6,45,"P0");label(l,13.48,45,"P1");label(l,23.36,45,"weak")
    a.mask(r,"NMOS reference and startup detector",(90.5,36,108,48.5),FE)
    label(r,93.71,46.1,"N0");label(r,98.59,46.1,"N1");label(r,104.1,38.1,"sense")
    save(fig,"bias",FE)
    fig,(l,r)=pair()
    a.mask(l,"P-tail unit array",(1,11,40,35),FE)
    a.mask(r,"Rotated input quad",(87,11,112,29.5),FE)
    for x,y,t in [(105.3,15.83,"P"),(93.3,15.83,"N"),(105.3,24.83,"N"),(93.3,24.83,"P")]:
        label(r,x,y,t)
    save(fig,"input",FE)
    fig,(l,r)=pair()
    l.remove()
    grid=fig.add_gridspec(2,2,left=.065,right=.984,bottom=.26,top=.89,wspace=.24,hspace=1.02)
    l=fig.add_subplot(grid[0,0])
    a.mask(l,"Four resistor bodies",(6,0,120,10.85),("POLY","TAP","R-ID"))
    l.set_yticks([0,10])
    l.set_xlabel("")
    inset=fig.add_subplot(grid[1,0])
    a.mask(inset,"Staggered left terminals",(7,0,29.8,10.85),("POLY","TAP","R-ID","CONT"))
    inset.set_yticks([0,5,10])
    a.mask(r,"Ring-rail capacitors",(109,9,161,36),("M3","M4","CAPM"))
    label(r,123.5,22.7,"rp");label(r,148.7,22.7,"rn")
    save(fig,"passives",("TAP","POLY","R-ID","CONT","M3","M4","CAPM"))
    fig,(l,r)=pair()
    a.mask(l,"P-ring phase order",(0,53.9,78.7,97.8),("M2","CAPM"))
    for i in range(8):
        label(l,4.85+i*9.85,65.5,str(2*i))
        label(l,4.85+i*9.85,86.5,str(2*i+1) if i<7 else "D")
    a.mask(r,"Stage 0 transistor gates",(.15,56.4,9.45,76.3),FE)
    save(fig,"ring",(*FE,"M2","CAPM"))
    fig,(l,r)=pair()
    a.mask(l,"Receiver 0 and adjacent pitch",(0,98.5,10.2,121.0),FE)
    a.mask(r,"Receiver 0 metal access",(0,98.5,10.2,121.0),("M1","M2","M3"))
    for net in ("pa0:M2","pb0:M2","p0:M3"):
        x,y=a.probes[net]
        r.plot(x,y,marker="o",ms=6,color="#99361c",mec="white",mew=.6)
        r.annotate(net.split(":")[0],(x,y),xytext=((-12,-1) if net=="pa0:M2" else (8,1)),textcoords="offset points",
                   ha="right" if net=="pa0:M2" else "left",fontsize=11,fontweight="bold",color="#7b351e",
                   bbox=dict(facecolor="white",edgecolor="none",pad=.6,alpha=.90))
    save(fig,"receiver",(*FE,"M1","M2","M3"))
    for name,titles,parts in [
        ("sampler",("Sampled phase history","Event counts and integrators"),
         [[("meta",("meta",)),("sync",("sync",)),("prev",("prev",))],
          [("pop15 P/N",("pp","pn")),("add1/2",("add1","add2")),("acc1/2",("acc1","acc2"))]]),
        ("output",("Serial comb and its clock gates","Frame timing and serial drivers"),
         [[("work",("work",)),("delay1",("delay1",)),("delay2",("delay2",)),
           ("clock gates",("g_work.latched","g_delay.latched"))],
          [("phase[7:0]",("phase",)),("SDO",("sdo",)),("CS_N",("cs_n",)),("SCLK",("sclk",))]])]:
        fig,axs=pair()
        for ax,title,groups in zip(axs,titles,parts): a.digital_map(ax,title,groups)
        save(fig,name)
    fig,(l,r)=pair()
    a.mask(l,"Substrate contacts between rings",(77.7,79,82.8,86),("TAP","CONT","M2"))
    a.mask(r,"Top-level distribution",(0,0,161,225.76),("M3","M4"),top=True)
    for x,y,t in [(18,76,"VDPWR"),(110,90,"VGND")]:
        r.annotate(t,(.6 if t=="VDPWR" else 92.8,y),(x,y+12),fontsize=9,fontweight="bold",
                   arrowprops=dict(arrowstyle="->",lw=.9),bbox=dict(fc="white",ec="none",alpha=.88))
    save(fig,"isolation",("TAP","CONT","M2","M3","M4"))
    marker_count=write_markers(a)
    data=dict(klayout_marker_count=marker_count,gds_sha256=EXPECTED,def_sha256=digest(DEF),formal_mapping_sha256=digest(MAPPING),
              coordinate_system="Top-cell micrometres; boxes are [xmin,ymin,xmax,ymax].",
              checked_def_instances=len(a.cells),geometry=a.geometry,analog_labels=a.probes,panels=a.views,
              digital_groups={g:{n:a.cells[n] for n in sorted(names)} for g,names in sorted(a.groups.items())})
    (OUT/"atlas_index.json").write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print(f"Verified {len(a.cells)} DEF placements, {len(a.views)} views and {len(a.probes)} analog labels.")

if __name__=="__main__":
    build()
