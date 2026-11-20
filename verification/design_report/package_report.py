"""Package the final design report and measured data; stream large waveform members."""
from pathlib import Path
import shutil, csv, gzip, hashlib, json, os, tempfile
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"docs/ccro_adc_design_report.pdf"
folder=ROOT/"results/design_report";result=ROOT/"results/torture"
def digest(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def main():
    manifest=json.loads((result/"manifest.json").read_text(encoding="utf-8"))
    waves=json.loads((folder/"waveforms/index.json").read_text())
    assert len(waves)+1==manifest["case_count"]
    files={"design_report.pdf":REPORT,"tutorial.pdf":REPORT.with_name("tutorial.pdf"),"test_results.md":ROOT/"docs/torture_T1-T6.md"}
    for name in ("report_sections.md","tutorial_sections.md","report29.py","report18.py","layout_summary.py","principles.py","bench_figures.py","layout_atlas.py","xschem_figures.py","export_schematics.tcl","pdf_report.py","startup_panel.py","README.md"):
        files["report_source/"+name]=Path(__file__).with_name(name)
    for source in sorted((ROOT/"review/bench").iterdir()):
        if source.is_file():
            files["review/bench/"+source.name] = source
    files["review/env.sh"] = ROOT/"review/env.sh"
    for source in sorted((ROOT/"review/xschem").iterdir()):
        if source.suffix in (".sch", ".sym") or source.name == "review.rc":
            files["review/xschem/"+source.name] = source
    for name in ("T3_fft_bins.csv","T3_fft_frames.csv","A5_fft_bins.csv","A5_codes.csv","summary.json"):
        files["spectra/"+name]=folder/"spectra"/name
    for name in ("tt_adc_pio_rx.py","analyze_sndr.py"):
        files["tools/"+name] = ROOT/"tools"/name
    files["analysis/spectra.py"]=Path(__file__).with_name("spectra.py")
    for name in ("analyze_sndr.py","vco_adc_model.py"):
        files["analysis/"+name]=ROOT/"tools"/name
    files["baseline/front_noise.csv"]=ROOT/"results/audited/front_noise.csv"
    files["analysis/README.md"]=Path(__file__).with_name("README.md")
    for name in ("noise_terms.json","passives.txt","digital_current.csv","bias_tt_2.csv","bias_tt_3.csv","route_extent.json"):
        files["bench/"+name]=folder/name
    for name in ("noise_terms.py","current.py","current_tb.v","current_sta.tcl","passives.cir","route_extent.py"):
        files["analysis/"+name]=Path(__file__).with_name(name)
    for source in (folder/"characterization").iterdir():
        if source.suffix in (".csv", ".json", ".md"):
            files["characterization/"+source.name] = source
    for name in ("characteristic_curves.py", "pvt_results.py", "step_figure.py"):
        files["analysis/"+name] = Path(__file__).with_name(name)
    for name in ("pvt_characterization.py", "input_admittance.py", "latency_pex.py", "step_spi.py", "step_spi_tb.v", "ideal_latency.py", "ideal_latency_tb.v"):
        files["design/verification/design_report/"+name] = Path(__file__).with_name(name)
    for name in ("verification/a0.py", "verification/pair.py", "verification/torture/bench.py",
                 "analog/frontend.spice", "analog/ccro.spice", "results/audited/interface_caps.spice"):
        files["design/"+name] = ROOT/name
    for name in ("figures","waveforms"):
        for f in (folder/name).iterdir():
            if f.suffix in (".png",".svg",".gz",".json",".md",".lyrdb"):files[f"{name}/{f.name}"]=f
    for f in result.glob("*.json"):files["measurements/"+f.name]=f
    for name in ("final_tt.csv","final_ss.csv","final_dynamic.csv","final_loaded_dynamic.csv","final_loaded_small.csv","final_slow.csv","final_loaded_fast.csv",
                 "final_noise_budget.csv","front_mismatch.csv","front_noise.txt","final_spi.txt","interface_caps.csv","a0_pvt_fit.csv"):
        files["baseline/"+name]=ROOT/"results/audited"/name
    files["baseline/release_gate.json"]=ROOT/"results/release_gate.json"
    files["baseline/final_functional.txt"]=ROOT/"results/readout/final_functional.txt"
    files["baseline/tile_sta_max.log"]=ROOT/"results/readout/tile_sta_max.log"
    files["baseline/tile_sta_min.log"]=ROOT/"results/readout/tile_sta_min.log"
    files["baseline/verification_status.md"]=ROOT/"docs/verification_status.md"
    signoff=folder/"submission_check.txt"
    if signoff.exists():files["baseline/submission_check.txt"]=signoff
    physical=folder/"physical_check.txt"
    if physical.exists():files["baseline/physical_check.txt"]=physical
    if (ROOT/"LICENSE").is_file():
        files["design/LICENSE"]=ROOT/"LICENSE"
    files["design/LICENSE.third-party"]=ROOT/"LICENSE.third-party"
    files["design/NOTICE"]=ROOT/"NOTICE"
    for name in ("analog/frontend_lowrail.spice","analog/ccro_lowrail.spice","layout/integration/final_analog_c.spice",
                 "gds/tt_um_eleva_ccro_adc.gds","rtl/adc_readout.v","layout/readout/adc_readout.nl.v"):
        files["design/"+name]=ROOT/name
    for name in ("layout/readout/adc_readout.def", "review/digital/state_mapping.tsv",
                 "review/klayout_checklist.md", "review/probe_points.lyrdb", "review/logs/gds_labels.tsv",
                 "review/logs/connectivity.log", "review/logs/lvs_tile.txt"):
        files["design/"+name] = ROOT/name
    files["waveforms/README.md"]=Path(__file__).with_name("waveform_guide.md")
    # Verify every CSV's header, row count and finite numeric endpoints before delivery.
    for c,expected in waves.items():
        wave=folder/"waveforms"/expected["file"]
        from math import isclose
        with gzip.open(wave,"rt") as f:
            fields=next(f).strip().split(",")
            assert fields==expected["columns"] and fields[0]=="time_s",c
            first=next(f);last=first;count=1
            for last in f:count+=1
            assert count==expected["points"],c
            assert isclose(float(first.split(",")[0]),expected["start_s"],rel_tol=1e-7,abs_tol=1e-16),c
            assert isclose(float(last.split(",")[0]),expected["end_s"],rel_tol=1e-7),c
    with gzip.open(folder/"waveforms/T6_gate.csv.gz","rt") as f:
        n=sum(1 for _ in f)-1
        assert n==json.loads((result/"T6.json").read_text())["gates"]["ticks"]
    hashes={name:digest(f) for name,f in files.items()}
    dest=ROOT.parent/"SKY26e_CCRO_ADC_Design_Report.zip"
    with tempfile.NamedTemporaryFile(dir=dest.parent,suffix=".zip",delete=False) as f:tmp=Path(f.name)
    try:
        with ZipFile(tmp,"w") as z:
            for name,f in sorted(files.items()):z.write(f,name,compress_type=ZIP_STORED if name.endswith(".gz") else ZIP_DEFLATED)
            z.writestr("SHA256SUMS","".join(f"{v}  {k}\n" for k,v in sorted(hashes.items())),compress_type=ZIP_DEFLATED)
        with ZipFile(tmp) as z:
            assert z.testzip() is None and len(z.namelist())==len(files)+1
            for name,expected in hashes.items():
                with z.open(name) as stream:assert hashlib.file_digest(stream,"sha256").hexdigest()==expected,name
        tmp.replace(dest)
    finally:tmp.unlink(missing_ok=True)
    print(dest,dest.stat().st_size,digest(dest))
if __name__=="__main__":main()
