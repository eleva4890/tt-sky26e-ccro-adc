"""Make two print-size panels directly from the archived SPICE samples."""
import csv
import gzip
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def plot(folder):
    fig,axes=plt.subplots(1,2,figsize=(7.25,2.45),layout="constrained")
    cases=[("T1_tt_0",0,1.6,[("v(xadc.pa0)","A[0]"),("v(xadc.pb0)","B[0]"),("v(xadc.rp)","rp")]),
           ("T2_brown",55.8,57.3,[("v(vdd)","VDPWR"),("v(xadc.vb)","VB"),("v(p0)","Tap P0")])]
    for ax,(name,lo,hi,signals) in zip(axes,cases):
        with gzip.open(folder/"waveforms"/(name+".csv.gz"),"rt") as f:
            rows=csv.DictReader(f)
            points=[]
            for r in rows:
                t=float(r["time_s"])*1e6
                if t>hi:break
                if t>=lo:points.append([t]+[float(r[k]) for k,_ in signals])
        assert len(points)>100
        time,*volts=zip(*points)
        for v,(_,label),color in zip(volts,signals,("#087c74","#b75632","#596c86")):
            ax.plot(time,v,label=label,color=color,lw=1.15)
        ax.spines[["top","right"]].set_visible(False)
        ax.set(xlabel="Time (µs)",ylabel="Voltage (V)",xlim=(lo,hi))
        ax.tick_params(labelsize=8);ax.grid(axis="y",alpha=.2)
        ax.legend(fontsize=8,ncol=3,frameon=False,loc="upper left",bbox_to_anchor=(0,1.2))
    fig.savefig(folder/"figures/startup_recovery.png",dpi=220)
    plt.close(fig)

if __name__=="__main__":
    here=Path(__file__).resolve().parent
    plot(here.parent if (here.parent/"waveforms").is_dir() else here.parents[1]/"results/design_report")
