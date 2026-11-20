"""Write a lumped tile I/O timing scenario from the flat Magic EXT (aF / milliohm scaling)."""
from collections import defaultdict
from pathlib import Path
import csv, shlex, sys

def write(ext, out):
    out=Path(out)
    top={"clk":"clk","rst_n":"rst_n","ui_in[0]":"osr_sel","ui_in[1]":"dbg_mode[0]",
         "ui_in[2]":"dbg_mode[1]","ui_in[5]":"err_clr",
         **{f"uo_out[{i}]":f"debug[{i}]" for i in range(8)},
         **{f"uio_out[{i}]":pin for i,pin in enumerate(["sdo","cs_n","sclk","wrap_err"])}}
    r,c0,cc={}, {}, defaultdict(float)
    for line in Path(ext).read_text().splitlines():
        if line.startswith("scale "):
            rs,cs=map(float,line.split()[1:3])
        elif line.startswith("node "):
            name=line.split('"',2)[1]
            if name in top:
                row=shlex.split(line)
                r[name]=float(row[2])*rs*.001
                c0[name]=float(row[3])*cs*.001
        elif line.startswith("cap "):
            _,a,b,v=shlex.split(line)
            for net in (a,b):
                if net in top: cc[net]+=abs(float(v))*cs*.001
    assert r.keys()==top.keys()
    tcl=[]
    with (out/"tile_loads.csv").open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow("tile_net macro_pin lumped_R_ohm ground_C_fF coupling_C_fF miller_load_fF RC_ns".split())
        for net,pin in top.items():
            cap=c0[net]+2*cc[net]
            tau=r[net]*cap*1e-6
            w.writerow([net,pin,r[net],c0[net],cc[net],cap,tau])
            if net.startswith(("uo_out","uio_out")):
                tcl.append(f"set_load {(15+cap)*.001:.7f} [get_ports {{{pin}}}]")
                tcl.append(f"set_output_delay -max -clock sample {4+tau:.7f} [get_ports {{{pin}}}]")
            else:
                tcl.append(f"set_input_transition {.3+2.2*tau:.7f} [get_ports {{{pin}}}]")
    (out/"tile_loads.tcl").write_text("\n".join(tcl)+"\n")
if __name__=="__main__":write(*sys.argv[1:])
