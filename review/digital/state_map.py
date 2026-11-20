"""Match each state bit by stable elaborated-Q aliases. No name is used as a proof."""
from collections import Counter, defaultdict
from pathlib import Path
import json
directory=Path(__file__).resolve().parent
mods=json.loads((directory/"prepared.json").read_text())["modules"]
def inventory(mod):
    bits=defaultdict(set)
    for name,wire in mod["netnames"].items():
        if wire["hide_name"]: continue
        for i,b in enumerate(wire["bits"]):
            bits[b].add((name,i+wire.get("offset",0)))
    cells = {c["connections"]["Q"][0]:(k,c) for k,c in mod["cells"].items() if "DFF" in c["type"] or "LATCH" in c["type"]}
    return cells,bits
g,ga=inventory(mods["gold"])
h,ha=inventory(mods["gate"])
pairs={}
for a,(_,c) in g.items():
    choices=[b for b in h if ga[a] & ha[b]]
    if len(choices)==1: pairs[a]=choices[0]
    elif "LATCH" in c["type"]:
        for b,(name,_) in h.items():
            # RTL adc_gate and library dlclkp share their hierarchical instance prefix.
            inst=next(n[:-8] for n,i in ga[a] if n.endswith(".latched"))
            if (inst+".cg.m0",0) in ha[b]:
                pairs[a]=b
print("state cells",Counter(c["type"] for k,c in g.values()),Counter(c["type"] for k,c in h.values()))
print("matched", len(pairs), "of",len(g),len(h))
for label,cells,aliases,matched in [("gold",g,ga,pairs),("gate",h,ha,pairs.values())]:
    for q in sorted(set(cells)-set(matched)):
        print("unmatched",label,q,cells[q][1]["type"],sorted(aliases[q])[:8])

