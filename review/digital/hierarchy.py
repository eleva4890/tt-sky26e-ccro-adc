"""Build a counted module-instantiation graph from Yosys' unflattened JSON."""
import json
from collections import Counter
from pathlib import Path
p=Path(__file__).resolve().parent
mods=json.loads((p/"hierarchy.json").read_text())["modules"]
def children(m):
    return Counter(c["type"] for c in mods[m]["cells"].values() if c["type"] in mods)
tree={}
edge_id=10
def visit(module,where,count,parent_edge=None):
    global edge_id
    pins={}
    roles={}
    if parent_edge is not None:
        pins["parent"]=[parent_edge]
        roles["parent"]="input"
    for sub,n in sorted(children(module).items()):
        edge_id+=1
        edge=edge_id
        # Every aggregation branch has its own wire, even when counts coincide.
        pname=f"{sub} x{n}"
        pins[pname]=[edge]
        roles[pname]="output"
        visit(sub,where+"/"+sub,count*n,edge)
    tree[where.replace("/"," / ")]=dict(type=module,connections=pins,port_directions=roles,
                         parameters={},attributes={},hide_name=0)
visit("adc_readout","adc_readout",1)
model={"modules":{"hierarchy":{"attributes":{"top":1},"ports":{},"cells":tree,"netnames":{}}}}
(p/"module_tree.json").write_text(json.dumps(model))
pop=mods["pop15"]
(p/"pop15.json").write_text(json.dumps({"modules":{"pop15":pop}}))

