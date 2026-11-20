"""Current-driven ring characterization with the physical CVSL input loads."""
import argparse
import csv
import itertools
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL = Path(os.environ["PDK_ROOT"]) / "sky130A/libs.tech/ngspice/sky130.lib.spice"
RING = Path(os.environ.get("ADC_RING", ROOT / "analog/ccro.spice")).resolve()
STEP_NS = float(os.environ.get("ADC_STEP_NS", "1"))


def run(point, duration_us=3):
    corner, temp, current = point
    taps = " ".join(f"t{i}" for i in range(15))
    loads = "\n".join(f"Ct{i} t{i} 0 5f" for i in range(15))
    # Start in the differential mode to characterize f-I. Autonomous startup is A1.
    seed = " ".join(f"v(xr.a{i})={.67*(i%2)} v(xr.b{i})={.67*(1-i%2)}" for i in range(15))
    deck = f"""A0 15-stage CCRO, nominal ring supply capacitance
.lib "{MODEL}" {corner}
.include "{RING}"
.option scale=1u method=gear reltol=.0003 klu
.temp {temp}
Vdd vdd 0 1.8
Iring 0 rail {current:.9f}u
Xcap rail 0 sky130_fd_pr__cap_mim_m3_1 w=21.8 l=21.8
Xr rail vdd 0 {taps} ring
{loads}
.ic v(rail)=.67 {seed}
.control
set num_threads=1
set wr_singlescale
set numdgt=12
save v(rail) v(xr.a0) v(xr.b0) v(t0)
tran {STEP_NS}n {duration_us}u 1u {STEP_NS}n uic
wrdata waves v(rail) v(xr.a0) v(xr.b0) v(t0)
quit
.endc
.end
"""
    with tempfile.TemporaryDirectory() as work:
        path = Path(work)
        (path / ".spiceinit").write_text((MODEL.parent / "spinit").read_text() + "\nset num_threads=1\n")
        (path / "test.cir").write_text(deck)
        proc = subprocess.run(["ngspice", "-b", "test.cir"], cwd=work, capture_output=True, text=True)
        if not (path / "waves").exists():
            raise RuntimeError((proc.stderr[:1800], proc.stdout[-1000:]))
        t, rail, a, b, tap = np.loadtxt(path / "waves").T
    if t[-1] < (duration_us-.001)*1e-6:
        raise RuntimeError(f"Incomplete transient {point}")
    vdiff = a - b
    idx = np.flatnonzero((vdiff[:-1] < 0) & (vdiff[1:] >= 0))
    edges = t[idx] - vdiff[idx] * np.diff(t)[idx] / np.diff(vdiff)[idx]
    edges = edges[edges > 1.5e-6]
    if len(edges) < 3 or np.ptp(vdiff) < .3:
        if duration_us==3: return run(point, 9)
        raise ValueError(f"Differential oscillation missing at {point}")
    period = np.diff(edges)
    idx = (t >= edges[0]) & (t <= edges[-1])
    mean_rail = np.trapezoid(rail[idx], t[idx]) / np.ptp(t[idx]) if hasattr(np, "trapezoid") else np.trapz(rail[idx], t[idx]) / np.ptp(t[idx])
    return (*point, 1e-6 / np.mean(period), mean_rail, len(period),
            np.ptp(period) / np.mean(period), np.min(tap[idx]), np.max(tap[idx]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corners", nargs="+", default=["tt", "ss", "ff"])
    ap.add_argument("--temps", nargs="+", type=int, default=[-20, 27, 85])
    ap.add_argument("--points", type=int, default=21)
    ap.add_argument("--currents", nargs="+", type=float, help="Explicit ring currents in microamperes")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--resume", action="store_true", help="Continue the same model and sweep from the saved rows")
    args = ap.parse_args()
    currents = args.currents or (np.linspace(6.5, 13.5, args.points) if args.points > 1 else [10.])
    existing=set()
    if args.resume and args.out.exists():
        with args.out.open() as saved:
            for r in csv.DictReader(saved):
                existing.add((r["corner"],float(r["temp_C"]),round(float(r["current_uA"]),6)))
    with args.out.open("a" if existing else "w", newline="") as out, ThreadPoolExecutor(args.jobs) as pool:
        writer = csv.writer(out)
        if not existing:
            writer.writerow(["corner","temp_C","current_uA","f_MHz","rail_V","periods","period_pp_fraction","tap_lo_V","tap_hi_V"])
        cases=(p for p in itertools.product(args.corners,args.temps,currents) if (p[0],p[1],round(p[2],6)) not in existing)
        for row in pool.map(run, cases):
            writer.writerow(row)
            out.flush()


if __name__ == "__main__":
    main()
