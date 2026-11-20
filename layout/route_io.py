"""Route top-level ports between the two checked macros and the fixed TT pads.

Run from the design root using KLayout in batch mode. The maze search uses the
actual streamed conductors as obstacles. Failed nets are recorded explicitly.
"""
from collections import defaultdict
from heapq import heappop,heappush
from pathlib import Path
import math,os,re,pya
import random

layout=pya.Layout()
layout.read("layout/integration/power_assembly.gds")
top=layout.cell("eleva_ccro_power_assembly")
layout.rename_cell(top.cell_index(),"tt_um_eleva_ccro_adc")
root=Path("layout/integration")
floor=(root/"top_floorplan.def").read_text()
lef=Path("layout/readout/adc_readout.lef").read_text()
step=int(os.environ.get("ADC_IO_GRID_NM","250"))
nx,ny=161000//step+1,225760//step+1
plane=nx*ny
def grid(v):return round(v/step)*step
def address(m,x,y):return (m-68)*plane+(y//step)*nx+x//step
def decode(n):
    m,offset=divmod(n,plane)
    y,x=divmod(offset,nx)
    return m+68,x*step,y*step

def box(m,x,y,u,v,dt=20):
    top.shapes(layout.layer(m,dt)).insert(pya.Box(x,y,u,v))
def wire(m,x,y,u,v,w):
    assert x==u or y==v
    box(m,min(x,u)-w//2,min(y,v)-w//2,max(x,u)+w//2,max(y,v)+w//2)
def cut(m,x,y):
    width,pad={67:(170,340),68:(150,360),69:(200,640),70:(200,680)}[m]
    for layer in (m,m+1):wire(layer,x,y,x,y,pad)
    box(m,x-width//2,y-width//2,x+width//2,y+width//2,44)
def pin_text(m,x,y,name):
    top.shapes(layout.layer(m,5)).insert(pya.Text(name,pya.Trans(x,y)))

ports={}
for name,lx,ly,ux,uy,x,y in re.findall(r"(?m)^    - (\S+) \+ NET \S+ \+ DIRECTION \S+ \+ USE SIGNAL\s+\+ PORT\s+\+ LAYER met4 \( (-?\d+) (-?\d+) \) \( (-?\d+) (-?\d+) \)\s+\+ PLACED \( (\d+) (\d+) \) N ;",floor):
    lx,ly,ux,uy,x,y=map(int,(lx,ly,ux,uy,x,y))
    for dt in (20,16):box(71,x+lx,y+ly,x+ux,y+uy,dt)
    pin_text(71,x,y,name)
    ports[name]=(71,x,y)
assert len(ports)==51
for x in [600,92800]:box(71,x-600,2000,x+600,217000,16)
box(235,0,0,161000,225760,4)
digital={}
for b in lef.split("\n  PIN ")[1:]:
    match=re.search(r"LAYER met2 ;\s+RECT ([.\d]+) 96.000 ([.\d]+) 100.000",b)
    if match:digital[b.split()[0]]=(69,4250+round(500*sum(map(float,match.groups()))),224500)
inner={"ua[0]":(71,85300,46440),"ua[1]":(71,84100,47430),
       "ui_in[3]":(71,32315,48420),"ui_in[4]":(71,35345,49410)}
digital_map={"clk":"clk","rst_n":"rst_n","ui_in[0]":"osr_sel","ui_in[1]":"dbg_mode[0]",
             "ui_in[2]":"dbg_mode[1]","ui_in[5]":"err_clr","uio_out[0]":"sdo",
             "uio_out[1]":"cs_n","uio_out[2]":"sclk","uio_out[3]":"wrap_err",
             **{f"uo_out[{i}]":f"debug[{i}]" for i in range(8)}}
inner.update({net:digital[pin] for net,pin in digital_map.items()})
for i in range(8):
    col,row=i%2,i//2
    x=156400+col*1380
    y=184960+row*2720
    low=f"uio_out[{i+4}]" if i<4 else f"uio_oe[{i}]"
    for net,dx,dy in [(low,1055,1530)]+([(f"uio_oe[{i}]",420,1210)] if i<4 else []):
        ax,ay=x+dx,y+(2720-dy if row%2 else dy)
        cut(67,ax,ay)
        cut(68,ax,ay)
        gx=(157000,160000)[col] if dx==1055 else (156000,158500)[col]
        escape_y=(900 if dx==420 else 1820)
        escape_y=y+(2720-escape_y if row%2 else escape_y)
        wire(69,ax,ay,ax,escape_y,320)
        wire(69,ax,escape_y,gx,escape_y,320)
        inner[net]=(69,gx,escape_y)
# Run the eight debug outputs across the empty upper band. The readout presents
# these pins in increasing X while the shuttle has the reverse order.
manual=set()
readout_x=[p[1] for p in digital.values()]
for i in range(8):
    name=f"uo_out[{i}]"
    m,src,_=inner[name]
    _,pad,_=ports[name]
    dst=next(pad+d for d in (0,950,-950,1100,-1100) if all(abs(pad+d-x)>840 for x in readout_x))
    layer=68 if i<6 else 70
    level=222850+i*480 if i<6 else 222850+(i-6)*1000
    for x in (src,dst):
        cut(68 if layer==68 else 69,x,level)
    wire(layer,src,level,dst,level,220 if layer==68 else 400)
    wire(69,dst,level,dst,224900,300)
    cut(69,dst,224900)
    cut(70,dst,224900)
    wire(71,dst,224900,pad,224900,320)
    manual.add(name)
# ERR_CLR is a slow level sampled by a synchronizer. A dedicated local-
# interconnect segment in the empty upper rim avoids all eight debug trunks.
name="ui_in[5]"
_,src,_=inner[name]
_,pad,_=ports[name]
dst=pad+950
for x in (src,dst):
    cut(67,x,223350)
    cut(68,x,223350)
wire(67,src,223350,dst,223350,340)
wire(69,dst,223350,dst,224900,320)
cut(69,dst,224900)
cut(70,dst,224900)
wire(71,dst,224900,pad,224900,320)
manual.add(name)
name="uio_out[4]"
sx,sy=157455,186490
edge=160500
_,pad,py=ports[name]
cut(69,sx,sy)
cut(70,sx,sy)
wire(71,sx,sy,edge,sy,400)
wire(71,edge,sy,edge,224180,400)
for x in (edge,pad):
    for layer in range(67,71):cut(layer,x,224180)
wire(67,edge,224180,pad,224180,340)
wire(71,pad,224180,pad,py,340)
manual.add(name)
nets=[n for n in inner if n not in manual]
ids={n:i+1 for i,n in enumerate(nets)}
locations=defaultdict(list)
ends={}
access=defaultdict(set)
for net in nets:
    ends[net]=[]
    for index,(m,x,y) in enumerate((inner[net],ports[net])):
        gx,gy=grid(x),grid(y)
        if y==225260:gy=225000
        if net=="ui_in[4]" and m==71 and y<100000:
            gx,gy=35250,49250
        w=300 if m<70 else 320
        wire(m,x,y,gx,y,w)
        wire(m,gx,y,gx,gy,w)
        ends[net].append(address(m,gx,gy))
        locations[m].append((pya.Point(x,y),ids[net],index))
# Pixelate conservative clearance around fixed GDS and reserve distinct pin nets.
# At a junction the only fixed conductors that can be reused carry the same ID.
mask=bytearray(4*plane)
def paint(m,b,tag,padding=0):
    x0=max(0,math.ceil((b.left-padding)/step))
    x1=min(nx-1,(b.right+padding)//step)
    y0=max(0,math.ceil((b.bottom-padding)/step))
    y1=min(ny-1,(b.top+padding)//step)
    width=x1-x0+1
    if width<=0:return
    val=bytes([tag])*width
    for y in range(y0,y1+1):
        a=(m-68)*plane+y*nx+x0
        if tag==255:
            mask[a:a+width]=val
        else:
            current=mask[a:a+width]
            mask[a:a+width]=bytes(tag if old in (0,tag) else 255 for old in current)
for m in range(68,72):
    reg=pya.Region(top.begin_shapes_rec(layout.layer(m,20))).merged()
    identified=defaultdict(pya.Region)
    for point,idnum,index in locations[m]:
        touch=reg.interacting(pya.Region(pya.Box(point.x-1,point.y-1,point.x+1,point.y+1)))
        if touch.is_empty():raise ValueError((point,idnum))
        identified[idnum]+=touch
        for polygon in touch.decompose_trapezoids_to_region().each():
            b=polygon.bbox()
            for iy in range(max(1,math.ceil((b.bottom+20)/step)),min(ny,(b.top-20)//step+1)):
                for ix in range(max(1,math.ceil((b.left+20)/step)),min(nx,(b.right-20)//step+1)):
                    access[idnum,index].add(address(m,ix*step,iy*step))
    other=reg.dup()
    for r in identified.values():other-=r
    radius=420 if m<70 else 615
    for group,tag in [(other,255)]+[(r,t) for t,r in identified.items()]:
        for poly in group.decompose_trapezoids_to_region().each():
            paint(m,poly.bbox(),tag,radius)
for m in range(68,72):
    for edge in (pya.Box(-20,-20,161020,300),pya.Box(-20,-20,300,225780),
                 pya.Box(160650,-20,161020,225780),pya.Box(-20,225400,161020,225780)):
        paint(m,edge,255)
for plate in pya.Region(top.begin_shapes_rec(layout.layer(89,44))).each():
    paint(70,plate.bbox(),255,1740)
for net,(a,b) in ends.items():
    if mask[a]!=ids[net] or mask[b]!=ids[net]:
        print("ACCESS",net,decode(a),mask[a],decode(b),mask[b],flush=True)
if os.environ.get("ADC_IO_ACCESS_ONLY"):raise SystemExit(0)
def route(start,end,tag):
    sources={a for a in access[tag,0]|{start} if mask[a]==tag}
    goals={a for a in access[tag,1]|{end} if mask[a]==tag}
    if not sources or not goals:return []
    em,ex,ey=decode(end)
    def h(k):
        m,x,y=decode(k)
        return (abs(x-ex)+abs(y-ey))//step+4*abs(m-em)
    queue=[]
    for a in sources:heappush(queue,(h(a),0,a))
    prev=dict.fromkeys(sources,-1)
    costs=dict.fromkeys(sources,0)
    while queue:
        _,cost,node=heappop(queue)
        if cost!=costs[node]:continue
        if node in goals:
            path=[]
            while node!=-1:
                path.append(node)
                node=prev[node]
            return path[::-1]
        layer=node//plane
        for delta,weight in ((-1,1),(1,1),(-nx,1),(nx,1),(-plane,7),(plane,7)):
            n=node+delta
            if n<0 or n>=len(mask) or mask[n] not in (0,tag):continue
            c=cost+weight
            if c>=costs.get(n,10**9):continue
            costs[n]=c
            prev[n]=node
            heappush(queue,(c+h(n),c,n))
    return []
def trim(path):
    if len(path)<3:return path
    return [path[0]]+[b for a,b,c in zip(path,path[1:],path[2:]) if b-a!=c-b or abs(b-a)==plane]+[path[-1]]
failed=[]
order=sorted(nets,key=lambda n:(0 if n.startswith("ua") or n in ("ui_in[3]","ui_in[4]") else 1,
                                -abs(ends[n][1]%nx-ends[n][0]%nx)))
if os.environ.get("ADC_IO_SEED"):
    random.Random(int(os.environ["ADC_IO_SEED"])).shuffle(order)
priority=os.environ.get("ADC_IO_FIRST","").split(",")
order=[n for n in priority if n in nets]+[n for n in order if n not in priority]
for net in order:
    tag=ids[net]
    start,end=ends[net]
    path=route(start,end,tag)
    if not path:
        failed.append(net)
        print("OPEN",net,"pin masks",mask[start],mask[end],"id",tag,flush=True)
        continue
    path=trim(path)
    for a,b in zip(path,path[1:]):
        m,x,y=decode(a)
        z,u,v=decode(b)
        if z==m:
            width=320 if m<70 else 400
            wire(m,x,y,u,v,width)
            paint(m,pya.Box(min(x,u),min(y,v),max(x,u),max(y,v)),tag,740 if m>=70 else 600)
        else:
            cut(min(m,z),x,y)
            for j in (m,z):paint(j,pya.Box(x,y,x,y),tag,810)
    print("ROUTED",net,len(path),"vertices",flush=True)
print("external signal nets",len(inner)-len(failed),"/",len(inner),"open",failed,flush=True)
opts=pya.SaveLayoutOptions()
opts.gds2_write_timestamps=False
target=Path(os.environ.get("ADC_IO_DEST",root/("io_work.gds" if failed else "tt_um_eleva_ccro_adc.gds")))
layout.write(str(target),opts)
if failed:raise ValueError("External routes incomplete")
