"""Package the SKY26e repository and verify its manifest, documents and signoff mask."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZIP_DEFLATED
import re, posixpath, tempfile, os
from release_gate import audit, ROOT, TOP
from package import write_member

def build(dst):
    data=audit()
    digest=data["gds_sha256"]
    tree=[".github/workflows","gds","lef","src","rtl","tools","layout/readout"]
    files={p.relative_to(ROOT).as_posix() for prefix in tree for p in (ROOT/prefix).rglob("*")
           if p.is_file() and "__pycache__" not in p.parts}
    files.update(["README.md","info.yaml","LICENSE.third-party","NOTICE","docs/info.md","docs/verification_status.md",
                  "docs/01_SPEC.md","docs/02_ANALOG_DESIGN.md","docs/03_LAYOUT_GUIDE.md","docs/04_VERIFICATION_EVAL.md","verification/RELEASE.md",
                  "layout/integration/top_floorplan.def","layout/integration/power_assembly.gds",
                  "layout/integration/final_analog.gds","layout/integration/final_analog_c.spice",
                  "layout/integration/"+TOP+".gds","layout/integration/"+TOP+".lef",
                  "layout/analog_cells/eleva_adc_analog.lef","layout/analog_cells/eleva_frontend_c.spice","layout/timing.sdc",
                  "results/audited/issue1_startup.csv","results/final_analog_drc.txt","results/final_analog_lvs.txt","results/final_analog_matrix.csv",
                  "results/release_gate.json","results/tile_loads.csv","results/tile_loads.tcl",
                  "results/readout/final_functional.txt","results/readout/area.txt","results/readout/lvs.txt",
                  "results/readout/antenna.txt","results/readout/drc.txt"])
    files.update("analog/"+n+".spice" for n in ("top","adc_analog_physical_lvs","osc_extracted","ccro_lowrail","frontend_lowrail","ccro","frontend"))
    files.update("layout/"+n+".py" for n in ("route_io","finalize_routes","space_mim_feeds","bias_antenna","enclose_lvtn"))
    files.update("verification/"+n for n in (
        "finalize_tile.sh","route_diagnostics.py","check_io.py","top_abstract.py","top_signoff.sh","top_extract.tcl",
        "primitive_syntax.py","precheck.sh","drc_summary.py","io_drc.sh","channel.tcl","final_analog.sh",
        "analog_core.tcl","cap_audit.py","tile_loads.py","tile_timing.sh","tile_timing.tcl","interface_geometry.py","interface_extract.tcl",
        "interface_caps.py","interface_caps.sh","test.sh","stimulus.py","readout_tb.v","divider_tb.v","mixed_tb.v","test_mixed.sh",
        "a0.py","fit_a0.py","pair.py","dynamic.py","evaluate_a4.py","noise_budget.py","mismatch_front.py","final_performance.sh",
        "release_gate.py","release_report.py","submission.py","package.py","connect_top.py","tt_docs.sh","check_submission.sh"))
    files.update(p.relative_to(ROOT).as_posix() for p in (ROOT/"results").glob("top*") if p.is_file())
    files.update(p.relative_to(ROOT).as_posix() for p in (ROOT/"results/readout").glob("tile_sta*"))
    for pattern in ("final*","a0_pvt*","a0_mismatch_range.csv","front_mismatch*","interface_caps*","front_noise*","a0.csv","full_small_long.csv"):
        files.update(p.relative_to(ROOT).as_posix() for p in (ROOT/"results/audited").glob(pattern) if p.is_file())
    files.update(p.relative_to(ROOT).as_posix() for p in (ROOT/"results/audited/final_taps").glob("taps*.txt"))
    # This archive contains the current signoff and a self-contained reproduction guide.
    files.add("results/tt_docs.txt")
    files.add("results/rebuilt_masks.sha256")
    fd,tmp=tempfile.mkstemp(dir=dst.parent,suffix=".zip")
    os.close(fd)
    try:
        hashes={}
        with ZipFile(tmp,"w",ZIP_DEFLATED) as z:
            for name in sorted(files):
                entry=(ROOT/name).read_bytes()
                if not entry:raise ValueError(name)
                hashes[name]=sha256(entry).hexdigest()
                write_member(z,name,entry)
            write_member(z,"SHA256SUMS","".join(f"{h}  {n}\n" for n,h in hashes.items()))
        with ZipFile(tmp) as z:
            if z.testzip() or len(z.namelist())!=len(set(z.namelist())):raise ValueError("ZIP integrity")
            for row in z.read("SHA256SUMS").decode().splitlines():
                h,k=row.split("  ",1)
                if sha256(z.read(k)).hexdigest()!=h:raise ValueError(k)
            if hashes["gds/"+TOP+".gds"]!=digest:raise ValueError("signoff digest")
            for doc in ["README.md","docs/info.md","docs/verification_status.md","verification/RELEASE.md"]:
                for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)",z.read(doc).decode()):
                    if "://" in link or link.startswith("#"):continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(doc),link))
                    if target not in hashes:raise ValueError(f"{doc}: missing {target}")
        Path(tmp).replace(dst)
        print(f"{len(hashes)} files; GDS {digest}; ZIP {sha256(dst.read_bytes()).hexdigest()}")
    finally:
        if Path(tmp).exists():Path(tmp).unlink()
if __name__=="__main__":
    build(ROOT.parent/"SKY26e_CCRO_ADC_1x2_Submission.zip")
