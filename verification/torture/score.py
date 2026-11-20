"""Evaluate interval, phase, converter and waveform evidence in original physical time."""
import csv, sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dynamic import analyze
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from vco_adc_model import cic2_slice
TAPS=[f"{s}{k}" for s in "pn" for k in range(15)]
def edges(t,x,up=True):
    k=np.flatnonzero((x[:-1]<0)&(x[1:]>=0)) if up else np.flatnonzero((x[:-1]>0)&(x[1:]<=0))
    return t[k]-x[k]*np.diff(t)[k]/(x[k+1]-x[k])
def mean(t,x):
    return float(np.trapezoid(x,t)/np.ptp(t))
def series(w,name):return w["v("+name+")"]
def windows(w,start,end):
    t=w["time"]*1e6
    use=(t>=start)&(t<=end)
    t=t[use]
    vg=series(w,"vg")[use]; vdd=series(w,"vdd")[use]; th=(vg+vdd)/2
    freqs=[];swing=[]
    for pin in TAPS:
        if "v("+pin+")" not in w:continue
        wave=series(w,pin)[use]
        e=edges(t,wave-th)
        freqs.append(float((len(e)-1)/np.ptp(e)) if len(e)>=3 else 0.)
        swing.append(float(np.ptp(wave-vg)))
    return dict(window_us=[start,end],fp_MHz=freqs[0],fn_MHz=freqs[len(freqs)//2],
                min_tap_MHz=min(freqs),max_tap_MHz=max(freqs),min_swing_V=min(swing),vb_V=mean(t,series(w,"xadc.vb")[use]-vg))
def phases(w):
    t=w["time"]*1e6
    vg=series(w,"vg"); half=(series(w,"vdd")+vg)/2
    return [edges(t,series(w,p)-half) for p in TAPS]
def t1(w):
    t=w["time"]*1e6; banks={}
    for bank in "pn":
        half=.5*series(w,"xadc.r"+bank)
        stage=[]; icerr=[]
        for i in range(15):
            a,b=[series(w,f"xadc.{bank}{s}{i}") for s in "ab"]
            icerr.append(max(abs(a[0]-.35),abs(b[0]-.35),abs(a[0]-b[0])))
            ea,eb=edges(t,a-half),edges(t,b-half)
            if min(len(ea),len(eb))<5:
                stage.append(dict(stage=i,pass_stage=False,edges=[len(ea),len(eb)]));continue
            nominal=float(np.median(np.diff(ea)[-4:]))
            passing=[]; deg=[]
            for left,right in zip(ea[:-1],ea[1:]):
                opposite=eb[(eb>=left)&(eb<right)]
                angle=(opposite[0]-left)/(right-left)*360 if len(opposite)==1 else -999.
                k=(t>=left)&(t<right)
                strong=np.max(a[k])>1.6*np.mean(half[k]) and np.min(a[k])<.4*np.mean(half[k]) and np.max(b[k])>1.6*np.mean(half[k]) and np.min(b[k])<.4*np.mean(half[k])
                passing.append(bool(strong and abs(angle-180)<=15 and .85*nominal<=right-left<=1.15*nominal))
                deg.append(float(angle))
            bad=np.flatnonzero(~np.array(passing))
            first=1+bad[-1] if len(bad) else 0
            valid=len(passing)-first>=2
            # End of the first two verified full periods is the conservative decision time.
            latency=float(ea[first+2]/nominal) if valid else None
            stage.append(dict(stage=i,period_us=nominal,confirmed_cycles=latency,
                              final_phase_deg=deg[-1],pass_stage=bool(valid and latency<=10)))
        banks[bank]=dict(ic_error_V=float(max(icerr)),stages=stage,success=all(s["pass_stage"] for s in stage))
    icok=max(x["ic_error_V"] for x in banks.values())<.001 and t[0]<.001
    return dict(status="INVALID_IC" if not icok else "PASS" if all(b["success"] for b in banks.values()) else "FAIL",banks=banks,
                initial_saved_us=float(t[0]),phase_tolerance_deg=15,confirmed_periods=2)
def t3(w):
    t=w["time"]*1e6; vg=series(w,"vg"); v=series(w,"vdd")
    local=v-vg;h=(vg+v)/2
    edge_list=[]
    for pin in TAPS:
        sig=series(w,pin)-h
        edge_list.append(np.sort(np.r_[edges(t,sig),edges(t,sig,False)]))
    t0,t1=28.8,131.2
    period=t1-t0
    e=[row[(row>=t0)&(row<t1)] for row in edge_list]
    freqline={}
    for freq in (.01953125,.15625,20,19.84375,20.15625):
        line=sum((1 if k<15 else -1)*np.exp(-2j*np.pi*freq*row).sum() for k,row in enumerate(e))
        freqline[str(freq)]=float(2e6*abs(line)/(30*period))
    # Phase excursion to each candidate rational lock; >1 cycle excludes continuous lock.
    u=np.arange(t0,t1,.025)
    slips={}
    for bank,group in [("p",edge_list[:15]),("n",edge_list[15:])]:
        phase=sum(np.interp(u,row,np.arange(len(row))*.5) for row in group)/15
        terms=[(f"20MHz/ {d}",20/d) for d in range(4,9)]+[(f"{n}*156.25k",n*.15625) for n in range(16,34)]
        excursions={label:float(np.ptp(phase-ratio*u)) for label,ratio in terms}
        closest=min(excursions,key=excursions.get)
        slips[bank]=dict(closest=closest,min_excursion_cycles=excursions[closest])
    waveforms=[series(w,p)-h for p in TAPS]
    align=[]
    for offset in np.arange(8)*.00625:
        grid=offset+np.arange(2688)*.05
        bits=np.column_stack([np.interp(grid,t,sig)>0 for sig in waveforms])
        change=(bits[1:]!=bits[:-1]).astype(int)
        delta=change[:,:15].sum(1)-change[:,15:].sum(1)
        codes=cic2_slice(delta,128)[-16:].astype(float)
        spec=np.abs(np.fft.rfft(codes-codes.mean()))**2
        # Real one-sided bins; the Nyquist bin has no negative-frequency partner.
        spec[-1]*=.5
        signal=spec[2]; noise=spec[1:].sum()-signal
        align.append(dict(offset_ns=float(offset*1000),codes=codes.astype(int).tolist(),
                          sndr_dB=float(10*np.log10(signal/noise))))
    return dict(status="MEASURED",codes=align[4]["codes"],sndr_dB=align[4]["sndr_dB"],sample_phase_sweep=align,
                freqline_amplitude_Hz=freqline,
                freqline_dBc={k:float(20*np.log10(a/freqline[str(.01953125)])) for k,a in freqline.items()},
                lock_excursion=slips,
                local_supply_pp_mV=float(np.ptp(local[(t>=t0)&(t<t1)])*1000),
                output_samples=16,input_Hz=19531.25)
def evaluate(case,w):
    t=w["time"]*1e6
    if case.startswith("T1"):return t1(w)
    if case=="T2_leak":
        out={}
        for s in "pn":
            crossings=edges(t,series(w,s+"0")-(series(w,"vdd")+series(w,"vg"))/2)
            if len(crossings)<2:raise ValueError("no complete leakage observation cycle")
            lo,hi=crossings[[0,-1]]
            middle=(t>lo)&(t<hi)
            grid=np.r_[lo,t[middle],hi]
            dc={};rectified={}
            for key in ("off","on"):
                names=[n for n in w if f"xadc.v{s}{key}" in n]
                if len(names)!=1:raise ValueError((names,list(w)))
                signal=np.interp(grid,t,w[names[0]])*1e9
                dc[key]=abs(mean(grid,signal))
                rectified[key]=mean(grid,np.abs(signal))
            out[s]=dict(off_nA=dc["off"],on_nA=dc["on"],off_percent_actual=100*dc["off"]/dc["on"],
                        mean_absolute_nA=rectified,complete_cycles=len(crossings)-1,units_off=39)
        return dict(status="PASS" if all(v["off_nA"]<25 and v["off_percent_actual"]<5 for v in out.values()) else "FAIL",banks=out)
    if case in ("T2_ramp","T2_reference","T2_ramp_alt","T2_reference_alt"):
        win=windows(w,10020,10100) if case.startswith("T2_ramp") else windows(w,20,100)
        return dict(status="MEASURED",tail=win)
    if case=="T2_brown":
        before,low,after=[windows(w,*bounds) for bounds in [(3,6),(8,54),(59,63)]]
        ok=(after["min_swing_V"]>1.5 and after["min_tap_MHz"]>0 and max(abs(after[k]/before[k]-1) for k in ["fp_MHz","fn_MHz","vb_V"])<.05)
        return dict(status="PASS" if ok else "FAIL",before=before,during=low,after=after)
    if case.startswith("T3"):return t3(w)
    if case=="T4_step":
        bins=[(3,4.95),(6,8.95),(10,11.95),(13,15.95),(17,20.95),(23,25.95),(28,30.95)]
        stats=[windows(w,*b) for b in bins]
        e=phases(w);lat=[]
        for start,steady in [(5.01,stats[1]),(12.01,stats[3])]:
            settle=[]
            for k,row in enumerate(e):
                q=row[(row>=start)&(row<start+3.9)]
                target=steady["fp_MHz" if k<15 else "fn_MHz"]
                good=(abs(np.diff(q)*target-1)<.05)
                lastbad=np.flatnonzero(~good)
                idx=0 if not len(lastbad) else int(lastbad[-1])+1
                settle.append(float((q[idx]-start)*target) if len(good)-idx>=2 else 999.)
            lat.append(max(settle))
        ok=max(lat)<=2 and all(s["min_tap_MHz"]>0 and s["min_swing_V"]>1.5 for s in [stats[i] for i in [1,3,4,5,6]])
        return dict(status="PASS" if ok else "FAIL",windows=stats,recovery_cycles=lat)
    if case.startswith("T4"):
        signals=np.column_stack([series(w,p) for p in TAPS])
        h,res=analyze(w["time"],signals,1.8,12e-6,50000)
        return dict(status="MEASURED",hd3_dBc=float(20*np.log10(h[2]/h[0])),phase_residual_cycles=float(res))
    if case in ("T5_hold","T5_hold_mid"):
        rows=phases(w);grid=np.linspace(18,178,3201)
        if any(len(q)<3 or q[0]>=18 or q[-1]<=178 for q in rows):raise ValueError("incomplete long phase trace")
        phi=np.array([np.interp(grid,q,np.arange(len(q))) for q in rows])
        rel=phi[:15].mean(0)-phi[15:].mean(0)
        parts=[float(np.polyfit(grid[ix],rel[ix],1)[0]*1000) for ix in (grid<=98,grid>=98)]
        return dict(status="MEASURED",window_us=[18,178],nominal_free_beat_cycles=6.9e-3*160,
                    delta_kHz=float(np.polyfit(grid,rel,1)[0]*1000),half_window_delta_kHz=parts,
                    relative_phase_span_cycles=float(np.ptp(rel)),signed_phase_advance_cycles=float(rel[-1]-rel[0]),
                    lock_indicator=bool(max(map(abs,parts))<.69 and np.ptp(rel)<.12))
    if case.startswith("T5"):
        if case.startswith("T5_tracking"):case="T5_0_0"
        stats=windows(w,13,25)
        df=(stats["fp_MHz"]-stats["fn_MHz"])*1e3
        short=[windows(w,13,19),windows(w,19,25)]
        split=[(v["fp_MHz"]-v["fn_MHz"])*1e3 for v in short]
        add=case.split("_")[-1]
        adj=-4.1989 if add=="removed" else float(add)
        grid=np.linspace(13.5,24.5,1025)
        rows=phases(w)
        if any(q[0]>grid[0] or q[-1]<grid[-1] for q in rows):raise ValueError("incomplete T5 phase coverage")
        phi=np.array([np.interp(grid,q,np.arange(len(q))) for q in rows])
        relative=phi[:15].mean(0)-phi[15:].mean(0)
        drift=float(np.polyfit(grid,relative,1)[0]*1000)
        return dict(status="MEASURED",added_fF=adj,total_direct_fF=adj+4.1989,mid_side_um=10*int(case.split("_")[1]),
                    delta_kHz=df,half_window_delta_kHz=split,reference_response_kHz=6.9,
                    phase_fit_kHz=drift,relative_phase_span_cycles=float(np.ptp(relative)),
                    lock_indicator=bool(abs(df)<.69 and max(abs(v) for v in split)<.69))
    raise ValueError(case)
