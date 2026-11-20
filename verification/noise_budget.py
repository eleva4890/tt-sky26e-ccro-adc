"""Conditional ADC noise budget. Jitter is a FoM assumption, not a device measurement."""
import csv
import argparse
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from vco_adc_model import cic2_slice
from analyze_sndr import analyze

def main(transfer="tt.csv",output="conditional_budget.csv"):
    dest=ROOT/"results/audited"
    with (dest/transfer).open() as f:
        curves=list(csv.DictReader(f))
    x=np.array([float(r["diff_V"]) for r in curves])
    if len(x)!=11: raise ValueError("Expected complete coupled DC curve")
    idx=np.argmin(abs(x))
    f0_hz=(float(curves[idx]["fp_MHz"])+float(curves[idx]["fn_MHz"]))*5e5
    rail=float(curves[idx]["rp_V"])
    with (dest/"a0.csv").open() as f:
        current=[r for r in csv.DictReader(f) if r["corner"]=="tt" and float(r["temp_C"])==27]
    ima=np.interp(rail,[float(r["rail_V"]) for r in current],[float(r["current_uA"]) for r in current])
    power_mw=rail*ima*.001
    asd=np.loadtxt(dest/"front_noise.csv",skiprows=1,delimiter=",")
    fs=20e6
    rate=128
    n=32768*rate
    t=np.arange(n)/fs
    tone=.2*10**(-1/20)*np.sin(2*np.pi*10010*t)
    frequency=np.fft.rfftfreq(n,1/fs)
    freq_noise=np.interp(frequency,asd[:,0],asd[:,2])
    with (dest/output).open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["assumed_FoM_dBc_Hz","assumed_sigma_T_ps","estimated_ring_power_uW","seed","fs_Hz","osr","input_dBFS_analog","SNDR_dB","max_transitions","HD3_dBc"])
        for fom in (-150,-155,-160):
            sigma=np.sqrt(10**(fom/10)/(power_mw*f0_hz))
            for seed in (26,27,28):
                rng=np.random.default_rng(seed)
                spec=np.fft.rfft(rng.normal(size=n))
                spec*=freq_noise*np.sqrt(fs/2)
                spec[0]=0
                voltage=tone+np.fft.irfft(spec,n=n)
                counts=[]
                for name in ("fp_MHz","fn_MHz"):
                    ffit=np.polynomial.Chebyshev.fit(x,[float(r[name])*1e6 for r in curves],5)
                    freq=ffit(voltage)
                    freq+=rng.normal(0,np.sqrt(fs*f0_hz**3)*sigma,size=n)
                    phase=30*np.cumsum(freq)/fs+rng.uniform(0,1)
                    counts.append(np.diff(np.floor(phase)).astype(np.int16))
                max_count=max(int(c.max()) for c in counts)
                if max_count>=14: raise ValueError("Transition aliasing")
                codes=cic2_slice(counts[0]-counts[1],rate)
                metric=analyze(codes,fs/rate)
                w.writerow([fom,sigma*1e12,power_mw*1e3,seed,fs,rate,-1,
                            metric["sndr_db"],max_count,metric["hd_dbc"][3]])
                f.flush()
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--transfer", default="tt.csv")
    parser.add_argument("--output", default="conditional_budget.csv")
    main(**vars(parser.parse_args()))
