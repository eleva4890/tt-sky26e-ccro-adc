"""Sample the routed analog tap voltages for a 0 to +100 mV input step."""
import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "verification/torture"))
from bench import CAPS, CORE, PDK, TAPS, raw

def main():
    # The step midpoint is halfway between the 34.000 and 34.050 us sample edges.
    loads = "\n".join(f"Cload{i} {node} 0 5f" for i, node in enumerate(TAPS))
    deck = f"""Loaded analog input step
.lib "{PDK / 'sky130.lib.spice'}" tt
.include "{CORE}"
.option scale=1u method=gear reltol=.0005 klu
.temp 27
Vdd v 0 pwl(0 0 1u 1.8)
Vstep d 0 pwl(0 0 34.020u 0 34.030u .1)
Ep ep cm d 0 .5
En en cm d 0 -.5
Ecm cm 0 v 0 .35
Rp ep ip 1500
Rn en in 1500
Cp ip 0 5p
Cn in 0 5p
Xadc ip in 0 0 v 0 {' '.join(TAPS)} eleva_adc_analog
{loads}
{CAPS}
.control
set num_threads=1
set filetype=binary
save v(d) {' '.join('v('+node+')' for node in TAPS)}
tran 2n 110u 0 2n
write waves.raw all
quit
.endc
.end
"""
    with tempfile.TemporaryDirectory() as dirname:
        path = Path(dirname)
        (path/"step.cir").write_text(deck)
        (path/".spiceinit").write_text((PDK/"spinit").read_text()+"\nset num_threads=1\n")
        subprocess.run(["ngspice","-b","step.cir"],cwd=path,stdout=subprocess.DEVNULL,check=True)
        waves = raw(path/"waves.raw")
    t = waves["time"]
    assert t[-1] >= 110e-6 * .999999
    ticks = np.arange(2201)
    times = ticks / 20e6
    banks = []
    for bank in "pn":
        bits = [np.interp(times,t,waves[f"v({bank}{i})"]) > .9 for i in range(15)]
        banks.append(sum(b.astype(np.uint16) << i for i,b in enumerate(bits)))
    dest = ROOT/"results/design_report/characterization/step_taps.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(".partial")
    with partial.open("w",newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["tick_50ns","diff_V","p_hex","n_hex"])
        for i,p,n in zip(ticks,*banks):
            writer.writerow([i,0 if i<=680 else .1,f"{p:04x}",f"{n:04x}"])
    partial.replace(dest)
    print(dest)
if __name__=="__main__":
    main()
