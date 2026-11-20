"""Replay a loaded PEX step through routed gates; decode the actual serial pin edges."""
import csv
import json
import os
from pathlib import Path
import subprocess
import tempfile
import statistics

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/"results/design_report/characterization"


def main():
    lib=Path(os.environ["PDK_ROOT"])/"sky130A/libs.ref/sky130_fd_sc_hd/verilog"
    override=["-B",os.environ["IVL_DIR"]] if "IVL_DIR" in os.environ else []
    rows=[]
    metrics=[]
    with tempfile.TemporaryDirectory() as tmp:
        binary=Path(tmp)/"readout"
        subprocess.run(["iverilog",*override,"-g2012","-s","step_spi_tb","-DFUNCTIONAL","-DUNIT_DELAY=#0.1",
            "-o",binary,HERE/"step_spi_tb.v",ROOT/"layout/readout/adc_readout.nl.v",
            lib/"primitives.v",lib/"sky130_fd_sc_hd.v"],check=True)
        for rate in (128,256):
            for phase in range(0,rate,rate//4):
                log=subprocess.check_output(["vvp",binary,f"+RATE={rate}",f"+DELAY={phase}"],cwd=ROOT,text=True)
                words=[list(map(int,l.split()[1:])) for l in log.splitlines() if l.startswith("WORD ")]
                assert len(words)>=7
                rows.extend(words)
                final=statistics.median(w[-1] for w in words[-3:])
                assert 2050<final<2200
                steady=next(i for i,w in enumerate(words) if all(abs(z[-1]-final)<=.01*abs(final) for z in words[i:]))
                assert len(words)-steady>=3
                metrics.append(dict(osr=rate,reset_delay_ticks=phase,final_code=final,settled_code=words[steady][-1],
                    latency_us=words[steady][-2]*.05-34.025))
    with (OUT/"step_spi_words.csv").open("w",newline="") as stream:
        w=csv.writer(stream); w.writerow(["osr","reset_delay_ticks","cs_start_tick","cs_end_tick","signed_code"]);w.writerows(rows)
    (OUT/"step_latency.json").write_text(json.dumps(metrics,indent=2)+"\n")
    print(metrics)

if __name__=="__main__":
    main()
