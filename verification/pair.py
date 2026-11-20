"""Autonomous supply-ramp test of both rings, all CVSL channels, and the physical bias."""
import argparse
import csv
import os
import re
from pathlib import Path
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from a0 import MODEL, ROOT, RING

def run(c):
    corner,temp,vdd,mode,vd,cm,ramp,settle=c
    cap_side=float(os.environ.get("ADC_RING_CAP_SIDE","21.8"))
    mid_side=float(os.environ.get("ADC_MID_CAP_SIDE","0"))
    trace_dir=os.environ.get("ADC_TRACE_DIR")
    dual=os.environ.get("ADC_DUAL")
    full=os.environ.get("ADC_FULL")
    step_ns=float(os.environ.get("ADC_PAIR_STEP_NS","2"))
    if full and (mid_side or cap_side!=21.8):
        raise ValueError("The fully routed GDS fixes its physical capacitor sizes")
    front=Path(os.environ.get("ADC_FRONT",ROOT/"analog/frontend.spice")).read_text()
    front=front.replace("w=21.8 l=21.8",f"w={cap_side} l={cap_side}")
    if mid_side:
        front=front.replace("Xr0 sp mid",f"Xmid mid g sky130_fd_pr__cap_mim_m3_1 w={mid_side} l={mid_side}\nXr0 sp mid")
    taps=[f"{s}{i}" for s in "pn" for i in range(15)]
    dual_include=""
    if dual:
        block="Xdual rp rn v g "+" ".join(taps)+" dual_flat"
        front,n=re.subn(r"^Xrp [^\n]+ ring\nXrn [^\n]+ ring$",block,front,flags=re.M)
        if n!=1:
            raise ValueError("Expected two independent oscillator instances")
        dual_include=f'.include "{Path(dual).resolve()}"'
    loads="\n".join(f"Cload{i} {pin} 0 5f" for i,pin in enumerate(taps))
    if os.environ.get("ADC_INTERFACE_CAPS"):
        loads+="\n"+Path(os.environ["ADC_INTERFACE_CAPS"]).read_text()
    probes=[f"v({pin})" for pin in taps]
    probes+=["v(xadc.rp)","v(xadc.rn)","v(xadc.xfront.sp)","v(xadc.xfront.sn)","v(xadc.xfront.vb)","i(Vdd)"]
    for s in "pn":
        prefix=f"xadc.xdual.{s}" if dual else f"xadc.xr{s}."
        probes.extend(f"v({prefix}{rail}{i})" for i in range(15) for rail in "ab")
    if full:
        front=Path(full).read_text()
        if os.environ.get("ADC_STUDY_RAIL_COUPLING")=="remove":
            front,n=re.subn(r"(?m)^C\d+ (?:rn rp|rp rn) [^\n]+$", "* rail-coupling sensitivity trial",front)
            if n!=1:raise ValueError("Expected one extracted coupling capacitor between ring supplies")
        study_side=float(os.environ.get("ADC_TEST_MID_SIDE","0"))
        if study_side:
            extra=f"Xstudy_mid mid g sky130_fd_pr__cap_mim_m3_1 w={study_side} l={study_side}\n"
            front,n=re.subn(r"(?m)^\.ends(?: eleva_adc_analog)?[ \t]*$",extra+".ends eleva_adc_analog",front)
            if n!=1:raise ValueError("Cannot identify the physical subcircuit")
            mid_side=study_side
        dual_include=""
        probes=[q.replace("xadc.xfront.","xadc.") for q in probes[:36]]
        probes.extend(f"v(xadc.{s}{rail}{i})" for s in "pn" for i in range(15) for rail in "ab")
    model="eleva_adc_analog" if full else "adc_analog"
    vectors=" ".join(probes)
    # No imposed node voltages, no pulse into the oscillator, both gates track VDD during ramp.
    deck=f"""Autonomous startup and differential response
.lib "{MODEL}" {corner}
.include "{RING}"
{dual_include}
.include frontend.spice
.option scale=1u method=gear reltol=.0005 klu
.temp {temp}
Vdd vdd 0 pwl(0 0 {ramp}u {vdd})
Eb0 b0 0 vdd 0 {mode&1}
Eb1 b1 0 vdd 0 {mode>>1}
Ep ep 0 vdd 0 {(cm+vd/2)/vdd}
En en 0 vdd 0 {(cm-vd/2)/vdd}
Rsp ep vinp 1.5k
Rsn en vinn 1.5k
Cpadp vinp 0 5p
Cpadn vinn 0 5p
Xadc vinp vinn b0 b1 vdd 0 {' '.join(taps)} {model}
{loads}
.control
set num_threads=1
set numdgt=10
set wr_singlescale
save {vectors}
tran {step_ns}n {ramp+settle}u {0 if trace_dir else ramp+settle/2}u {step_ns}n
wrdata waves {vectors}
quit
.endc
.end
"""
    with tempfile.TemporaryDirectory() as tmp:
        d=Path(tmp)
        (d/"frontend.spice").write_text(front)
        (d/"pair.cir").write_text(deck)
        (d/".spiceinit").write_text((MODEL.parent/"spinit").read_text()+"\nset num_threads=1\n")
        p=subprocess.run(["ngspice","-b","pair.cir"],cwd=d,capture_output=True,text=True)
        if not (d/"waves").exists():
            raise RuntimeError((p.stderr[:650],p.stdout[-650:]))
        data=np.loadtxt(d/"waves")
    t=data[:,0]
    if t[-1]<.99999*(ramp+settle)*1e-6:
        raise RuntimeError("Incomplete transient")
    if trace_dir:
        trace=Path(trace_dir)
        trace.mkdir(parents=True,exist_ok=True)
        # At a clock edge, compare interpolated CVSL voltages to half the supply.
        # Input changes in the RTL replay are advanced on the preceding low phase.
        fs=float(os.environ.get("ADC_TRACE_FS","32000000"))
        edges=(np.arange(int(t[-1]*fs))+.5)/fs
        words=np.zeros((len(edges),2),dtype=np.uint16)
        for j in range(30):
            sampled=np.interp(edges,t,data[:,j+1])>vdd/2
            words[:,j//15]|=sampled.astype(np.uint16)<<(j%15)
        with (trace/f"taps_{vd:+.4f}.txt").open("w") as ft:
            for j,(pword,nword) in enumerate(words):
                ft.write(f"{int(edges[j]>(ramp+.5)*1e-6)} {pword:04x} {nword:04x}\n")
        data=data[t>=(ramp+settle/2)*1e-6]
        t=data[:,0]
    signals=data[:,1:31]
    def avg(x):
        fn=np.trapezoid if hasattr(np,"trapezoid") else np.trapz
        return fn(x,t,axis=0)/np.ptp(t)
    def freq(sig):
        k=np.where((sig[:-1]<vdd/2)&(sig[1:]>=vdd/2))[0]
        edges=t[k]+(vdd/2-sig[k])*np.diff(t)[k]/np.diff(sig)[k]
        return (len(edges)-1)/np.ptp(edges)/1e6 if len(edges)>1 else 0.
    frequencies=np.array([freq(s) for s in signals.T])
    # Duty measured over complete rising-edge periods only.
    duties=[]
    for sig in signals.T:
        cross=np.flatnonzero((sig[:-1]-vdd/2)*(sig[1:]-vdd/2)<0)
        times=t[cross]+(vdd/2-sig[cross])*np.diff(t)[cross]/np.diff(sig)[cross]
        if len(times)>3:
            if sig[cross[0]]>vdd/2:
                times=times[1:]
            periods=(len(times)-1)//2
            if periods:
                duties.append(np.sum(times[1:2*periods:2]-times[:2*periods:2])/(times[2*periods]-times[0]))
    internal=data[:,37:].reshape(len(t),30,2)
    differential=np.ptp(internal[:,:,0]-internal[:,:,1],axis=0).min()
    rp,rn,sp,sn,vb,idd=avg(data[:,31:37])
    return (*c,cap_side,mid_side,frequencies[0],frequencies[15],min(frequencies),max(frequencies),
            np.max(np.min(signals,axis=0)),np.min(np.max(signals,axis=0)),min(duties,default=0),max(duties,default=0),
            rp,rn,vdd-sp,vdd-sn,vb,-1e6*idd,differential)

HEADER="corner temp_C vdd_V bias diff_V cm_V ramp_us settle_us ring_cap_side_um mid_cap_side_um fp_MHz fn_MHz fmin30_MHz fmax30_MHz worst_lo_V worst_hi_V duty_min duty_max rp_V rn_V tailp_vsd tailn_vsd vb_V idd_uA min_internal_diff_pp_V".split()

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--corner",default="tt")
    ap.add_argument("--temp",type=int,default=27)
    ap.add_argument("--vdd",type=float,default=1.8)
    ap.add_argument("--mode",type=int,default=0)
    ap.add_argument("--vd",nargs="+",type=float,default=[0.,.001,.003,.01,.20,-.20])
    ap.add_argument("--cm",type=float,default=.75)
    ap.add_argument("--ramp",type=float,default=1)
    ap.add_argument("--settle",type=float,default=5)
    ap.add_argument("--jobs",type=int,default=3)
    a=ap.parse_args()
    cases=[(a.corner,a.temp,a.vdd,a.mode,vd,a.cm,a.ramp,a.settle) for vd in a.vd]
    with a.out.open("w",newline="") as out, ThreadPoolExecutor(a.jobs) as pool:
        writer=csv.writer(out)
        writer.writerow(HEADER)
        out.flush()
        for row in pool.map(run,cases):
            writer.writerow(row)
            out.flush()
