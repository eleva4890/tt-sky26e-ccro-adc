"""50 PDK mismatch draws of the extracted front end, with typical measured ring load and f(I)."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import csv
import subprocess
import tempfile
import numpy as np
from a0 import MODEL, ROOT

dest=ROOT/"results/audited"
with (dest/"a0.csv").open() as f:
    ref=[r for r in csv.DictReader(f) if r["corner"]=="tt" and float(r["temp_C"])==27]
amps=np.array([float(r["current_uA"]) for r in ref])
vcurve=np.polynomial.Polynomial.fit(amps-10,[float(r["rail_V"]) for r in ref],3).convert()
with (dest/"a0_mismatch_range.csv").open() as f:
    extra=list(csv.DictReader(f))
if len(extra)!=4 or any(r["corner"]!="tt" or float(r["temp_C"])!=27 for r in extra):
    raise ValueError("Incomplete TT load calibration extension")
fit_rows=ref+extra
fit_current=np.array([float(r["current_uA"]) for r in fit_rows])
fcurve=np.polynomial.Polynomial.fit(fit_current,[float(r["f_MHz"]) for r in fit_rows],3)
def trial(seed):
    deck=f"""Front-end mismatch with nominal rings
.option seed={seed}
.lib "{MODEL}" tt_mm
.include "{ROOT/'layout/analog_cells/eleva_frontend_c.spice'}"
.option scale=1u
.temp 27
Vdd v 0 1.8
Vcm cm 0 .63
Vexc diff 0 0
Ep p cm diff 0 .5
En n cm diff 0 -.5
Xf p n 0 0 rp rn v 0 front_flat
Vload ref 0 {vcurve(0)}
Vsp rp lp 0
Vsn rn ln 0
Ip lp 0 10u
In ln 0 10u
Rlp lp ref {vcurve.deriv()(0)*1e6}
Rln ln ref {vcurve.deriv()(0)*1e6}
.control
set wr_singlescale
set numdgt=12
dc Vexc -.2 .2 .01
wrdata data i(Vsp) i(Vsn)
quit
.endc
.end
"""
    with tempfile.TemporaryDirectory() as tmp:
        d=Path(tmp)
        (d/".spiceinit").write_text((MODEL.parent/"spinit").read_text()+f"\nset num_threads=1\noption seed={seed}\n")
        (d/"mc.cir").write_text(deck)
        driver=f"Seed before sourcing the mismatch model\n.control\nsetseed {seed}\nsource mc.cir\nquit\n.endc\n.end\n"
        (d/"driver.cir").write_text(driver)
        p=subprocess.run(["ngspice","-b","driver.cir"],cwd=d,capture_output=True,text=True)
        if not (d/"data").exists():raise ValueError(p.stderr[-700:])
        x,ip,inn=np.loadtxt(d/"data").T
    ip,inn=ip*1e6,inn*1e6
    if len(x)!=41 or not np.all(np.isfinite(ip+inn)):raise ValueError(seed)
    fp,fn=fcurve(ip),fcurve(inn)
    coeff=np.polynomial.chebyshev.chebfit(x/.2,fp-fn,5)
    idx=np.argmin(abs(x))
    sp=np.polyfit(x,fp,1)[0]
    sn=-np.polyfit(x,fn,1)[0]
    return (seed,ip.min(),ip.max(),inn.min(),inn.max(),fp[idx]-fn[idx],
            2*(sp-sn)/(sp+sn),-1000*(fp[idx]-fn[idx])/(sp+sn),
            20*np.log10(abs(coeff[2]/coeff[1])),max(fp.max(),fn.max()),
            int(np.ceil(30*max(fp.max(),fn.max())/20)),
            min(ip.min(),inn.min())>=fit_current.min() and max(ip.max(),inn.max())<=fit_current.max())

if __name__=="__main__":
    with ThreadPoolExecutor(3) as pool:
        a,b,repeat=pool.map(trial,[26001,26002,26001])
        if not np.allclose(np.asarray(a,float),np.asarray(repeat,float)) or abs(a[5]-b[5])<1e-6:
            raise ValueError(f"Mismatch seed check: {a}, {b}, repeat {repeat}")
        rows=[a,b,*pool.map(trial,range(26003,26051))]
    with (dest/"front_mismatch.csv").open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow("seed ip_min_uA ip_max_uA in_min_uA in_max_uA df0_MHz gain_asymmetry offset_mV HD2_dBc max_f_MHz max_ideal_edges_20MHz interpolation_in_range".split())
        w.writerows(rows)
    print("50 PDK front-end draws, repeated first seed; inside calibrated current range",sum(r[-1] for r in rows))
