"""Verify that each proof fails on a known defect; alter only temporary copies."""
import json, os, re, subprocess, tempfile
from pathlib import Path
review=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as tmp:
    cwd=Path(tmp)
    # Widen just the principal A-side pull-up in every instantiated ring stage.
    src=(review/"netlists/xschem.spice").read_text()
    src,n=re.subn(r"(?mi)^(XMmainA_Xp\s+[^\n]*?\bW=)8\.4\b",r"\g<1>12.6",src)
    assert n==1
    (cwd/"changed.spice").write_text(src)
    (cwd/"mask.spice").write_bytes((review/"netlists/analog_mask.spice").read_bytes())
    subprocess.run(["netgen","-batch","lvs","mask.spice eleva_adc_analog","changed.spice adc_analog",
                    str(Path(os.environ["PDK_ROOT"])/"sky130A/libs.tech/netgen/sky130A_setup.tcl"),"changed.log","-json"],
                   cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True)
    report=(cwd/"changed.log").read_text()
    data=json.loads((cwd/"changed.json").read_text())
    assert any(rec.get("properties") for rec in data), data[-1].keys()
    excerpts=[s.strip() for s in report.splitlines() if "property errors" in s.lower() or "12.6" in s]
    assert excerpts
    (review/"logs/control_lvs.txt").write_text("Negative control: stage XmainA_Xp W=8.4 -> 12.6 um\n"+"\n".join(excerpts[:5])+"\nPASS: Netgen reported a property mismatch.\n")
    m=json.loads((review/"digital/step.json").read_text())
    gate=m["modules"]["gate"]
    original=gate["ports"]["sdo"]["bits"]
    fresh=max(bit for c in gate["cells"].values() for bits in c["connections"].values() for bit in bits if isinstance(bit,int))+1
    gate["cells"]["$injected_output_inverter"]={"type":"$_NOT_","hide_name":1,"parameters":{},"attributes":{},
        "port_directions":{"A":"input","Y":"output"},"connections":{"A":original,"Y":[fresh]}}
    gate["ports"]["sdo"]["bits"]=[fresh]
    gate["netnames"]["sdo"]["bits"]=[fresh]
    (cwd/"defect.json").write_text(json.dumps(m))
    src=(review/"digital/equivalence.ys").read_text().replace("review/digital/step.json","defect.json")
    (cwd/"check.ys").write_text(src)
    run=subprocess.run(["yosys","-Q","-s","check.ys"],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    assert run.returncode!=0 and "unproven" in run.stdout
    lines=[s.strip() for s in run.stdout.splitlines() if "unproven" in s.lower() or ("sdo" in s and "failed" in s)]
    (review/"logs/control_formal.txt").write_text("Negative control: invert routed SDO at observable port\n"+"\n".join(lines[-6:])+"\nPASS: equiv_status -assert rejected defect.\n")

