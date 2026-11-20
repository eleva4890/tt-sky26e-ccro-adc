"""Run loaded macro PEX with one temperature or supply change per TT measurement."""
import csv
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "verification"))
from pair import HEADER, run


def main():
    os.chdir(ROOT)
    os.environ["ADC_FULL"] = str(ROOT / "layout/integration/final_analog_c.spice")
    os.environ["ADC_INTERFACE_CAPS"] = str(ROOT / "results/audited/interface_caps.spice")
    os.environ["ADC_PAIR_STEP_NS"] = "2"
    for key in ("ADC_TRACE_DIR", "ADC_DUAL", "ADC_TEST_MID_SIDE", "ADC_STUDY_RAIL_COUPLING"):
        os.environ.pop(key, None)
    conditions = [(27, 1.8), (-20, 1.8), (85, 1.8), (27, 1.62), (27, 1.98)]
    cases = [("tt", temp, vdd, 0, vin, .63, 1, 6)
             for temp, vdd in conditions for vin in (-.16, 0, .16)]
    for mode, voltage, duration in [(0, .2, 6), (1, .035, 36), (2, .095, 14), (3, .2, 6)]:
        cases.extend(("ff", 85, 1.98, mode, sign * voltage, .63, 1, duration)
                     for sign in (-1, 1))
    dest = ROOT / "results/design_report/characterization/pvt.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.with_suffix(".partial").open("w", newline="") as out, ThreadPoolExecutor(5) as workers:
        writer = csv.writer(out)
        writer.writerow(HEADER)
        for row in workers.map(run, cases):
            writer.writerow(row)
            out.flush()
            print(row[:6], row[10:14], flush=True)
    dest.with_suffix(".partial").replace(dest)


if __name__ == "__main__":
    main()
