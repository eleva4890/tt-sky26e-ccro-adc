"""Independently compare flat Magic EXT node/coupling records with the exported capacitor matrix."""
from collections import defaultdict,Counter
import csv,re,shlex,sys
from pathlib import Path
def audit(ext,spice,out,check=None):
    ext=Path(ext).read_text().splitlines()
    kinds=Counter(s.split(maxsplit=1)[0] for s in ext if s.strip())
    if any(kinds[k] for k in ("merge","adjust","use")):
        raise ValueError(f"Hierarchical or aliased EXT requires separate resolution: {kinds}")
    alias={}
    for s in ext:
        if s.startswith("equiv "):
            _,canonical,other=shlex.split(s)
            alias[other]=canonical
    scale=next(float(s.split()[2]) for s in ext if s.startswith("scale "))
    ground=next(shlex.split(s)[1] for s in ext if s.startswith("substrate "))
    raw=defaultdict(float)
    rendered=defaultdict(float)
    def key(a,b): return tuple(sorted((alias.get(a,a),alias.get(b,b))))
    for s in ext:
        if s.startswith("node "):
            row=shlex.split(s)
            raw[key(row[1],ground)]+=float(row[3])*scale*.001
        elif s.startswith("cap "):
            _,a,b,v=shlex.split(s)
            raw[key(a,b)]+=float(v)*scale*.001
    for s in Path(spice).read_text().splitlines():
        if re.match(r"^C\d+ ",s):
            _,a,b,v=s.split()[:4]
            match=re.fullmatch(r"([\d.]+)([fp]?)",v)
            if not match:raise ValueError(v)
            val,unit=match.groups()
            rendered[key(a,b)]+=float(val)*{"f":1,"p":1000,"":1e15}[unit]
    rows=sorted(set(raw)|set(rendered))
    with Path(out).open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["node_a","node_b","EXT_fF","SPICE_fF","difference_fF"])
        for a,b in rows:
            w.writerow([a,b,raw[a,b],rendered[a,b],rendered[a,b]-raw[a,b]])
    for v in sorted(rows,key=lambda k:-abs(rendered[k]-raw[k]))[:8]:
        print(v,round(raw[v],5),round(rendered[v],5))
    if check and max(abs(rendered[v]-raw[v]) for v in rows)>.012:
        raise ValueError("Capacitance matrix differs by more than SPICE output rounding (0.012 fF)")
if __name__=="__main__": audit(*sys.argv[1:])
