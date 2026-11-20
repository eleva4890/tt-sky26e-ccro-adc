"""Fit harmonics of continuous differential frequency from 30 CVSL phase trajectories."""
import argparse
import csv
from pathlib import Path
import tempfile
import subprocess
import numpy as np
from a0 import MODEL, ROOT
import os
import re

def analyze(t, taps, vdd, start, freq):
    # Interpolate each rising/falling-edge phase separately to cancel tap-delay ripple.
    # A complete oscillator cycle advances the phase by 1 on each of these sequences.
    grid = start + np.arange(8192) / (4096 * freq)
    phases = []
    for sig in taps.T:
        sig = sig - vdd/2
        per_tap = []
        for rising in (True, False):
            k = np.flatnonzero((sig[:-1] < 0) & (sig[1:] >= 0) if rising
                               else (sig[:-1] >= 0) & (sig[1:] < 0))
            edges = t[k] - sig[k] * np.diff(t)[k] / np.diff(sig)[k]
            if len(edges) < 5 or edges[0] >= grid[0] or edges[-1] <= grid[-1]:
                raise ValueError("Missing complete phase coverage")
            per_tap.append(np.interp(grid, edges, np.arange(len(edges))))
        phases.append(np.mean(per_tap, axis=0))
    phase = np.mean(phases[:15], axis=0) - np.mean(phases[15:], axis=0)
    # Fit the integral of the Fourier series. Scale nth phase harmonic by n*omega.
    angle = (grid - start) * (2 * np.pi * freq)
    design = [np.ones_like(angle), angle]
    for n in range(1, 10):
        design.extend([np.sin(n*angle), np.cos(n*angle)])
    coeff, *_ = np.linalg.lstsq(np.array(design).T, phase, rcond=None)
    harmonics = np.hypot(coeff[2::2], coeff[3::2]) * np.arange(1,10) * 2*np.pi*freq
    return harmonics, np.max(np.abs(phase - np.array(design).T @ coeff))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--step-ns", type=float, default=1)
    ap.add_argument("--amp", type=float, default=.2)
    ap.add_argument("--corner", default="tt")
    ap.add_argument("--vdd", type=float, default=1.8)
    ap.add_argument("--cm", type=float, default=.63)
    a = ap.parse_args()
    freq = 50_000
    start = 12e-6
    probes = " ".join(f"{s}{i}" for s in "pn" for i in range(15))
    vectors = " ".join(f"v({pin})" for pin in probes.split())
    loads = "\n".join(f"Cload{i} {pin} 0 5f" for i,pin in enumerate(probes.split()))
    if os.environ.get("ADC_INTERFACE_CAPS"):
        loads += "\n" + Path(os.environ["ADC_INTERFACE_CAPS"]).read_text()
    front=Path(os.environ.get("ADC_FRONT",ROOT/"analog/frontend_lowrail.spice")).read_text()
    dual=os.environ.get("ADC_DUAL")
    extra=""
    if dual:
        front,n=re.subn(r"^Xrp [^\n]+ ring\nXrn [^\n]+ ring$","Xdual rp rn v g "+probes+" dual_flat",front,flags=re.M)
        assert n==1
        extra=f'.include "{Path(dual).resolve()}"'
    model="adc_analog"
    if os.environ.get("ADC_FULL"):
        front=Path(os.environ["ADC_FULL"]).read_text()
        model="eleva_adc_analog"
        extra=""
    deck = f"""A4 dynamic differential sine
.lib "{MODEL}" {a.corner}
.include "{ROOT / 'analog/osc_extracted.spice'}"
.include frontend.spice
{extra}
.option scale=1u method=gear reltol=.0003 klu
.temp 27
Vdd vdd 0 pwl(0 0 1u {a.vdd})
Vtone tone 0 sin(0 {a.amp/2} {freq} 1u)
Bpos ep 0 v=v(vdd)*{a.cm/a.vdd}+v(tone)
Bneg en 0 v=v(vdd)*{a.cm/a.vdd}-v(tone)
Rp ep vinp 1.5k
Rn en vinn 1.5k
Cp vinp 0 5p
Cn vinn 0 5p
Xadc vinp vinn 0 0 vdd 0 {probes} {model}
{loads}
.control
set num_threads=1
set numdgt=12
set wr_singlescale
save {vectors}
tran {a.step_ns}n 53u 11u {a.step_ns}n
wrdata waves {vectors}
quit
.endc
.end
"""
    with tempfile.TemporaryDirectory() as work:
        p = Path(work)
        (p/"frontend.spice").write_text(front)
        (p/"sine.cir").write_text(deck)
        (p/".spiceinit").write_text((MODEL.parent/"spinit").read_text()+"\nset num_threads=1\n")
        proc = subprocess.run(["ngspice","-b","sine.cir"],cwd=p,capture_output=True,text=True)
        if not (p/"waves").exists():
            raise RuntimeError(proc.stderr[-1200:] + proc.stdout[-1200:])
        data = np.loadtxt(p/"waves")
    h, residual = analyze(data[:,0], data[:,1:], a.vdd, start, freq)
    with a.out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["corner","vdd_V","cm_V","amplitude_Vdiff","input_Hz","cycles",
                    "max_step_ns","harmonic","frequency_amplitude_Hz","relative_dBc","max_phase_fit_residual_cycles"])
        for idx, val in enumerate(h, 1):
            w.writerow([a.corner,a.vdd,a.cm,a.amp,freq,2,a.step_ns,idx,val,20*np.log10(val/h[0]),residual])

if __name__ == "__main__":
    main()
