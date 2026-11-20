#!/usr/bin/env python3
"""SNDR / SNR / SFDR / ENOB analyzer for the TT VCO-ADC output (04_VERIFICATION_EVAL v3, Step 3).

Input formats
  *.bin : raw 32-bit little-endian words saved by tt_adc_pio_rx.py
          (each word = two 16-bit frames, earlier frame in bits [31:16])
  *.npy : 1-D array of signed samples (e.g. from vco_adc_model.py)

The AD2 signal source and the RP2040-generated ADC clock are independent, so the
capture is non-coherent; a 4-term Blackman-Harris window (sidelobes ~ -92 dB) is
applied. The whole output Nyquist band (0 .. fs_out/2) is treated as the signal band.

Usage
  python3 analyze_sndr.py adc_raw.bin --fs-out 156250
  python3 analyze_sndr.py samples.npy --fs-out 156250 --plot spectrum.png
"""
import argparse

import numpy as np

FULL_SCALE = 32768.0  # 16-bit signed full scale used for dBFS
DIGITAL_MAX = 30720.0  # code for d_diff = +-15 (01_SPEC v3 sec.4)


def load_samples(path):
    if path.endswith(".npy"):
        return np.load(path).astype(np.float64)
    words = np.fromfile(path, dtype="<u4")
    s = np.empty(2 * len(words), dtype=np.int16)
    s[0::2] = (words >> 16).astype(np.uint16).view(np.int16)
    s[1::2] = (words & 0xFFFF).astype(np.uint16).view(np.int16)
    return s.astype(np.float64)


def blackman_harris4(n):
    a0, a1, a2, a3 = 0.35875, 0.48829, 0.14128, 0.01168
    x = 2.0 * np.pi * np.arange(n) / n  # periodic (DFT-even) window
    return a0 - a1 * np.cos(x) + a2 * np.cos(2 * x) - a3 * np.cos(3 * x)


def _fold(k, n):
    """Fold a bin index of a real signal into 0 .. n/2."""
    k = k % n
    return n - k if k > n // 2 else k


def analyze(x, fs_out, nharm=5, lobe=5, dc_bins=6, skip=4):
    """Return a dict of metrics. `skip` drops CIC start-up samples."""
    x = np.asarray(x, dtype=np.float64)[skip:]
    n = len(x)
    w = blackman_harris4(n)
    spec = np.abs(np.fft.rfft((x - x.mean()) * w)) ** 2
    nb = len(spec)

    used = np.zeros(nb, dtype=bool)
    used[:dc_bins] = True  # DC / 1/f region excluded from every figure

    search = spec.copy()
    search[:dc_bins] = 0.0
    k0 = int(np.argmax(search))

    def group(kc):
        lo, hi = max(kc - lobe, 0), min(kc + lobe + 1, nb)
        return lo, hi

    lo, hi = group(k0)
    p_sig = spec[lo:hi].sum()
    used[lo:hi] = True

    harm = {}
    for h in range(2, nharm + 1):
        kh = _fold(h * k0, n)
        lo, hi = group(kh)
        mask = ~used[lo:hi]
        harm[h] = spec[lo:hi][mask].sum()
        used[lo:hi] = True

    noise_bins = ~used
    p_noise_meas = spec[noise_bins].sum()
    # extrapolate noise density into excluded (signal/harmonic, not DC) bins
    n_band = nb - dc_bins
    p_noise = p_noise_meas * n_band / max(noise_bins.sum(), 1)
    p_harm = sum(harm.values())
    p_nd_all = spec[dc_bins:].sum() - p_sig  # everything in band except the tone

    # SFDR: largest (2*lobe+1)-bin group outside the signal lobe
    rest = spec.copy()
    rest[:dc_bins] = 0.0
    lo, hi = group(k0)
    rest[lo:hi] = 0.0
    spur = np.convolve(rest, np.ones(2 * lobe + 1), mode="same").max()

    amp = np.sqrt(4.0 * p_sig / (n * np.sum(w**2)))
    db = lambda r: 10.0 * np.log10(r)
    sndr = db(p_sig / p_nd_all)
    return {
        "n": n,
        "f_sig_hz": k0 * fs_out / n,
        "amp_code": amp,
        "amp_dbfs": 20.0 * np.log10(amp / FULL_SCALE),
        "amp_rel_digital_max": amp / DIGITAL_MAX,
        "sndr_db": sndr,
        "snr_db": db(p_sig / p_noise),
        "sfdr_db": db(p_sig / spur),
        "hd_dbc": {h: (db(p / p_sig) if p > 0 else -np.inf) for h, p in harm.items()},
        "enob": (sndr - 1.76) / 6.02,
        "_spec": spec,
    }


def report(m):
    print(f"samples        : {m['n']}")
    print(f"tone           : {m['f_sig_hz']:.1f} Hz, {m['amp_code']:.0f} code "
          f"({m['amp_dbfs']:.2f} dBFS16, {m['amp_rel_digital_max']*100:.1f}% of +-30720)")
    print(f"SNDR / SNR     : {m['sndr_db']:.2f} dB / {m['snr_db']:.2f} dB")
    print(f"SFDR           : {m['sfdr_db']:.2f} dB")
    print("HD2..HD5 (dBc) : " + ", ".join(f"{v:.1f}" for v in m["hd_dbc"].values()))
    print(f"ENOB           : {m['enob']:.2f} bit")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--fs-out", type=float, required=True, help="output sample rate = fs / OSR [Hz]")
    ap.add_argument("--skip", type=int, default=4, help="start-up samples to drop")
    ap.add_argument("--plot", help="save spectrum plot to this PNG (needs matplotlib)")
    a = ap.parse_args()
    x = load_samples(a.path)
    m = analyze(x, a.fs_out, skip=a.skip)
    report(m)
    if a.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        spec = m["_spec"]
        f = np.arange(len(spec)) * a.fs_out / m["n"]
        ref = spec.max()
        plt.figure(figsize=(8, 4))
        plt.semilogx(f[1:], 10 * np.log10(spec[1:] / ref + 1e-30), lw=0.7)
        plt.ylim(-140, 5)
        plt.xlabel("Frequency [Hz]")
        plt.ylabel("dBc")
        plt.title(f"SNDR {m['sndr_db']:.1f} dB, SFDR {m['sfdr_db']:.1f} dB")
        plt.grid(True, which="both", alpha=0.3)
        plt.tight_layout()
        plt.savefig(a.plot, dpi=130)


if __name__ == "__main__":
    main()
