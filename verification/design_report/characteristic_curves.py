"""Central A5 model sweeps, DC code distribution and sampled transfer residuals."""
import csv
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
BUNDLE = (HERE.parent/"baseline/final_tt.csv").is_file()
ROOT = HERE.parent if BUNDLE else HERE.parents[1]
AUDIT = ROOT/("baseline" if BUNDLE else "results/audited")
OUT = ROOT if BUNDLE else ROOT/"results/design_report"
DATA, FIG = OUT/"characterization", OUT/"figures"
sys.path.insert(0,str(HERE if BUNDLE else ROOT/"tools"))
from analyze_sndr import analyze
from vco_adc_model import cic2_slice

FS, R, N = 20_000_000, 128, 32768*128
TEAL, BLUE, RUST = "#00776d", "#37668a", "#b04a2d"


def read(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def save(name, rows):
    with (DATA/name).open("w",newline="") as f:
        writer=csv.DictWriter(f,rows[0])
        writer.writeheader()
        writer.writerows(rows)


def plot(figure, name):
    for ax in figure.axes:
        ax.spines[["right","top"]].set_visible(False)
        ax.grid(axis="y",alpha=.2)
    figure.savefig(FIG/(name+".png"),dpi=200)
    plt.close(figure)


def static():
    curve=read(AUDIT/"final_tt.csv")
    x=np.array([float(r["diff_V"]) for r in curve])
    fp,fn=[np.array([float(r[k])*1e6 for r in curve]) for k in ("fp_MHz","fn_MHz")]
    gain=(fp[-1]-fn[-1]-fp[0]+fn[0])/(x[-1]-x[0])
    y=2048*30*(fp-fn)/FS
    ep=(y[-1]-y[0])/(x[-1]-x[0])
    fits=[np.array([ep,y[0]-ep*x[0]]),np.polyfit(x,y,1)]
    residual=[y-np.polyval(f,x) for f in fits]
    save("static_residual.csv",[dict(diff_V=v,ideal_slice_code=c,endpoint_codes=e,best_fit_codes=b)
         for v,c,e,b in zip(x,y,*residual)])
    fig,(a,b)=plt.subplots(1,2,figsize=(7.2,2.7),layout="constrained")
    for values,label,color in zip(residual,["Endpoint","Least squares"],[TEAL,RUST]):
        a.plot(x*1e3,values,"o-",ms=3,label=label,color=color)
    a.set(xlabel="Differential input (mV)",ylabel="Residual (output codes)")
    a.legend(fontsize=8)
    small=read(AUDIT/"final_loaded_small.csv")
    v=np.array([float(r["diff_V"]) for r in small])
    df=np.array([float(r["fp_MHz"])-float(r["fn_MHz"]) for r in small])*1e6
    b.plot(v*1e3,(df-gain*v)/1e3,"o-",ms=4,color=BLUE)
    b.set(xlabel="Differential input (mV)",ylabel="Loaded residual (kHz)")
    a.set_title("11-point macro PEX",fontsize=10); b.set_title("7 points with routed tap loads",fontsize=10)
    plot(fig,"char_static")
    t4=ROOT/("measurements" if BUNDLE else "results/torture")/"T4_step.json"
    windows=json.loads(t4.read_text())["windows"]
    ws=windows[4:6]
    same_load_diff=lambda w: (w["fp_MHz"]-w["fn_MHz"])*1e6
    t4_gain=(same_load_diff(windows[1])-same_load_diff(windows[3]))/.20
    delta=[(w["fp_MHz"]-w["fn_MHz"])*1e6 for w in ws]
    cmgain=(delta[1]-delta[0])/.30
    metrics=dict(span_codes=float(np.ptp(y)),lsb_uV=1e6/ep,endpoint_codes=max(abs(residual[0])),
                 bestfit_codes=max(abs(residual[1])),diff_gain_Hz_V=gain,
                 t4_gain_Hz_V=t4_gain,cmgain_Hz_V=cmgain,cmrr_conditional_dB=20*np.log10(abs(t4_gain/cmgain)))
    return x,fp,fn,metrics


def model(x,fp,fn,metrics):
    budget=next(r for r in read(AUDIT/"final_noise_budget.csv")
                if float(r["assumed_FoM_dBc_Hz"])==-155 and int(r["seed"])==27)
    rng=np.random.default_rng(27)
    t=np.arange(N)/FS
    asd=np.loadtxt(AUDIT/"front_noise.csv",delimiter=",",skiprows=1)
    spec=np.fft.rfft(rng.normal(size=N))
    spec*=np.interp(np.fft.rfftfreq(N,1/FS),asd[:,0],asd[:,2])*np.sqrt(FS/2)
    spec[0]=0
    noise=np.fft.irfft(spec,n=N)
    del spec
    f0=((fp+fn)/2)[np.argmin(abs(x))]
    jitter_rms=np.sqrt(FS*f0**3)*float(budget["assumed_sigma_T_ps"])*1e-12
    rings=[(np.polynomial.Chebyshev.fit(x,f,5),rng.normal(0,jitter_rms,size=N),rng.uniform())
           for f in (fp,fn)]

    def codes(vin):
        counts=[]
        for fit,jitter,phase0 in rings:
            phase=30*np.cumsum(fit(vin+noise)+jitter)/FS+phase0
            counts.append(np.diff(np.floor(phase)).astype(np.int16))
        return cic2_slice(counts[0]-counts[1],R)

    cache={}
    def tone(db,hz):
        if (db,hz) not in cache:
            a=analyze(codes(.2*10**(db/20)*np.sin(2*np.pi*hz*t)),FS/R)
            assert abs(a["f_sig_hz"]-hz)< (FS/R)/a["n"]
            cache[db,hz]=dict(analog_dBFS=db,input_Hz=hz,n_fft=a["n"],amplitude_code=a["amp_code"],
                SNR_dB=a["snr_db"],SNDR_dB=a["sndr_db"],SFDR_dB=a["sfdr_db"],
                HD2_dBc=a["hd_dbc"][2],HD3_dBc=a["hd_dbc"][3])
        return cache[db,hz]
    amps=[tone(db,10010) for db in (-60,-50,-40,-30,-20,-12,-9,-6,-3,-1,0)]
    freqs=[tone(-1,hz) for hz in (1000,5000,10010,20000,30000,40000,50000)]
    assert abs(tone(-1,10010)["SNDR_dB"]-float(budget["SNDR_dB"]))<.01
    save("model_amplitude.csv",amps); save("model_frequency.csv",freqs)
    metrics["sampled_peak"]=max(amps,key=lambda r:r["SNDR_dB"])
    for name,rows,key,fields in [("amplitude",amps,"analog_dBFS",("SNR_dB","SNDR_dB","SFDR_dB")),
                                ("frequency",freqs,"input_Hz",("SNDR_dB","HD2_dBc","HD3_dBc"))]:
        fig,axes=plt.subplots(1,2 if name=="frequency" else 1,figsize=(7.2,2.55),layout="constrained")
        axes=np.atleast_1d(axes)
        for i,field in enumerate(fields):
            axis=axes[-1] if name=="frequency" and i else axes[0]
            axis.plot([r[key]/(1000 if name=="frequency" else 1) for r in rows],
                      [r[field] for r in rows],"o-",label=field.split("_")[0],ms=4,color=(TEAL,RUST,BLUE)[i])
        for ax in axes:
            ax.set_xlabel("Input frequency (kHz)" if name=="frequency" else "Analog input amplitude (dBFS, 0 dB = 200 mV peak)")
            ax.legend(fontsize=8)
        if name=="amplitude":
            threshold=20*np.log10(.001/.2)
            axes[0].axvspan(-60,threshold,color="#d7b58a",alpha=.24,zorder=0)
            axes[0].text(-59.7,.96,"≤1 mV peak\nLock omitted",transform=axes[0].get_xaxis_transform(),
                         va="top",fontsize=8,color="#754a20")
            axes[0].legend(loc="lower right",ncols=3,fontsize=8)
        axes[0].set_ylabel("dB"); axes[-1].set_ylabel("dBc" if name=="frequency" else "dB")
        plot(fig,"char_"+name)
    dc=codes(.05)[4:]
    bins,counts=np.unique(dc,return_counts=True)
    save("dc_histogram.csv",[dict(code=int(b),count=int(c)) for b,c in zip(bins,counts)])
    s=dc.std(); span=metrics["span_codes"]
    metrics["dc"]=dict(input_V=.05,n=len(dc),mean=dc.mean(),rms_codes=s,rms_uV=s*metrics["lsb_uV"],
        minimum=int(dc.min()),maximum=int(dc.max()),noise_free_6p6_bits=np.log2(span/(6.6*s)),
        observed_pp_codes=int(np.ptp(dc)),range_dB=20*np.log10(span/(2*np.sqrt(2)*s)))
    fig,ax=plt.subplots(figsize=(7.2,2.35),layout="constrained")
    ax.bar(bins,counts,color=TEAL,width=.83)
    ax.set(xlabel="Signed SPI output code (model)",ylabel="Occurrences")
    plot(fig,"char_histogram")


def main():
    DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    x,fp,fn,metrics=static()
    model(x,fp,fn,metrics)
    (DATA/"model_summary.json").write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps(metrics,indent=2))

if __name__=="__main__":
    main()
