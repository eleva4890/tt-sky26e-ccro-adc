"""Retain tap-to-tap coupling and collapse the remaining load network to AC ground."""
import csv, re, shlex, sys
from pathlib import Path
from collections import defaultdict
p=Path(sys.argv[1])
dest=Path(sys.argv[2])
ids={f"ext_{side}{i}" for side in "pn" for i in range(15)}
ground={}
couplings=defaultdict(float)
for line in p.read_text().splitlines():
    if line.startswith("scale "): unit=float(line.split()[2])*.001
    elif line.startswith("node "):
        name=line.split('"',2)[1]
        if name in ids:ground[name]=float(shlex.split(line)[3])*unit
    elif line.startswith("cap "):
        _,a,b,c=shlex.split(line)
        if a in ids or b in ids:
            if b not in ids:b="0"
            if a not in ids:a="0"
            couplings[tuple(sorted((a,b)))]+=float(c)*unit
if set(ground)!=ids:raise ValueError(ids-set(ground))
for n,c in ground.items():couplings["0",n]+=c
lines=["* Final tile routing and receiver-metal capacitance, fF. Receiver transistor load is separate."]
total=defaultdict(float)
for (a,b),c in sorted(couplings.items()):
    if c<0:raise ValueError((a,b,c))
    a,b=a.removeprefix("ext_"),b.removeprefix("ext_")
    lines.append(f"Cio{len(lines)} {a} {b} {c:.7f}f")
    total[a]+=c
    total[b]+=c
(dest/"interface_caps.spice").write_text("\n".join(lines)+"\n")
with (dest/"interface_caps.csv").open("w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["pin","external_metal_C_fF"])
    w.writerows((n,total[n]) for n in sorted(total) if n!="0")
print("30 external tap loads (fF, quiet neighbours)",min(total[n] for n in total if n!="0"),max(total[n] for n in total if n!="0"))
