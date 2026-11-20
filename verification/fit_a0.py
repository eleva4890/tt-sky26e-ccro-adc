"""Least-squares fits in normalized input current. Report residual and local fit sensitivity."""
import csv
import sys
from pathlib import Path
import numpy as np

def main(source,target):
    with open(source) as f:
        data=list(csv.DictReader(f))
    corners={(r["corner"],float(r["temp_C"])) for r in data}
    with open(target,"w",newline="") as out:
        w=csv.writer(out)
        w.writerow("corner temp_C points f0_MHz a1 c2_over_linear c3_over_linear c3_inner25 rring_ohm max_fit_ppm worst_tap_lo_V worst_tap_hi_V".split())
        for c,t in sorted(corners):
            rows=sorted([r for r in data if r["corner"]==c and float(r["temp_C"])==t],key=lambda r:float(r["current_uA"]))
            if len(rows)<21: raise ValueError(f"Incomplete sweep at {c},{t}")
            x=np.array([float(r["current_uA"])/10.-1 for r in rows])
            y=np.array([float(r["f_MHz"]) for r in rows])
            rail=np.array([float(r["rail_V"]) for r in rows])
            a=np.polynomial.polynomial.polyfit(x,y,3)
            inner=np.abs(x)<=.25
            local=np.polynomial.polynomial.polyfit(x[inner],y[inner],3)
            b=np.polynomial.polynomial.polyfit(x,rail,3)
            residual=np.max(np.abs(np.polynomial.polynomial.polyval(x,a)-y))/a[0]
            w.writerow([c,t,len(x),a[0],a[1]/a[0],a[2]/a[1],a[3]/a[1],local[3]/local[1],
                        b[1]/10e-6,residual*1e6,max(float(r["tap_lo_V"]) for r in rows),min(float(r["tap_hi_V"]) for r in rows)])
if __name__=="__main__":
    main(*sys.argv[1:])
