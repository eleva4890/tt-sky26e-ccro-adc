"""Export measured analog samples and scientific plots for the design report."""
from pathlib import Path
import argparse, csv, gzip, hashlib, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"verification/torture"))
from bench import raw, WORK, TAPS
from report import CASES
from score import phases
OUT=ROOT/"results/design_report"
FIG=OUT/"figures"
WAVE=OUT/"waveforms"
for d in (FIG,WAVE):d.mkdir(exist_ok=True,parents=True)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.labelcolor":"#213d4a","xtick.color":"#385563",
 "ytick.color":"#385563","axes.edgecolor":"#bdcdd0","axes.spines.top":False,"axes.spines.right":False,"axes.axisbelow":True,
 "grid.color":"#dce5e7","grid.linewidth":.6,"axes.grid":True,"legend.frameon":False,"savefig.facecolor":"white"})
TEAL="#007d73"; ORANGE="#cb5b32"; BLUE="#355d95"; GRAY="#687985"; GOLD="#a57921"
def graph(w=7,h=2.45):
    f,ax=plt.subplots(figsize=(w,h),layout="constrained")
    return f,ax
def save(f,name):
    f.savefig(FIG/(name+".png"),dpi=235,pad_inches=.015);plt.close(f)
def csvrows(name):
    with (ROOT/"results/audited"/name).open() as f:return list(csv.DictReader(f))
def transfer():
    fig,aa=plt.subplots(1,2,figsize=(7.1,2.55),layout="constrained")
    for name,color,lab in [("final_tt.csv",TEAL,"TT / 1.80 V"),("final_ss.csv",ORANGE,"SS / 1.62 V")]:
        d=csvrows(name);xx=np.array([float(r["diff_V"])*1000 for r in d])
        yy=[float(r["fp_MHz"])-float(r["fn_MHz"]) for r in d]
        aa[0].plot(xx,yy,"o-",color=color,label=lab,ms=3,lw=1.5)
    aa[0].set(xlabel="Differential input (mV)",ylabel="Frequency difference (MHz)");aa[0].legend(fontsize=8)
    d=csvrows("final_loaded_small.csv")
    x=np.array([float(r["diff_V"])*1000 for r in d]);y=np.array([(float(r["fp_MHz"])-float(r["fn_MHz"]))*1e3 for r in d])
    aa[1].plot(x,x*6.9,":",color=GRAY,label="6.9 kHz/mV reference")
    aa[1].plot(x,y,"o-",color=TEAL,label="Loaded extraction",ms=4)
    aa[1].set(xlabel="Differential input (mV)",ylabel="Frequency difference (kHz)");aa[1].legend(fontsize=8)
    save(fig,"transfer")
def series(w,n):return w["v("+n+")"]
def waves(case):
    result=json.loads((ROOT/f"results/torture/{case}.json").read_text())
    return raw(WORK/result.get("measured_case",case)/"waves.raw")
def export(case,w):
    # Include every saved probe so the all-stage tests can be recalculated from CSV.
    names=list(w)
    columns=["time_s" if name=="time" else name for name in names]
    dst=WAVE/(case+".csv.gz")
    with gzip.open(dst,"wt",compresslevel=5,newline="") as f:
        f.write(",".join(columns)+"\n")
        # Bound working memory on the high-bandwidth tests.
        for ix in range(0,len(w["time"]),8192):
            block=np.column_stack([w[n][ix:ix+8192] for n in names])
            np.savetxt(f,block,fmt="%.9g",delimiter=",")
    return dict(file=dst.name,points=len(w["time"]),columns=columns,start_s=float(w["time"][0]),end_s=float(w["time"][-1]))
def startup(w):
    t=w["time"]*1e6;sel=t<1.6
    f,ax=graph()
    for key,lab,c in [("xadc.pa0","P ring, stage 0 / A",TEAL),("xadc.pb0","P ring, stage 0 / B",ORANGE),("xadc.rp","Ring supply",GRAY)]:
        ax.plot(t[sel],series(w,key)[sel],color=c,label=lab,lw=1.3 if key!="xadc.rp" else .85)
    ax.set(xlabel="Time from release (us)",ylabel="Voltage (V)",xlim=(0,1.6));ax.legend(ncol=3,fontsize=8,loc="upper right")
    save(f,"startup")
def brownout(w):
    t=w["time"]*1e6
    f,aa=plt.subplots(1,2,figsize=(7.1,2.3),gridspec_kw={"width_ratios":[1.25,1]},layout="constrained")
    for ax,mask in [(aa[0],t>=0),(aa[1],(t>=55.9)&(t<=57.3))]:
        for k,lab,c in [("vdd","Supply",GRAY),("xadc.vb","Bias",ORANGE),("p0","Tap P0",TEAL)]:
            ax.plot(t[mask],series(w,k)[mask],color=c,lw=.85,label=lab)
        ax.set(xlabel="Time (us)",ylim=(-.09,2.1))
    aa[0].set_ylabel("Voltage (V)");aa[1].legend(ncol=3,fontsize=7,loc="upper right")
    save(f,"brownout")
def supply_ramp(w):
    t=w["time"]*1000
    x=np.linspace(t[0],t[-1],3600)
    f,ax=graph(7,2)
    ax.plot([0,10,10.1],[0,1.8,1.8],ls="--",color=GRAY,lw=1.2,label="Specified ramp")
    for key,c,lab in [("vdd",TEAL,"VDPWR"),("xadc.vb",ORANGE,"Bias VB"),("xadc.rp",BLUE,"Ring supply RP")]:
        ax.plot(x,np.interp(x,t,series(w,key)),color=c,lw=1,label=lab)
    ax.set(xlim=(0,10.15),xlabel="Time (ms)",ylabel="Voltage (V)")
    ax.legend(ncol=4,fontsize=8);save(f,"slow_ramp")
def dirty_rails(w):
    t=w["time"]*1e6;mask=(t>=39.25)&(t<=39.6)
    fig,(a,b)=plt.subplots(1,2,figsize=(7.15,2.45),gridspec_kw={"width_ratios":[1.12,1]},layout="constrained")
    a.plot(t[mask],(series(w,"vdd")[mask]-1.8)*1000,label="VDPWR - 1.8 V",color=ORANGE,lw=1)
    a.plot(t[mask],series(w,"vg")[mask]*1000,label="VGND",color=BLUE,lw=1)
    a.plot(t[mask],(series(w,"vdd")[mask]-series(w,"vg")[mask]-1.8)*1000,label="Local supply - 1.8 V",color=TEAL,lw=1)
    a.set(xlabel="Time (us)",ylabel="Rail deviation (mV)");a.legend(fontsize=6.7,loc="best")
    gate=json.loads((ROOT/"results/torture/T3_gate.json").read_text())
    freq=np.arange(1,9)*156.25/16
    for label,key,dx,color in [("Quiet","clean_codes",-1.25,BLUE),("Injected","dirty_codes",1.25,ORANGE)]:
        x=np.array(gate[key],dtype=float);p=np.abs(np.fft.rfft(x-x.mean()))**2;p[-1]*=.5
        db=10*np.log10(np.maximum(p[1:]/p[2],1e-11))
        b.bar(freq+dx,db+110,bottom=-110,width=2.3,color=color,label=label)
    b.set(xlabel="SPI output spectrum (kHz)",ylabel="Bin power (dBc)",ylim=(-110,6))
    b.legend(fontsize=7);save(fig,"ssn")
def dynamic(w):
    t=w["time"]*1e6
    grid=np.linspace(13,51,1501)
    f,ax=graph(7,2.22)
    for side,color in zip("pn",(TEAL,ORANGE)):
        ph=[]
        for i in range(15):
            sig=series(w,f"{side}{i}")-.9
            for up in (True,False):
                k=np.flatnonzero((sig[:-1]<0)&(sig[1:]>=0)) if up else np.flatnonzero((sig[:-1]>0)&(sig[1:]<=0))
                ed=t[k]-sig[k]*np.diff(t)[k]/(sig[k+1]-sig[k])
                ph.append(np.interp(grid,ed,np.arange(len(ed))))
        p=np.mean(ph,axis=0)
        # 0.25 us symmetric slope of interpolated average phase, in MHz.
        dt=grid[10:]-grid[:-10]
        ax.plot((grid[10:]+grid[:-10])/2,(p[10:]-p[:-10])/dt,color=color,label="Ring "+side.upper(),lw=1.25)
    ax.set(xlabel="Time (us)",ylabel="Ring frequency (MHz)");ax.legend(ncol=2)
    save(f,"dynamic")
def t5plot():
    f,ax=graph(7,2.25)
    for mid,color,label in [(0,TEAL,"Mask design"),(1,ORANGE,"10 x 10 um midpoint MIM")]:
        pts=[json.loads((ROOT/f"results/torture/T5_{mid}_{s}.json").read_text()) for s in ("removed",0,1,5,20,50)]
        ax.plot([r["total_direct_fF"] for r in pts],[r["phase_fit_kHz"] for r in pts],"o-",color=color,label=label,ms=4)
    ax.axvline(4.1989,ls=":",color=GRAY,lw=1,label="PEX 4.1989 fF")
    ax.axvline(20.9945,ls="--",color=BLUE,lw=1,label="5x margin")
    ax.axhspan(-.69,.69,color="#dceeea",alpha=.65,zorder=0)
    ax.axhline(6.9,ls=":",color=GOLD,lw=1,label="Linear response at 1 mV")
    ax.set(xlabel="Total direct ring-to-ring coupling (fF)",ylabel="Frequency difference (kHz)")
    ax.legend(ncol=2,fontsize=8);save(f,"locking")
def long_phase():
    grid=np.linspace(18,178,3201)
    fig,(wide,detail)=plt.subplots(1,2,figsize=(7.1,2.55),layout="constrained")
    wide.plot(grid,(grid-grid[0])*.0069,":",color=GRAY,label="Linear response")
    for case,label,color in [("T5_hold","Mask design",TEAL),("T5_hold_mid","Midpoint MIM",ORANGE)]:
        tap_edges=phases(waves(case))
        phi=np.array([np.interp(grid,ed,np.arange(len(ed))) for ed in tap_edges])
        delta=phi[:15].mean(0)-phi[15:].mean(0)
        for ax in (wide,detail):
            ax.plot(grid,delta-delta[0],lw=1.2,color=color,label=label)
    for ax in (wide,detail):
        ax.set(xlabel="Time from power-up (us)",ylabel="Relative phase change (cycles)")
    wide.legend(fontsize=7);detail.legend(fontsize=7)
    save(fig,"long_phase")
def digital():
    with gzip.open(WAVE/"T6_gate.csv.gz","rt") as f:
        rows=list(csv.DictReader(f))
    active=next(i for i in range(505,len(rows)) if rows[i]["clean_cs_n"]=="0" and rows[i-1]["clean_cs_n"]=="1")
    sl=rows[active-5:active+70];xx=np.array([int(x["tick"]) for x in sl])-active
    f,ax=graph(7,1.95)
    for col,label,y,c in [("clean_cs_n","CS_N",2,BLUE),("clean_sclk","SCLK",1,TEAL),("clean_sdo","SDO",0,ORANGE)]:
        ax.step(xx,np.array([int(r[col]) for r in sl])*.57+y,where="post",color=c,lw=1.3)
    ax.set(yticks=[.25,1.25,2.25],yticklabels=["SDO","SCLK","CS_N"],xlabel="20 MHz clock cycles from CS assertion",ylim=(-.15,2.75))
    save(f,"spi")
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("cases",nargs="*");ap.add_argument("--plots-only",action="store_true");opt=ap.parse_args()
    transfer()
    if (WAVE/"T6_gate.csv.gz").exists():digital()
    all_cases=opt.cases or CASES[:-1];index={}
    for case in all_cases:
        w=waves(case)
        if not opt.plots_only:index[case]=export(case,w)
        if case=="T1_tt_0":startup(w)
        if case=="T2_brown":brownout(w)
        if case=="T2_ramp":supply_ramp(w)
        if case=="T3_dirty":dirty_rails(w)
        if case=="T4_series":dynamic(w)
        if len(all_cases)>6:print(case,flush=True)
    if set(CASES[:-1])<=set(index):
        t5plot();long_phase()
        (WAVE/"index.json").write_text(json.dumps(index,indent=2)+"\n")
