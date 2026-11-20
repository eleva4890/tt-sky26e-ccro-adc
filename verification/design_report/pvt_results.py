"""Reduce the two independent PEX sweeps and check the bias-specific tap clock limits."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
OUT=HERE.parent if (HERE.parent/"baseline").is_dir() else HERE.parents[1]/"results/design_report"
DATA=OUT/"characterization"
def main():
    with (DATA/"pvt.csv").open(newline="") as f:
        data=list(csv.DictReader(f))
    assert len(data)==23
    conditions=[(27,1.8),(-20,1.8),(85,1.8),(27,1.62),(27,1.98)]
    rows=[]
    for temp,vdd in conditions:
        part=sorted((r for r in data if r["corner"]=="tt" and float(r["temp_C"])==temp
                     and float(r["vdd_V"])==vdd), key=lambda r:float(r["diff_V"]))
        assert [float(p["diff_V"]) for p in part]==[-.16,0,.16]
        assert all(float(p["fmin30_MHz"])>0 for p in part)
        df=[float(p["fp_MHz"])-float(p["fn_MHz"]) for p in part]
        f0=.5*(float(part[1]["fp_MHz"])+float(part[1]["fn_MHz"]))
        gain=(df[-1]-df[0])/.32
        rows.append(dict(temp_C=temp,vdd_V=vdd,gain_MHz_V=gain,f0_MHz=f0))
    for r in rows:
        r["gain_change_percent"]=100*(r["gain_MHz_V"]/rows[0]["gain_MHz_V"]-1)
    temp=[rows[1],rows[0],rows[2]]
    supply=[rows[3],rows[0],rows[4]]
    drift_temp=(temp[-1]["gain_change_percent"]-temp[0]["gain_change_percent"])/105
    drift_supply=(supply[-1]["gain_change_percent"]-supply[0]["gain_change_percent"])/.36
    clocks=[]
    for b in range(4):
        points=[r for r in data if r["corner"]=="ff" and int(r["bias"])==b]
        assert len(points)==2 and min(float(r["diff_V"]) for r in points)<0
        peak=max(float(r["fmax30_MHz"]) for r in points)
        clocks.append(dict(bias=b,abs_diff_V=abs(float(points[0]["diff_V"])),max_tap_MHz=peak,
            strict_2f_MHz=2*peak,guard_2p5f_MHz=2.5*peak,
            active_at_both_ends=all(float(r["fmin30_MHz"])>0 for r in points)))
    fig,axes=plt.subplots(2,2,figsize=(7.2,3.55),layout="constrained")
    for j,(rr,key,label) in enumerate([(temp,"temp_C","Temperature (°C), 1.80 V"),(supply,"vdd_V","Supply (V), 27 °C")]):
        for i,(metric,unit) in enumerate([("gain_change_percent","Gain change (%)"),("f0_MHz","Zero-input f0 (MHz)")]):
            ax=axes[i,j]
            ax.plot([r[key] for r in rr],[r[metric] for r in rr],"o-",color=("#00776d","#37668a")[i])
            ax.set(xlabel=label if i else "",ylabel=unit)
            ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y",alpha=.23)
    fig.savefig(OUT/"figures/char_pvt.png",dpi=200)
    plt.close(fig)
    result=dict(tt=rows,temperature_pct_per_C=drift_temp,supply_pct_per_V=drift_supply,clock_points=clocks)
    (DATA/"pvt_summary.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    main()
