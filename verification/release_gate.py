"""Evaluate the prototype release criteria against final mask and electrical reports."""
import csv
import hashlib
import json
import re
from pathlib import Path
import numpy as np
from evaluate_a4 import static, dynamic

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"results"
A=R/"audited"
TOP="tt_um_eleva_ccro_adc"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path): 
    with path.open() as file: return list(csv.DictReader(file))
def text(name): return (R/name).read_text()
def need(ok,msg):
    if not ok: raise ValueError(msg)
def valid_sweep(path,corner,vdd):
    data=rows(path)
    need(len(data)==11 and np.allclose(sorted(float(r["diff_V"]) for r in data),np.linspace(-.2,.2,11)),path)
    need(all(r["corner"]==corner and float(r["vdd_V"])==vdd and float(r["cm_V"])==.63
             and int(r["bias"])==0 and float(r["temp_C"])==27 for r in data),path)
    return data

def audit():
    tile=ROOT/"gds"/(TOP+".gds")
    lef=ROOT/"lef"/(TOP+".lef")
    mask=sha(tile)
    for p in (tile,lef):need(sha(p)==sha(ROOT/"layout/integration"/p.name),p)
    need(mask==text("top_precheck.sha256").strip()==text("top_signoff.sha256").strip(),"signoff mask digest")
    checks=re.findall(r"^\| ([^|]+) \| ✅ \|$",text("top_precheck.md"),re.M)
    need(len(set(checks))==17 and {"lvtn/nwell check", "hvtp/nwell check"} <= set(checks) and "❌" not in text("top_precheck.md"),"official precheck")
    need(text("top_drc.txt").strip()=="FULL_DRC_TYPES 0","tile Magic DRC")
    need(text("top_beol.txt").strip()=="TOTAL 0","BEOL")
    lvs=text("top_lvs.txt")
    need("Circuits match uniquely." in lvs and "property errors" not in lvs.lower(),"tile LVS")
    need("ANTENNA_FEEDBACK 0"==text("top_antenna.txt").strip(),"tile antenna")
    need("TRACE SUMMARY 64/64 signal connections; 0 shorted port groups" in text("top_connectivity.txt"),"tile pin trace")
    need("Documentation check passed successfully" in text("tt_docs.txt"),"official project metadata")
    need(mask==text("rebuilt_masks.sha256").split()[0],"independent mask regeneration")
    need(text("final_analog_drc.txt").strip()=="FULL_DRC_TYPES 0" and "Circuits match uniquely." in text("final_analog_lvs.txt"),"analog macro")
    cells,nets=(int(re.search("Number of "+k+r":\s+(\d+)",lvs)[1]) for k in ("devices","nets"))
    slacks=[]
    for rc in ("min","nom","max"):
        s=[float(v) for v in re.findall(r"^worst slack ([-\d.]+)",text(f"readout/tile_sta_{rc}.log"),re.M)]
        need(len(s)==2 and min(s)>=0,"STA "+rc)
        slacks.append(s)
    rtl=text("readout/final_functional.txt")
    need(rtl.count("PASS: 13800 checked clocks, 70 complete frames")==2 and rtl.count("PASS: /64")==2,"RTL and gate simulation")
    spi=text("audited/final_spi.txt")
    need(all(f"3 frames, sign {s}" in spi for s in [-1,1]) and spi.count("PASS:")==2,"mixed simulation")
    a0=rows(A/"a0_pvt_fit.csv")
    need({(r["corner"],int(float(r["temp_C"]))) for r in a0}=={(c,t) for c in ("tt","ss","ff") for t in (-20,27,85)} and all(int(r["points"])==21 for r in a0),"A0 PVT")
    sweep=rows(A/"a0_pvt.csv")
    grid={(r["corner"],int(r["temp_C"]),round(float(r["current_uA"]),3)) for r in sweep}
    need(len(sweep)==189 and grid=={(c,t,round(6.5+.35*i,3)) for c in ("tt","ss","ff")
                                   for t in (-20,27,85) for i in range(21)},"A0 tested current grid")
    ss=valid_sweep(A/"final_ss.csv","ss",1.62)
    tt=valid_sweep(A/"final_tt.csv","tt",1.8)
    min_tail=min(min(float(r[k]) for k in ("tailp_vsd","tailn_vsd")) for r in ss)
    need(min_tail>=.20,"SS tail compliance")
    tt_hd=static(A/"final_tt.csv")
    ss_hd=static(A/"final_ss.csv")
    ac_hd=dynamic(A/"final_dynamic.csv")
    need(all(r["corner"]=="tt" and float(r["input_Hz"])==50000 and float(r["vdd_V"])==1.80 and
             float(r["amplitude_Vdiff"])==.2 and int(r["cycles"])==2 for r in rows(A/"final_dynamic.csv")),"dynamic test conditions")
    deltas={n:abs(tt_hd[n]-ac_hd[n]) for n in (2,3)}
    loaded_hd=dynamic(A/"final_loaded_dynamic.csv")
    for case,h in [("TT static",tt_hd),("SS static",ss_hd),("TT dynamic",ac_hd),("TT loaded dynamic",loaded_hd)]:
        for n,lim in ((2,-66),(3,-62)):need(h[n]<=lim,f"{case} HD{n} = {h[n]:.3f} dBc")
    need(deltas[3]<=1,f"HD3 static/dynamic difference {deltas[3]}")
    vx=np.array([float(r["diff_V"])/.2 for r in tt])
    fy=np.array([float(r["fp_MHz"])-float(r["fn_MHz"]) for r in tt])
    h7=np.polynomial.chebyshev.chebfit(vx,fy,7)
    hd2_degree7=float(20*np.log10(abs(h7[2]/h7[1])))
    small=rows(A/"final_small.csv")
    dfs={round(float(r["diff_V"])*1000):1000*(float(r["fp_MHz"])-float(r["fn_MHz"])) for r in small}
    need(set(dfs)=={-10,-3,0,3,10} and dfs[-10]<dfs[0]<dfs[10],"small-input polarity")
    loadsmall=rows(A/"final_loaded_small.csv")
    ldfs={round(float(r["diff_V"])*1000):1000*(float(r["fp_MHz"])-float(r["fn_MHz"])) for r in loadsmall}
    need(set(ldfs)=={-10,-3,-1,0,1,3,10} and ldfs[-10]<ldfs[0]<ldfs[10],"loaded small-input polarity")
    zero=next(r for r in small if float(r["diff_V"])==0)
    f0=(float(zero["fp_MHz"])+float(zero["fn_MHz"]))/2
    need(abs(dfs[0])<.01*1000*f0 and float(zero["min_internal_diff_pp_V"])>.3,"zero-input start-up")
    slow=rows(A/"final_slow.csv")[0]
    need(slow["corner"]=="sf" and float(slow["temp_C"])==-20 and
         float(slow["worst_lo_V"])<.20 and float(slow["worst_hi_V"])>1.78 and float(slow["fmin30_MHz"])>0 and
         .4<float(slow["duty_min"])<=float(slow["duty_max"])<.6,"slow CVSL")
    fast={}
    for label,file,fs,mode in [("nominal","final_ff_nom.csv",20,0),("fast","final_fast.csv",32,3)]:
        r=rows(A/file)[0]
        fast[label]=float(r["fmax30_MHz"])
        need(r["corner"]=="ff" and float(r["temp_C"])==85 and float(r["vdd_V"])==1.98 and int(r["bias"])==mode and 0<fast[label]<.4*fs,"phase wrap at "+label)
    budget=[float(r["SNDR_dB"]) for r in rows(A/"final_noise_budget.csv")]
    loaded_fast=rows(A/"final_loaded_fast.csv")[0]
    need(0<float(loaded_fast["fmax30_MHz"])<12.8,"loaded FF speed")
    need(len(budget)==9 and np.all(np.isfinite(budget)),"noise model")
    mc=rows(A/"front_mismatch.csv")
    need(len(mc)==50 and len({r["df0_MHz"] for r in mc})==50,"50 distinct mismatch samples")
    need(all(r["interpolation_in_range"]=="True" for r in mc),"mismatch currents outside characterized ring response")
    return dict(gds_sha256=mask,lef_sha256=sha(lef),analog_pex_sha256=sha(ROOT/"layout/integration/final_analog_c.spice"),
                official_checks=len(checks),devices=cells,nets=nets,setup_ns=min(s[0] for s in slacks),hold_ns=min(s[1] for s in slacks),
                PVT_points=21*len(a0),HD_TT_static=tt_hd,HD_SS_static=ss_hd,HD_TT_50kHz=ac_hd,HD_loaded_TT_50kHz=loaded_hd,static_dynamic_delta_dB=deltas,
                HD2_degree7_TT_dBc=hd2_degree7,HD2_agreement_4dB_reference_met=bool(deltas[2]<=4),
                diff_kHz_by_mV=dfs,loaded_diff_kHz_by_mV=ldfs,zero_f0_MHz=f0,minimum_SS_tail_V=min_tail,slow_min_MHz=float(slow["fmin30_MHz"]),
                fast_max_MHz=fast,noise_budget_range_dB=[min(budget),max(budget)],front_mismatch_draws=len(mc),
                front_mismatch_in_range=sum(r["interpolation_in_range"]=="True" for r in mc),
                mixed_frame_codes=[int(v) for v in re.findall(r"frame \d+ signed code (-?\d+)",spi)])
if __name__=="__main__":
    data=audit()
    (R/"release_gate.json").write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(data,ensure_ascii=False))
