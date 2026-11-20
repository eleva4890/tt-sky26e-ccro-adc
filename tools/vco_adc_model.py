#!/usr/bin/env python3
"""Behavioral model of the 15-stage pseudo-differential VCO ADC (01_SPEC v3).

Purpose (04_VERIFICATION_EVAL v3, A5): combine the pieces that ngspice cannot
simulate end-to-end - quantization, VCO phase noise, current noise, V-to-f
nonlinearity, P/N mismatch - and predict SNDR at the SPI output.

Model per ring (side s = p: +1, n: -1)
  x_s   = s * m * u(t)                    normalized current deviation (u = input / FS)
  g(x)  = x + c2*x^2 + c3*x^3             single-ended f-I curve from A0/A4 (normalized)
  f_s   = f0*(1 + s*df0/2) * (1 + (1 + s*eps/2) * g(x_s)) + white FM noise
  phase counted in transitions (30 per period); d_s[n] = floor(phi[n]) - floor(phi[n-1])
  (identical to XOR + popcount of 15 taps while d_s <= 15)
Digital: d_diff = d_p - d_n -> 21-bit wrapping Sinc^2 CIC -> slice
  OSR=128: comb2[18:3], OSR=256: comb2[20:5]   (+-30720 at d_diff = +-15)

White FM from period jitter: S_f = 2 * f0^3 * sigma_T^2  [Hz^2/Hz, one-sided]
Current noise per side (differential part, A^2/Hz) maps to S_f = (f0 * m_per_amp)^2 * S_i,
pass it directly with --sf-extra.

Examples
  python3 vco_adc_model.py --selftest
  python3 vco_adc_model.py                                  # ideal quantizer, FS input
  python3 vco_adc_model.py --sigma-t 92e-12                 # + phase noise (FoM ~ -155 dBc/Hz)
  python3 vco_adc_model.py --c3 -0.0275 --c2 0.1 --eps 0.02 # + nonlinearity / mismatch
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_sndr import analyze, report  # noqa: E402

N_TRANS = 30          # transitions per period (15 stages)
CIC_BITS = 21
SHIFT = {128: 3, 256: 5}


def cic2_slice(d_diff, osr):
    mod = 1 << CIC_BITS
    d = d_diff.astype(np.int64)
    i1 = np.cumsum(d) % mod
    i2 = np.cumsum(i1) % mod
    y = i2[osr - 1::osr]
    c1 = np.diff(y) % mod
    c2 = np.diff(c1) % mod
    c2 = np.where(c2 >= mod // 2, c2 - mod, c2)       # 21-bit two's complement
    out = c2 >> SHIFT[osr]                            # floor = bit slice
    assert out.min() >= -32768 and out.max() <= 32767
    return out


def simulate(fs=20e6, f0=5e6, m=0.34, osr=128, n_out=16384, fin=None, amp=1.0,
             c2=0.0, c3=0.0, eps=0.0, df0=0.0, sigma_t=0.0, sf_extra=0.0, seed=1):
    rng = np.random.default_rng(seed)
    n = (n_out + 4) * osr
    if fin is None:  # ~10 kHz, deliberately non-coherent
        fin = 10e3 * (1 + 1 / 977)
    t = np.arange(n) / fs
    u = amp * np.sin(2 * np.pi * fin * t)
    s_f = 2.0 * f0**3 * sigma_t**2 + sf_extra
    f_std = np.sqrt(s_f * fs / 2.0)
    d = {}
    for side in (+1, -1):
        x = side * m * u
        g = x + c2 * x**2 + c3 * x**3
        f = f0 * (1 + side * df0 / 2) * (1 + (1 + side * eps / 2) * g)
        if f_std > 0:
            f = f + rng.normal(0.0, f_std, n)
        phi = rng.uniform(0, N_TRANS) + np.cumsum(N_TRANS * f / fs)
        d[side] = np.diff(np.floor(phi), prepend=np.floor(phi[0])).astype(np.int64)
        d[side][0] = d[side][1]
    dmax = max(d[+1].max(), d[-1].max())
    out = cic2_slice(d[+1] - d[-1], osr)
    return out, dmax


def selftest():
    for osr in (128, 256):
        for v in (15, -15):
            out = cic2_slice(np.full(osr * 8, v), osr)
            assert np.all(out[2:] == 2048 * v), (osr, v, out[:6])
    print("selftest OK: d_diff=+-15 -> +-30720 for OSR 128/256 (21-bit wrap, bit slice)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fs", type=float, default=20e6)
    ap.add_argument("--f0", type=float, default=5e6)
    ap.add_argument("--m", type=float, default=0.34, help="modulation depth at FS (df/f0)")
    ap.add_argument("--osr", type=int, default=128, choices=(128, 256))
    ap.add_argument("--n-out", type=int, default=16384)
    ap.add_argument("--amp", type=float, default=1.0, help="input amplitude relative to FS")
    ap.add_argument("--c2", type=float, default=0.0)
    ap.add_argument("--c3", type=float, default=0.0)
    ap.add_argument("--eps", type=float, default=0.0, help="P/N gain mismatch")
    ap.add_argument("--df0", type=float, default=0.0, help="P/N f0 mismatch")
    ap.add_argument("--sigma-t", type=float, default=0.0, help="period jitter per ring [s rms]")
    ap.add_argument("--sf-extra", type=float, default=0.0, help="extra white FM per ring [Hz^2/Hz]")
    ap.add_argument("--save", help="save output samples to .npy")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    out, dmax = simulate(a.fs, a.f0, a.m, a.osr, a.n_out, None, a.amp,
                         a.c2, a.c3, a.eps, a.df0, a.sigma_t, a.sf_extra)
    print(f"max d per ring : {dmax} (WRAP_ERR at >= 14)")
    report(analyze(out, a.fs / a.osr))
    if a.save:
        np.save(a.save, out)


if __name__ == "__main__":
    main()
