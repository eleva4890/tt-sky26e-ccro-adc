"""Prove an event-by-event identity relation over every flop/latch and every output.

Take Yosys' elaborated cell graphs, expose paired pre-event state as inputs,
and compare all effective update data, clock edges, latch enables, resets
and output pins as functions of arbitrary common inputs and current state.
"""
from collections import Counter
from copy import deepcopy
from state_map import directory,mods,g,h,ga,ha,pairs
import json,re
assert len(g)==len(h)==len(pairs)==len(set(pairs.values()))
ordered=sorted(pairs,key=lambda a:sorted(ga[a]))
template=None
mapping=["bit\tRTL alias\tRTL cell\trouted cell\tstate semantics"]
stepmods={}
for side,src,cells in [("gold",mods["gold"],g),("gate",mods["gate"],h)]:
    m=deepcopy(src)
    boundary=m["ports"]
    nets = m["netnames"]
    next_bit=max((bit for w in nets.values() for bit in w["bits"] if isinstance(bit,int)),default=0)+1
    def port(name,direction,field):
        boundary[name]={"direction":direction,"bits":[field]}
    types=[]
    for i,a in enumerate(ordered):
        b=a if side=="gold" else pairs[a]
        name,cell=cells[b]
        c=cell["connections"]
        del m["cells"][name]
        t=cell["type"]
        port(f"prior_{i}","input",b)
        if "LATCH" in t:
            assert t=="$_DLATCH_N_"
            port(f"low_latch_gate_{i}","output",c["E"][0])
            types.append("low-transparent latch")
        else:
            defn=re.fullmatch(r"\$_DFF(E?)_([PN])(?:([PN])([01]))?([PN])?_",t)
            assert defn,t
            enable,cpol,rpol,rval,epol=defn.groups()
            port(f"clock_{i}","output",c["C"][0])
            if rpol:
                port(f"reset_{i}","output",c["R"][0])
            types.append(f"clock={cpol}, async reset={rpol}/{rval}")
        d=c["D"][0]
        if "DFFE" in t:
            assert epol in ("P","N")
            v0,v1=(b,d) if epol=="P" else (d,b)
            m["cells"][f"$step_mux_{i}"]={"hide_name":1,"type":"$_MUX_","parameters":{},"attributes":{},
                "port_directions":{"A":"input","B":"input","S":"input","Y":"output"},
                "connections":{"A":[v0],"B":[v1],"S":c["E"],"Y":[next_bit]}}
            d=next_bit
            next_bit+=1
        port(f"update_{i}","output",d)
        if side=="gold":
            alias=min(ga[a],key=lambda v:(len(v[0]),v))
            mapping.append(f"{i}\t{alias[0]}[{alias[1]}]\t{name}\t{h[pairs[a]][0]}\t{types[-1]}")
    assert all(cell["type"].startswith("$_") and "DFF" not in cell["type"] and "LATCH" not in cell["type"] for cell in m["cells"].values())
    if template is None: template=types
    assert template==types,"edge, reset value, reset polarity or latch polarity differs"
    # Only boundary ports are named, preventing any assumed internal combinational match.
    m["netnames"]={k:dict(hide_name=0,bits=v["bits"],attributes={}) for k,v in boundary.items()}
    stepmods[side]=m
(directory/"state_mapping.tsv").write_text("\n".join(mapping)+"\n")
(directory/"step.json").write_text(json.dumps(dict(modules=stepmods)))
print("Paired state bits",len(pairs),"including",template.count("low-transparent latch"),"latches")
print("All non-state standard-cell logic retained; all state update events and observable bits are proof outputs.")

