"""Plot decoded step responses and summarize explicit geometrical capacitances at each input."""
from pathlib import Path
import csv
import json
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
BUNDLE=(HERE.parent/"baseline").is_dir()
ROOT=HERE.parent if BUNDLE else HERE.parents[1]
OUT=ROOT if BUNDLE else ROOT/"results/design_report"
DATA=OUT/"characterization"


def main():
    model=(ROOT/("design" if BUNDLE else "")/"layout/integration/final_analog_c.spice").read_text()
    extracted={}
    for pin in ("vinp","vinn"):
        total=0
        for line in model.splitlines():
            fields=line.split()
            if len(fields)!=4 or not re.fullmatch(r"C\d+",fields[0]) or pin not in fields[1:3]:
                continue
            if fields[3]!="0" and not fields[3].endswith("f"):
                raise ValueError(line)
            total+=float(fields[3].removesuffix("f"))
        extracted[pin]=total
    (DATA/"wire_caps_fF.json").write_text(json.dumps(extracted,indent=2)+"\n")
    with (DATA/"step_spi_words.csv").open() as f:
        words=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(7.2,2.25),layout="constrained")
    for rate,color in [(128,"#00776d"),(256,"#b04a2d")]:
        example=[w for w in words if int(w["osr"])==rate and int(w["reset_delay_ticks"])==0]
        ax.step([int(w["cs_end_tick"])*.05-34.025 for w in example],[int(w["signed_code"]) for w in example],
                where="post",marker="o",ms=3,color=color,label=f"OSR {rate}")
    ax.axvline(0,ls="--",color="#486474",lw=.8)
    ax.set(xlim=(-15,70),xlabel="Time from input step midpoint (µs)",ylabel="Completed SPI code")
    ax.legend(fontsize=8); ax.spines[["top","right"]].set_visible(False);ax.grid(axis="y",alpha=.2)
    fig.savefig(OUT/"figures/char_step.png",dpi=200)
    plt.close(fig)
if __name__=="__main__":
    main()
