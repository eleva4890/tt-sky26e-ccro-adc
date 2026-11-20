"""Fail closed on mismatched pins, devices, nets, properties, GUI or formal results."""
import hashlib,json,re
from pathlib import Path
review=Path(__file__).resolve().parent
logs=review/"logs"
lines=[]
for name,n1,n2,pins in [("core","eleva_adc_analog","adc_analog",36),("tile","tile_mask","tt_um_eleva_ccro_adc",53)]:
    raw=(logs/f"lvs_{name}.txt").read_text()
    assert raw.rstrip().endswith("Circuits match uniquely.")
    assert "Cell pin lists are equivalent." in raw and not re.search(r"property errors|Netlists do not match",raw,re.I)
    data=json.loads((logs/f"lvs_{name}.json").read_text())
    top=next(c for c in data if c["name"]==[n1,n2])
    for c in data:
        for key in ("badnets","badelements","properties"):
            assert not c.get(key),(name,key,c.get(key))
    a,b=map(dict,top["devices"])
    assert a==b and top["nets"][0]==top["nets"][1]
    pp,qq=top["pins"]
    assert len(pp)==len(set(pp))==pins and pp==qq
    lines.append(f"PASS {name:4} LVS  {n1} <-> {n2}  devices {sum(a.values())}/{sum(b.values())}, nets {top['nets'][0]}/{top['nets'][1]}, pins {pins}/{pins}, Property errors = 0")
formal=(logs/"formal_equivalence.log").read_text()
match=re.search(r"Of those cells (\d+) are proven and 0 are unproven",formal)
assert match and "Equivalence successfully proven!" in formal
status=(logs/"state_mapping.log").read_text()
assert "matched 239 of 239 239" in status
lines.append(f"PASS RTL/routed equivalence  {match[1]}/{match[1]} proven, 0 unproven; 239/239 state bits (235 FF + 4 latches)")
assert "TRACE SUMMARY 64/64 signal connections; 0 shorted port groups" in (logs/"connectivity.log").read_text()
assert "GUI PASS" in (logs/"klayout_gui.log").read_text()
sheets={s.name for s in (review/"xschem").glob("*.sch")}
opened=set(re.findall(r"(?m)^OPEN (\S+.sch)",(logs/"xschem_gui.log").read_text()))
assert sheets==opened
for f in (review/"xschem").glob("*.sch"):
    text=f.read_text()
    assert not re.search(r"(?i)\.include|devices/(code|netlist|simulator_commands)",text)
    inst=[s for s in text.splitlines() if s.startswith("C {") and not s.startswith(("C {devices/iopin","C {devices/lab_pin"))]
    assert 0<len(inst)<=20
    # All wire segments are Manhattan. Detect collinear coincident segments
    # (including partial overlaps), regardless of whether labels agree.
    spans={}
    for x,y,u,v in re.findall(r"(?m)^N ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)",text):
        x,y,u,v=map(float,(x,y,u,v))
        assert (x==u)!=(y==v)
        key,endpoints=(("v",x),(y,v)) if x==u else (("h",y),(x,u))
        left,right=sorted(endpoints)
        assert all(right<=lo or left>=hi for lo,hi in spans.get(key,[])),(f.name,key,endpoints)
        spans.setdefault(key,[]).append((left,right))
assert all((review/"digital"/f).stat().st_size>1000 for f in ["module_hierarchy.svg","pop15.svg"])
assert all("PASS:" in (logs/f).read_text() for f in ["control_lvs.txt","control_formal.txt"])
lines.extend([f"PASS GUI  {len(sheets)} Xschem sheets; KLayout final GDS and 17 markers",
              "PASS connectivity  64/64 signal connections; 0 shorted external-port groups",
              "PASS negative controls  W change and inverted SDO both detected"])
(logs/"verdict.txt").write_text("\n".join(lines)+"\n")
paths=sorted([*(review/"xschem").glob("*.s*"),review/"xschem/review.rc",review/"inputs/tt_um_eleva_ccro_adc.gds",
              review/"digital/module_hierarchy.svg", review/"digital/pop15.svg",review/"probe_points.lyrdb",
              review/"index.html",review/"SUMMARY.md",review/"klayout_checklist.md",
              *(logs/f for f in ["magic_warnings.txt","magic_extraction_feedback.tcl.gz","state_mapping.log","control_lvs.txt","control_formal.txt"]),
              *(review/"netlists").glob("*.spice"),*(logs/f for f in ["formal_equivalence.log","lvs_core.txt","lvs_tile.txt","lvs_core.json","lvs_tile.json","verdict.txt","deck_provenance.txt"])])
(logs/"review_files.sha256").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(review)}\n" for p in paths))
print("\n".join(lines))

