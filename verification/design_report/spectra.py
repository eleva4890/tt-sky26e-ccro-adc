"""Recompute the datasheet plots from archived SPI pins and the published A5 noise budget."""
import csv
import gzip
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
IN_BUNDLE = (HERE.parent / "waveforms/index.json").is_file()
ROOT = HERE.parent if IN_BUNDLE else HERE.parents[1]
sys.path.insert(0, str(HERE if IN_BUNDLE else ROOT / "tools"))
from analyze_sndr import analyze
from vco_adc_model import cic2_slice

OUT = ROOT if IN_BUNDLE else ROOT / "results/design_report"
FIG = OUT / "figures"
DATA = OUT / "spectra"
AUDIT = ROOT / ("baseline" if IN_BUNDLE else "results/audited")
FS = 20_000_000
R = 128
ODR = FS / R
TEAL, RUST = "#007e74", "#c6542e"


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def gate_frames(rows, side):
    """Latch SDO on every rising SCLK during a single active-low frame."""
    frames = []
    prev_cs, prev_clk = 1, 0
    bits = []
    for row in rows:
        tick = int(row["tick"])
        cs, clk, sdo = (int(row[side + "_" + pin]) for pin in ("cs_n", "sclk", "sdo"))
        if prev_cs and not cs:
            start = tick
            bits = []
        if not cs and clk and not prev_clk:
            assert tick - start == 2 + 4 * len(bits)
            bits.append(str(sdo))
        if not prev_cs and cs:
            assert len(bits) == 16 and tick - start == 64
            word = int("".join(bits), 2)
            frames.append((start, word - 65536 if word >= 32768 else word))
        prev_cs, prev_clk = cs, clk
    assert all(b[0] - a[0] == R for a,b in zip(frames,frames[1:]))
    return frames


def style(ax):
    ax.spines[["top","right"]].set_visible(False)
    ax.grid(axis="y", alpha=.22)
    ax.set_axisbelow(True)


def gate_spectrum():
    ref = json.loads((ROOT/("measurements" if IN_BUNDLE else "results/torture")/"T3_gate.json").read_text())
    with gzip.open(OUT/"waveforms/T3_gate.csv.gz", "rt") as f:
        pins = list(csv.DictReader(f))
    freqs = np.fft.rfftfreq(16, 1/ODR)
    spectra = {}
    metrics = {}
    samples = {}
    for side in ("clean","dirty"):
        frames = gate_frames(pins, side)
        assert len(frames) == 20
        x = np.array([code for _,code in frames[-16:]])
        assert x.tolist() == ref[side + "_codes"]
        samples[side] = frames[-16:]
        power = (np.abs(np.fft.rfft(x - x.mean()))/len(x))**2
        power[1:-1] *= 2
        assert np.isclose(sum(power),np.var(x))
        residual = sum(power[k] for k in range(1,9) if k != 2)
        sndr = float(10*np.log10(power[2]/residual))
        assert abs(sndr-ref[side + "_sndr_dB"]) < 1e-7
        spur = max([1,*range(3,9)],key=lambda k:power[k])
        metrics[side] = dict(sndr=sndr, sfdr=float(10*np.log10(power[2]/power[spur])),
                             spur_hz=float(freqs[spur]), tone_rms=float(np.sqrt(power[2])),
                             residual_rms=float(np.sqrt(residual)),first=int(x[0]),second=int(x[1]))
        spectra[side] = power
    with (DATA/"T3_fft_bins.csv").open("w", newline="") as f:
        w=csv.writer(f);w.writerow(["bin","frequency_Hz","quiet_code2","injected_code2","quiet_dBc","injected_dBc"])
        for k,hz in enumerate(freqs):
            p=[spectra[s][k] for s in ("clean","dirty")]
            levels=[10*np.log10(v/spectra[s][2]) if v>0 else "-inf" for v,s in zip(p,("clean","dirty"))]
            w.writerow([k,hz,*p,*levels])
    with (DATA/"T3_fft_frames.csv").open("w", newline="") as f:
        w=csv.writer(f);w.writerow(["frame_index_1based","cs_start_tick","quiet_s16","injected_s16"])
        for i,((t,a),(u,b)) in enumerate(zip(samples["clean"],samples["dirty"]),5):
            assert t==u
            w.writerow([i,t,a,b])
    fig, ax = plt.subplots(figsize=(7.0,2.8),layout="constrained")
    for s,dx,label,color in (("clean",-1.1,"Quiet",TEAL),("dirty",1.1,"Injected",RUST)):
        with np.errstate(divide="ignore"):
            db=10*np.log10(spectra[s][1:]/spectra[s][2])
        ax.vlines(freqs[1:]/1000+dx,-108,np.maximum(db,-108),lw=2.2,color=color,alpha=.7)
        finite=np.isfinite(db)
        ax.scatter(freqs[1:][finite]/1000+dx,db[finite],s=18,color=color,label=label)
    ax.set(xlabel="Output frequency (kHz)",ylabel="Power per bin (dBc)",ylim=(-108,7),xlim=(4,83))
    ax.set_xticks(freqs[1:]/1000,labels=[f"{v/1000:.1f}" for v in freqs[1:]])
    ax.legend(loc="upper right",ncols=2);style(ax)
    fig.savefig(FIG/"spi_sndr_spectrum.png",dpi=210);plt.close(fig)

    start,code=samples["clean"][1]
    ticks=np.array([int(r["tick"])-start for r in pins])
    subset=(ticks>=-2)&(ticks<=66)
    fig,ax=plt.subplots(figsize=(7,2.1),layout="constrained")
    for k,(name,label) in enumerate((("sdo","SDO"),("sclk","SCLK"),("cs_n","CS_N"))):
        data=np.array([int(r["clean_"+name]) for r in pins])
        ax.step(ticks[subset]*.05,data[subset]*.53+k,where="post",color=TEAL,lw=1.3)
    for i,bit in enumerate(f"{code & 0xffff:016b}"):
        px=.1+.2*i
        ax.axvline(px,color="#acbabb",ls=":",lw=.6)
        ax.text(px,2.8,bit,ha="center",fontsize=9,color=RUST)
    ax.set(xlim=(-.1,3.3),ylim=(-.18,3.1),xlabel="Time after CS_N falling edge (us)")
    ax.set_yticks([.24,1.24,2.24],labels=["SDO","SCLK","CS_N"]);style(ax)
    fig.savefig(FIG/"spi_word_example.png",dpi=210);plt.close(fig)
    return metrics


def budget_spectrum():
    # Reproduce the central FoM / central seed of verification/noise_budget.py.
    row=next(r for r in read_rows(AUDIT/"final_noise_budget.csv")
             if float(r["assumed_FoM_dBc_Hz"])==-155 and int(r["seed"])==27)
    curve=read_rows(AUDIT/"final_tt.csv")
    x=np.array([float(r["diff_V"]) for r in curve])
    zero=curve[int(np.argmin(abs(x)))]
    f0=(float(zero["fp_MHz"])+float(zero["fn_MHz"]))*5e5
    n=32768*R
    t=np.arange(n)/FS
    tone=.2*10**(-1/20)*np.sin(2*np.pi*10010*t)
    asd=np.loadtxt(AUDIT/"front_noise.csv",skiprows=1,delimiter=",")
    amplitude=np.interp(np.fft.rfftfreq(n,1/FS),asd[:,0],asd[:,2])
    rng=np.random.default_rng(int(row["seed"]))
    noise=np.fft.rfft(rng.normal(size=n))
    noise*=amplitude*np.sqrt(FS/2); noise[0]=0
    vin=tone+np.fft.irfft(noise,n=n)
    sigma=float(row["assumed_sigma_T_ps"])*1e-12
    counts=[]
    for key in ("fp_MHz","fn_MHz"):
        fitted=np.polynomial.Chebyshev.fit(x,[float(r[key])*1e6 for r in curve],5)
        freq=fitted(vin)
        freq+=rng.normal(0,np.sqrt(FS*f0**3)*sigma,size=n)
        phase=30*np.cumsum(freq)/FS+rng.uniform(0,1)
        counts.append(np.diff(np.floor(phase)).astype(np.int16))
    assert max(c.max() for c in counts)==int(row["max_transitions"])
    codes=cic2_slice(counts[0]-counts[1],R)
    a=analyze(codes,ODR)
    assert abs(a["sndr_db"]-float(row["SNDR_dB"]))<.01
    assert abs(a["hd_dbc"][3]-float(row["HD3_dBc"]))<.01
    ps=a["_spec"];k0=int(round(a["f_sig_hz"]*a["n"]/ODR))
    dbc=10*np.log10(np.maximum(ps,np.finfo(float).tiny)/sum(ps[k0-5:k0+6]))
    hz=np.fft.rfftfreq(a["n"],1/ODR)
    np.savetxt(DATA/"A5_fft_bins.csv",np.column_stack((hz,dbc)),fmt="%.10g",delimiter=",",
               header="frequency_Hz,power_dBc_per_bin",comments="")
    np.savetxt(DATA/"A5_codes.csv",codes,fmt="%d",header="signed_code",comments="")
    fig,ax=plt.subplots(figsize=(7,2.8),layout="constrained")
    ax.plot(hz[6:]/1000,dbc[6:],color=TEAL,lw=.38,rasterized=True)
    for h in (1,2,3):
        kh=h*k0
        j=kh-5+int(np.argmax(dbc[kh-5:kh+6]))
        ax.annotate(["","Input","H2","H3"][h],xy=(hz[j]/1000,dbc[j]),
                    xytext=(hz[j]/1000+2, min(0,dbc[j]+15)),ha="left",fontsize=8,
                    arrowprops=dict(arrowstyle="-",lw=.7,color=RUST),color=RUST)
    ax.set(xlim=(0,ODR/2000),ylim=(-135,5),xlabel="Output frequency (kHz)",ylabel="Power per bin (dBc)")
    style(ax);fig.savefig(FIG/"budget_sndr_spectrum.png",dpi=220);plt.close(fig)
    return dict(n=a["n"],samples=len(codes),bin_hz=ODR/a["n"],tone_bin=k0,
                sndr=a["sndr_db"],snr=a["snr_db"],sfdr=a["sfdr_db"],hd3=a["hd_dbc"][3],
                amp_code=a["amp_code"],seed=int(row["seed"]),sigma_ps=float(row["assumed_sigma_T_ps"]))


def response():
    f=np.linspace(0,100e3,1500)
    fig,ax=plt.subplots(figsize=(7,2.45),layout="constrained")
    results={}
    for rate,color in ((128,TEAL),(256,RUST)):
        odr=FS/rate
        def gain(hz):
            return 40*np.log10(abs(np.sinc(hz/odr)/np.sinc(hz/FS)))
        ny=odr/2
        lo,hi=0.,ny
        for _ in range(45):
            mid=(hi+lo)/2
            if gain(mid)>-3:lo=mid
            else:hi=mid
        results[str(rate)]=dict(cutoff_hz=(hi+lo)/2,nyquist_db=gain(ny),tone_19k_db=gain(19531.25))
        mask=f<=ny
        ax.plot(f[mask]/1e3,gain(f[mask]),color=color,label=f"OSR {rate}")
        ax.scatter([ny/1000],[gain(ny)],s=24,color=color)
    ax.axhline(-3,color="#60777d",lw=.8,ls=":");ax.set(xlim=(0,80),ylim=(-8.6,.5),
        xlabel="Input frequency to CIC (kHz)",ylabel="Normalized gain (dB)")
    ax.legend();style(ax);fig.savefig(FIG/"cic_bandwidth.png",dpi=210);plt.close(fig)
    return results


if __name__=="__main__":
    DATA.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
    result=dict(gate=gate_spectrum(),model=budget_spectrum(),cic=response())
    (DATA/"summary.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print(json.dumps(result,indent=2))
