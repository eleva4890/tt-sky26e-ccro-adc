"""Measure the quadrature current at each running macro input, excluding the fixture."""
import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"verification/torture"))
from bench import CAPS, CORE, PDK, TAPS, raw


def main():
    loads="\n".join(f"Cload{i} {p} 0 5f" for i,p in enumerate(TAPS))
    deck=f"""Small-signal differential drive, TT at 50 kHz, 10 mV peak per pin
.lib "{PDK/'sky130.lib.spice'}" tt
.include "{CORE}"
.temp 27
.option scale=1u method=gear reltol=.0005 klu
Vdd v 0 pwl(0 0 1u 1.8)
Ecm cm 0 v 0 .35
Vd d 0 sin(0 .02 50k)
Ep ep cm d 0 .5
En en cm d 0 -.5
Rp ep xp 1.5k
Rn en xn 1.5k
Cp xp 0 5p
Cn xn 0 5p
Vap xp ip 0
Van xn in 0
Xadc ip in 0 0 v 0 {' '.join(TAPS)} eleva_adc_analog
{CAPS}
{loads}
.control
set num_threads=1
set filetype=binary
save v(ip) v(in) i(Vap) i(Van)
tran 2n 105u 0 2n
write waves.raw all
quit
.endc
.end
"""
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)
        (path/"input.cir").write_text(deck)
        (path/".spiceinit").write_text((PDK/"spinit").read_text()+"\nset num_threads=1\n")
        subprocess.run(["ngspice","-b","input.cir"],cwd=path,stdout=subprocess.DEVNULL,check=True)
        w=raw(path/"waves.raw")

    reduce_current(w)


def reduce_current(w):
    t=w["time"]
    assert t[-1]>=104.999e-6
    integrate=getattr(np,"trapezoid",None) or np.trapz
    dest=ROOT/"results/design_report/characterization/macro_input.csv"
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["pin","t0_us","t1_us","Ceff_fF","conductance_nS"])
        for pin,sense,name in [("ip","vap","vinp"),("in","van","vinn")]:
            v=w[f"v({pin})"]; current=w[f"i({sense})"]
            for lo,hi in [(20,60),(60,100),(20,100)]:
                a,b=lo*1e-6,hi*1e-6
                times=np.r_[a,t[(t>a)&(t<b)],b]
                phase=np.exp(-2j*np.pi*50e3*times)
                # Integrate an integer number of periods and compare adjacent records.
                def phasor(z):
                    return integrate(np.interp(times,t,z)*phase,times)
                admittance=phasor(current)/phasor(v)
                writer.writerow([name,lo,hi,admittance.imag/(2*np.pi*50e3)*1e15,admittance.real*1e9])
    print(dest.read_text())
if __name__=="__main__":
    main()
