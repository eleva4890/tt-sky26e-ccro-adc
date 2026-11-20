"""Gate activity and Liberty/SPEF digital supply-current estimates for board bring-up."""
import csv
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def main():
    pdk = (Path(os.environ["PDK_ROOT"]) / "sky130A").resolve()
    verilog = pdk / "libs.ref/sky130_fd_sc_hd/verilog"
    iv = Path(os.environ.get("IVERILOG", "/usr/bin/iverilog"))
    base = os.environ.get("IVERILOG_BASE")
    result = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        subprocess.run([iv, *(["-B", base] if base else []), "-g2012", "-DFUNCTIONAL",
                        "-DUNIT_DELAY=#0.1", "-s", "current_tb", "-o", work/"sim",
                        verilog/"primitives.v", verilog/"sky130_fd_sc_hd.v",
                        ROOT/"layout/readout/adc_readout.nl.v", HERE/"current_tb.v"], check=True)
        for mode, state in enumerate(("reset_clk_low", "run_zero", "run_pos_fs")):
            subprocess.run([iv.with_name("vvp"),work/"sim",f"+MODE={mode}"], cwd=work,check=True)
            # Shift the recorded time origin to zero so the warm-up is outside the averaging window.
            vcd = work/"activity.vcd"
            source = vcd.read_text()
            first = int(re.search(r"^#(\d+)", source, re.M)[1])
            assert first > 0
            vcd.write_text(re.sub(r"^#(\d+)",lambda m:f"#{int(m[1])-first}",source,flags=re.M))
            for rc, corner, volts in (("min","ff_n40C_1v95",1.95),("nom","tt_025C_1v80",1.8),
                                      ("max","ss_100C_1v60",1.6)):
                command = ["docker","run","--rm","--read-only","--network","none",
                           "-v",f"{ROOT}:/design:ro","-v",f"{pdk}:/pdk:ro","-v",f"{work}:/work:ro",
                           "-e",f"PWR_CORNER={corner}","-e",f"PWR_RC={rc}","-e",f"PWR_MODE={mode}",
                           "efabless/openlane:2023.09.07","sta","-exit","/design/verification/design_report/current_sta.tcl"]
                log = subprocess.check_output(command,text=True,stderr=subprocess.STDOUT)
                if "Error:" in log or "Total" not in log:
                    raise ValueError(log[-2400:])
                pins = int(re.search(r"Annotated (\d+) pin activities",log)[1])
                assert pins >= 1600, pins
                print(pins, "annotated pins", log[-900:], flush=True)
                fields = re.findall(r"^Total\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",log,re.M)
                assert len(fields)==1
                internal, switching, leakage, total=map(float,fields[0])
                result.append((state,corner,volts,internal,switching,leakage,total,total/volts*1e6))
    out=ROOT/"results/design_report/digital_current.csv"
    with out.open("w", newline="") as f:
        writer=csv.writer(f)
        writer.writerow(("state","liberty","V","internal_W","switching_W","leakage_W","total_W","digital_uA"))
        writer.writerows(result)

if __name__=="__main__":
    main()
