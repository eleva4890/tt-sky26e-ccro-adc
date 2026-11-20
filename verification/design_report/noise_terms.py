"""Decompose the same seed-27 output into additive, aligned code-domain waveforms."""
import csv
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
bundle = (HERE.parent/"baseline/front_noise.csv").is_file()
ROOT = HERE.parent if bundle else HERE.parents[1]
BASE = ROOT/("baseline" if bundle else "results/audited")
OUT = ROOT if bundle else ROOT/"results/design_report"
sys.path.insert(0,str(HERE if bundle else ROOT/"tools"))
from analyze_sndr import blackman_harris4
from vco_adc_model import cic2_slice

def linear_cic(steps):
    # Evaluate twice-accumulated block differences without a long floating-point accumulator.
    blocks = steps[:len(steps)//128*128].reshape(-1,128)
    slope = np.arange(128)
    return ((blocks @ (128-slope))[2:] + (blocks @ slope)[1:-1])/8

def main():
    fs, rate = 20e6, 128
    vin_pk = .2*10**(-1/20)
    data = np.genfromtxt(BASE/"final_tt.csv",names=True,delimiter=",")
    row = next(r for r in csv.DictReader((BASE/"final_noise_budget.csv").open())
               if int(r["seed"])==27 and float(r["assumed_FoM_dBc_Hz"])==-155)
    sigma = float(row["assumed_sigma_T_ps"])*1e-12
    f0 = (data["fp_MHz"][5]+data["fn_MHz"][5])*5e5
    n = 32768*rate
    tone = vin_pk*np.sin(2*np.pi*10010*(np.arange(n)/fs))
    asd = np.loadtxt(BASE/"front_noise.csv",skiprows=1,delimiter=",")
    rng = np.random.default_rng(27)
    raw = np.fft.rfft(rng.normal(size=n))
    raw *= np.interp(np.fft.rfftfreq(n,1/fs),asd[:,0],asd[:,2])*np.sqrt(fs/2)
    raw[0] = 0
    vin = tone + np.fft.irfft(raw,n=n)
    sig = np.zeros(n); front = np.zeros(n); jit = np.zeros(n)
    counts = []
    for name,sgn in (("fp_MHz",1),("fn_MHz",-1)):
        fit = np.polynomial.Chebyshev.fit(data["diff_V"],data[name]*1e6,5)
        nominal, noisy = fit(tone), fit(vin)
        jitter = rng.normal(0,np.sqrt(fs*f0**3)*sigma,size=n)
        phase = 30*np.cumsum(noisy+jitter)/fs+rng.uniform(0,1)
        counts.append(np.diff(np.floor(phase)).astype(np.int16))
        sig += sgn*nominal; front += sgn*(noisy-nominal); jit += sgn*jitter
    actual = cic2_slice(counts[0]-counts[1],rate)
    saved = np.loadtxt(OUT/"spectra/A5_codes.csv",skiprows=1,dtype=int)
    assert np.array_equal(actual,saved)
    signal, front, jitter = [linear_cic(30*x[1:]/fs) for x in (sig,front,jit)]
    quant = actual - (signal + front + jitter)
    terms = dict(front=front,jitter=jitter,quant=quant,transfer=signal,total=actual)
    def transform(x):
        y=x[4:].astype(float)
        return np.fft.rfft((y-y.mean())*blackman_harris4(len(y)))
    obs = abs(transform(actual))**2
    k=int(np.argmax(obs[6:])+6)
    tone_power=sum(obs[k-5:k+6])
    mask=np.ones(len(obs),dtype=bool); mask[:6]=False; mask[k-5:k+6]=False
    powers={key:float(sum(abs(transform(y)[mask])**2)/tone_power) for key,y in terms.items()}
    powers["cross"]=powers["total"]-sum(powers[k] for k in ("front","jitter","quant","transfer"))
    result={k:dict(percent=100*v/powers["total"],
                   input_uVrms=np.sqrt(v)*vin_pk/np.sqrt(2)*1e6 if v>=0 else None)
            for k,v in powers.items()}
    result["sndr_db"]=float(-10*np.log10(powers["total"]))
    assert abs(result["sndr_db"]-62.17395)<.001
    path=(OUT/"bench" if bundle else OUT)/"noise_terms.json"
    path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
