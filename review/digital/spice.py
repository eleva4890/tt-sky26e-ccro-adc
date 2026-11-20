"""Bind the route Verilog's named standard-cell pins to the PDK transistor library.
The digital reference uses no layout-extracted netlist.
"""
from pathlib import Path
import re, os, hashlib
from collections import Counter

review=Path(__file__).resolve().parents[1]
pdk=Path(os.environ["PDK_ROOT"])/"sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice"
source=pdk.read_text()
library={m[1]:(m[2].split(),m[0]) for m in re.finditer(r"(?mi)^\.subckt (\S+) ([^\n]*)\n[\s\S]*?^\.ends[^\n]*",source)}
rtl=(review.parent/"layout/readout/adc_readout.nl.v").read_text()
pattern=r"(?ms)^\s*(sky130_fd_sc_hd__\w+)\s+(\\?\S+)\s*\((.*?)\);"
all_types=re.findall(r"(?m)^\s*(sky130_fd_sc_hd__\w+)\s+",rtl)
instances=list(re.finditer(pattern,rtl))
assert [m[1] for m in instances]==all_types and not re.search(r"\bassign\b",rtl)
ports=["VGND","VPWR","clk","cs_n","dbg_mode[0]","dbg_mode[1]"]
ports += [f"debug[{i}]" for i in range(8)]+["err_clr","osr_sel","rst_n","sclk","sdo"]
ports += [f"tap_{side}[{i}]" for side in "np" for i in [0,10,11,12,13,14,1,2,3,4,5,6,7,8,9]]+["wrap_err"]
lines=[".subckt adc_readout "+" ".join(ports)]
used=set()
seen=set()
for match in instances:
    model,name,body=match.groups()
    name=name.lstrip("\\")
    assert name not in seen
    seen.add(name)
    fields=dict(re.findall(r"\.(\w+)\s*\(\s*([^()]*?)\s*\)",body))
    assert not re.sub(r"\.\w+\s*\([^()]*\)|[\s,]","",body)
    cell_ports=library[model][0]
    # These are the only physical loads omitted by the Boolean comparison.
    if any(x in model for x in ("__fill_", "__decap_", "__tapvpwrvgnd_","__diode_")):
        signal_pins=set(cell_ports)-{"VPWR","VGND","VPB","VNB"}
        assert signal_pins==({"DIODE"} if "__diode_" in model else set())
    for pg,rail in dict(VPWR="VPWR",VGND="VGND",VPB="VPWR",VNB="VGND").items():
        if pg in cell_ports:
            assert pg not in fields
            fields[pg]=rail
    # Unconnected output pins have a unique floating net.
    for p in cell_ports:
        if p not in fields:
            assert p in {"COUT","SUM","LO","HI","Q","X","Y"},(model,p)
            fields[p]=f"open_{name}_{p}"
    assert set(fields)==set(cell_ports)
    nets=[fields[p].lstrip("\\").replace(" ","") for p in cell_ports]
    assert all(re.fullmatch(r"[\w.$\[\]/-]+",n) for n in nets),nets
    lines.append("X"+name+" "+" ".join(nets)+" "+model)
    used.add(model)
lines.append(".ends")
output=review/"netlists/digital_reference.spice"
output.write_text("* Route Verilog connectivity + foundry standard-cell schematics\n"+
                  "\n".join(library[m][1] for m in sorted(used))+"\n"+"\n".join(lines)+"\n")
print("route instances",len(instances),"unique PDK cell masters", len(used))
print("PDK standard cell SPICE SHA-256",hashlib.sha256(pdk.read_bytes()).hexdigest())

