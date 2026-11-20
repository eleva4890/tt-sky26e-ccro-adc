"""Score harmonic limits from the active project specification and measured A4 data."""
import csv
from pathlib import Path
import re
import argparse
import numpy as np

root=Path(__file__).resolve().parents[1]
results=root/"results/audited"
spec=(root/"docs/01_SPEC.md").read_text(encoding="utf-8")
limits={order:float(re.search(rf"HD{order} ≤ (−[\d.]+) dBc",spec)[1].replace("−","-")) for order in (2,3)}

def static(path):
    with path.open() as f:
        rows=list(csv.DictReader(f))
    x=np.array([float(r["diff_V"]) for r in rows])
    df=np.array([float(r["fp_MHz"])-float(r["fn_MHz"]) for r in rows])
    if len(x)!=11 or not np.isclose(x.min(),-.2) or not np.isclose(x.max(),.2):
        raise ValueError(f"Incomplete sweep {path}")
    h=np.polynomial.chebyshev.chebfit(x/.2,df,5)
    return {n:20*np.log10(abs(h[n]/h[1])) for n in limits}

def dynamic(path):
    with path.open() as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=9:raise ValueError(path)
    return {int(r["harmonic"]):float(r["relative_dBc"]) for r in rows if int(r["harmonic"]) in limits}

def summarize(available_only=False):
    records=[]
    for model,prefix in [("coupled oscillators + schematic front end",""),("complete analog GDS","full_")]:
        tt=static(results/f"{prefix}tt.csv")
        ss=static(results/f"{prefix}ss.csv")
        path=results/f"{prefix}dynamic.csv"
        ac=dynamic(path) if path.exists() or not available_only else {}
        for condition,values in [("TT 1.80 V static",tt),("SS 1.62 V static",ss),("TT 1.80 V 50 kHz",ac)]:
            for n,measured in values.items():
                margin=limits[n]-measured
                records.append([model,condition,f"HD{n}","dBc",f"{measured:.4f}",limits[n],f"{margin:.4f}","PASS" if margin>=0 else "FAIL"])
        for n in ac:
            delta=abs(tt[n]-ac[n])
            records.append([model,"TT static/dynamic difference",f"HD{n}","dB",f"{delta:.4f}",1.0,f"{1.-delta:.4f}","PASS" if delta<=1. else "FAIL"])
    with (results/"a4_v3_1.csv").open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["model","condition","quantity","unit","value","upper_limit","margin_dB","result"])
        w.writerows(records)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--available-only",action="store_true",help="Score completed runs while a transient is still running")
    summarize(parser.parse_args().available_only)
