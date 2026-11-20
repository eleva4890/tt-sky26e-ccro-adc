"""Generate explicit, editable device schematics from the archived design-side topology."""
from pathlib import Path
import math
import os
import re

review = Path(__file__).resolve().parent
dest = review / "xschem"
pdk = Path(os.environ["PDK_ROOT"]) / "sky130A/libs.tech/xschem/sky130_fd_pr"
blocks = {}
for line in (review.parent / "analog/adc_analog_physical_lvs.spice").read_text().splitlines():
    words = line.split()
    if not words:
        continue
    if words[0].lower() == ".subckt":
        ports, devices = words[2:], []
        blocks[words[1]] = (ports, devices)
    elif words[0].startswith("X"):
        fields = [w for w in words[1:] if "=" not in w]
        props = dict(w.split("=") for w in words[1:] if "=" in w)
        devices.append((words[0], fields[:-1], fields[-1], props))

ports, devices = blocks["bias"]
blocks["beta_ref"] = (["vb","v","g"], devices[:9])
blocks["bias"] = (ports, [("Xreference", ["vb","v","g"], "beta_ref", {})] + devices[9:])
ports,devices = blocks["tail"]
units = [devices[0]]
for size, start in [(4,1),(15,5),(20,20)]:
    kind = f"units{size}"
    blocks[kind] = (["s","control","v"], [(name,["s","control","v","v"],model,props) for name,pins,model,props in devices[start:start+size]])
    units.append(("X"+kind,["s",f"g{size}","v"],kind,{}))
blocks["tail"] = (ports,units)
ports = blocks["adc_analog"][0]
blocks["analog_review"] = (ports,[("Xadc",ports,"adc_analog",{})])
tile_name="tt_um_eleva_ccro_adc"
tile_devices=[]
wrapper=(review.parent / "analog/top.spice").read_text().replace("\n+"," ")
for line in wrapper.splitlines():
    fields=line.split()
    if line.startswith(".subckt"):
        tile_ports=fields[2:]
    if not line.startswith("X"):
        continue
    words=[w for w in fields if "=" not in w]
    model=words[-1]
    nets=words[1:-1]
    attrs=dict(w.split("=") for w in fields if "=" in w)
    if model=="sky130_fd_sc_hd__conb_1":
        lo,hi,vpb,vnb,vgnd,vpwr=nets
        nets=[hi,lo]
        attrs=dict(VGND=vgnd,VNB=vnb,VPB=vpb,VPWR=vpwr)
    tile_devices.append((words[0],nets,model,attrs))
digital_ports=(["VGND","VPWR","clk","cs_n","dbg_mode[0]","dbg_mode[1]"]+
    [f"debug[{i}]" for i in range(8)]+["err_clr","osr_sel","rst_n","sclk","sdo"]+
    [f"tap_{s}[{i}]" for s in "np" for i in [0,10,11,12,13,14,1,2,3,4,5,6,7,8,9]]+["wrap_err"])
blocks["adc_readout"]=(digital_ports,[])
blocks[tile_name]=(tile_ports,tile_devices)
descriptions = dict(analog_review="Analog macro interface",adc_analog="Differential VCO ADC",front="Split-tail input and ring reservoirs",
    bias="Bias reference and static enable decoder",beta_ref="Beta multiplier and start-up branch",tail="Selectable current-source banks",
    nor2="Static CMOS NOR",tailgate="Transmission gate and off clamp",stage="Main inverters, cross-couplers and MIM loads",
    bank="15 active stages and one layout dummy",ring="Oscillator bank and 15 level shifters",dual="Positive and negative channels",
    cvsl="Cross-coupled level shifter and tap buffers")
header="v {xschem version=3.4.4 file_version=1.2}\nG {}\n"
pins={}
for typ,(ports,devices) in blocks.items():
    # Pin records follow design order, independently of their graphical side.
    split=(len(ports)+1)//2
    pts=[]
    for i,port in enumerate(ports):
        x,y=(-120 if i<split else 120), (i if i<split else i-split)*30
        pts.append((x,y,port))
    pins[typ]=pts
    bottom=(split-1)*30+20
    symbol_type="primitive" if typ=="adc_readout" else "subcircuit"
    sym=[header+f'K {{type={symbol_type} format="@name @pinlist @symname" template="name=X1"}}\nV {{}}\nS {{}}\nE {{}}']
    for x,y,u,v in [(-100,-25,100,-25),(-100,bottom,100,bottom),(-100,-25,-100,bottom),(100,-25,100,bottom)]:
        sym.append(f"L 4 {x} {y} {u} {v} {{}}")
    sym += [f"T {{{typ}}} -98 -64 0 0 0.38 0.38 {{}}","T {@name} -98 -42 0 0 0.23 0.23 {layer=13}"]
    for x,y,port in pts:
        sym += [f"L 4 {min(x,int(x*5/6))} {y} {max(x,int(x*5/6))} {y} {{}}",
                f"B 5 {x-2} {y-2} {x+2} {y+2} {{name={port} dir=inout}}",
                f"T {{{port}}} {-90 if x<0 else 90} {y-8} 0 {0 if x<0 else 1} 0.25 0.25 {{}}"]
    (dest/(typ+".sym")).write_text("\n".join(sym)+"\n")
for typ,(ports,devices) in blocks.items():
    if typ=="adc_readout":
        continue
    title=descriptions.get(typ,typ+" parallel unit PMOS")
    if typ==tile_name:
        title="Tile / analog pins, digital readout, tie cells and input protection"
    sch=[header+"K {}\nV {}\nS {}\nE {}",f"T {{{title}}} 0 0 0 0 0.62 0.62 {{}}",
         "T {Sheet terminals} 0 60 0 0 0.32 0.32 {layer=13}"]
    for i,port in enumerate(ports):
        sch.append(f"C {{devices/iopin.sym}} {i%8*150} {110+i//8*35} 0 0 {{name=io{i} lab={port} sim_pinnumber={i+1}}}")
    top=240+math.ceil(len(ports)/8)*35
    next_y=top
    count=0
    # Stack complementary pairs on selected functional sheets. Wire common
    # drains and common gates locally; the remaining labeled nets join by name.
    pair_plan={
        "stage":[("XmainA_Xp","XmainA_Xn"),("XmainB_Xp","XmainB_Xn"),("XcrossA_Xp","XcrossA_Xn"),("XcrossB_Xp","XcrossB_Xn")],
        "cvsl":[("Xp0","Xn0"),("Xp1","Xn1"),("Xbuf_p","Xbuf_n"),("Xdummy_p","Xdummy_n")],
        "beta_ref":[("Xp0","Xn1"),("Xp1","Xn0"),("Xweak","Xsense")],
        "bias":[("Xi0p","Xi0n"),("Xi1p","Xi1n"),("Xi4p","Xi4n"),("Xi15p","Xi15n"),("Xi20p","Xi20n")]}
    positions={}
    skip=set()
    if typ in pair_plan:
        by_name={d[0]:d for d in devices}
        for j,(upper,lower) in enumerate(pair_plan[typ]):
            x=180+(j%4)*420
            y=top+(j//4)*480
            positions[upper]=(x,y)
            positions[lower]=(x,y+190)
            p,n=by_name[upper][1],by_name[lower][1]
            assert p[0]==n[0]
            sch.extend([f"N {x+20} {y+30} {x+20} {y+95} {{lab={p[0]}}}",
                        f"N {x+20} {y+95} {x+20} {y+160} {{lab={p[0]}}}",
                        f"N {x+20} {y+95} {x+80} {y+95} {{lab={p[0]}}}",
                        f"C {{devices/lab_pin.sym}} {x+80} {y+95} 0 1 {{name=drain{j} lab={p[0]}}}"])
            skip.update([(upper,"D"),(lower,"D")])
            if p[1]==n[1]:
                for yy in (y,y+190):
                    sch.append(f"N {x-75} {yy} {x-20} {yy} {{lab={p[1]}}}")
                sch.extend([f"N {x-75} {y} {x-75} {y+95} {{lab={p[1]}}}",
                            f"N {x-75} {y+95} {x-75} {y+190} {{lab={p[1]}}}",
                            f"C {{devices/lab_pin.sym}} {x-75} {y+95} 0 0 {{name=gate{j} lab={p[1]}}}"])
                skip.update([(upper,"G"),(lower,"G")])
        rest_y=top+480*math.ceil(len(pair_plan[typ])/4)
        for i,d in enumerate(d for d in devices if d[0] not in positions):
            positions[d[0]]=(180+i%4*420,rest_y+(i//4)*280)
    columns = 3 if len(devices)>2 else 2
    for start in range(0,len(devices),columns):
        row_h=240
        for col,(name,nets,model,props) in enumerate(devices[start:start+columns]):
            primitive=model.startswith(("sky130_fd_pr__","sky130_fd_sc_hd__"))
            if primitive:
                short=model.split("__")[1]
                path="sky130_fd_pr/"+("diode" if short.startswith("diode_") else short)+".sym"
                if short=="conb_1": path="sky130_stdcells/conb_1.sym"
                body=(pdk.parent/path).read_text()
                pts=[(round((float(x)+float(u))/2),round((float(y)+float(v))/2),p)
                      for x,y,u,v,p in re.findall(r"^B 5 (\S+) (\S+) (\S+) (\S+) \{name=(\S+)",body,re.M)]
                dtype="M" if "fet_" in short else ("R" if short.startswith("res") else "C")
                attr="name="+dtype+name[1:]+" "+" ".join(f"{k.upper() if k in ('w','l') else k}={v}" for k,v in props.items())
                if short=="conb_1":
                    attr="name="+name+" "+" ".join(f"{k}={v}" for k,v in props.items())
                if short.startswith("diode_"):
                    attr="name=D"+name[1:]+" model="+short+" "+" ".join(f"{k}={v}" for k,v in props.items())
            else:
                path=model+".sym"
                pts=pins[model]
                attr="name="+name
            assert len(nets)==len(pts),(name,model)
            x,y=positions.get(name,(180+col*495,next_y))
            sch.append(f"C {{{path}}} {x} {y} 0 0 {{{attr}}}")
            for net,(dx,dy,port) in zip(nets,pts):
                if (name,port) in skip: continue
                px,py=x+dx,y+dy
                if primitive and "fet_" in short and port=="B":
                    ey=py+43
                    ex=x+90
                    sch.extend([f"N {px} {py} {x+30} {py} {{lab={net}}}",
                                f"N {x+30} {py} {x+30} {ey} {{lab={net}}}"])
                    px=x+30
                elif primitive and dy and short!="conb_1":
                    # Vertical outer terminals turn away from the symbol text.
                    ey=py+(35 if dy>0 else -35)
                    ex=px-25
                    sch.append(f"N {px} {min(py,ey)} {px} {max(py,ey)} {{lab={net}}}")
                else:
                    ey=py
                    ex=px+(125 if primitive and dx>0 else 35) if dx>0 else px-35
                flip=int(ex>px)
                sch += [f"N {min(px,ex)} {ey} {max(px,ex)} {ey} {{lab={net}}}",
                        f"C {{devices/lab_pin.sym}} {ex} {ey} 0 {flip} {{name=net{count} lab={net}}}"]
                count+=1
            row_h=max(row_h,max(p[1] for p in pts)+180)
        next_y+=row_h
    assert len(devices)<=20
    (dest/(typ+".sch")).write_text("\n".join(sch)+"\n")

