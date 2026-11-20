"""Package the reviewed branch and verify every archived byte against its SHA-256 manifest."""
from pathlib import Path
from hashlib import sha256
import tempfile
import zipfile
import os
import re
import posixpath
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE_RESULTS={
    "dual_cap_audit.csv","dual_flat_cap_audit.csv","a0_smoke.csv",
}
def write_member(archive,name,data):
    info=zipfile.ZipInfo(name,(2026,11,19,0,0,0))
    info.create_system=3
    mode=0o755 if name.endswith(".sh") else 0o644
    info.external_attr=(0o100000|mode)<<16
    archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)

def package(destination):
    keep=[]
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if rel.parts[0] in {"gds","lef"}:continue
        if "__pycache__" in rel.parts or p.suffix==".pyc":continue
        if "pre_audit" in p.name or "narrow" in p.name:continue
        if p.name.startswith(("io_work","notch_trial")):continue
        if p.name in {"route_trials.sh","roof_space.py","stripe_access.py","fill_notches.py"}:continue
        if rel.parts[0]=="results" and len(rel.parts)>1:
            if rel.parts[1] in {"mixed_taps","osc_taps"}:continue
            if len(rel.parts)==2 and (
                p.name.startswith(("osc_","dual_small","dual_star_small","bank_pex","mixed_spi","mixed_polarity","dual_narrow"))
                and p.name not in {"osc_drc.txt","osc_lvs.txt"}
            ):continue
            if p.name in EXCLUDE_RESULTS:continue
        if rel.parts[0]=="analog" and p.name=="ccro_bank_pex.spice":continue
        if p.stat().st_size==0:raise ValueError(f"Empty file: {rel}")
        keep.append((rel.as_posix(),p))
    for ext in ("gds","lef"):
        name=f"tt_um_eleva_ccro_adc.{ext}"
        keep.append((f"{ext}/{name}",ROOT/"layout/integration"/name))
    fd,tmp=tempfile.mkstemp(suffix=".zip",dir=destination.parent)
    os.close(fd)
    temp=Path(tmp)
    try:
        checks={}
        with zipfile.ZipFile(temp,"w",zipfile.ZIP_DEFLATED,compresslevel=8) as z:
            for name,p in keep:
                data=p.read_bytes()
                checks[name]=sha256(data).hexdigest()
                write_member(z,name,data)
            write_member(z,"SHA256SUMS","".join(f"{digest}  {n}\n" for n,digest in checks.items()))
        with zipfile.ZipFile(temp) as z:
            if z.testzip() is not None or set(z.namelist())!=set(checks)|{"SHA256SUMS"}:
                raise ValueError("ZIP directory or CRC mismatch")
            manifest=z.read("SHA256SUMS").decode().splitlines()
            for row in manifest:
                digest,name=row.split("  ",1)
                if sha256(z.read(name)).hexdigest()!=digest:raise ValueError(name)
            for name in ("layout/analog_cells/eleva_adc_analog.gds","layout/analog_cells/eleva_adc_analog.lef",
                         "layout/readout/adc_readout.gds","layout/readout/adc_readout.lef","docs/verification_status.md",
                         "layout/integration/power_assembly.gds","results/power_drc.txt","results/power_connectivity.txt",
                         "layout/integration/tt_um_eleva_ccro_adc.gds","layout/integration/tt_um_eleva_ccro_adc.lef",
                         "results/audited/a4_v3_1.csv","results/audited/full_dynamic.csv",
                         "results/top_lvs.txt","results/top_precheck.md","results/top_beol_markers.xml"):
                assert name in checks,name
            for report in ("README.md","docs/verification_status.md","verification/README.md"):
                body=z.read(report).decode()
                for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',body):
                    if "://" in target or target.startswith("#"):continue
                    dest=posixpath.normpath(posixpath.join(posixpath.dirname(report),target))
                    if dest not in checks and not any(p.startswith(dest+"/") for p in checks):
                        raise ValueError(f"{report} links to missing {target}")
        temp.replace(destination)
        print(f"{len(checks)} files verified, {destination.stat().st_size} bytes")
        print(sha256(destination.read_bytes()).hexdigest())
    finally:
        if temp.exists():temp.unlink()
if __name__=="__main__":
    package(ROOT.parent/"SKY26e_CCRO_ADC_1x2_Engineering.zip")
