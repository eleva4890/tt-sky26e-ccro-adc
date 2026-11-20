"""Check the full triangular FIR settling time at every decimator phase in RTL."""
import csv
from pathlib import Path
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
def main():
    override=["-B",os.environ["IVL_DIR"]] if "IVL_DIR" in os.environ else []
    with tempfile.TemporaryDirectory() as tmp:
        sim=Path(tmp)/"latency"
        subprocess.run(["iverilog",*override,"-g2012","-s","ideal_latency_tb","-o",sim,
                        ROOT/"rtl/adc_readout.v",HERE/"ideal_latency_tb.v"],check=True)
        def run(rate):
            output=subprocess.check_output(["vvp",sim,f"+RATE={rate}"],text=True)
            points=[list(map(int,line.split()[1:])) for line in output.splitlines() if line.startswith("PHASE")]
            assert len(points)==rate and len({p[-1] for p in points})==rate
            assert min(p[-1] for p in points)==2*rate+97
            assert max(p[-1] for p in points)==3*rate+96
            return points
        with ThreadPoolExecutor(2) as pool:
            results=list(pool.map(run,(128,256)))
    out=ROOT/"results/design_report/characterization/ideal_step.csv"
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="") as f:
        writer=csv.writer(f); writer.writerow(["osr","relative_phase","sample_to_cs_end_ticks"])
        for rows in results: writer.writerows(rows)
    print([(rows[0][0],min(r[-1] for r in rows),max(r[-1] for r in rows)) for rows in results])
if __name__=="__main__":
    main()
