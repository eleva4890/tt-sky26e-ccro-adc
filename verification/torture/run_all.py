"""Run every requested extracted/RTL test, refresh the report, and verify the ZIP."""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
import json
from bench import run, OUT
from ramp_comparison import adopt
from report import CASES, verify_input, main as package
from t6 import main as digital
if __name__=="__main__":
    ap=ArgumentParser()
    ap.add_argument("--jobs",type=int,default=2)
    ap.add_argument("--ramp-solver",choices=("archived","strict","crosschecked"),default="archived")
    arg=ap.parse_args()
    verify_input()
    digital()
    mode=arg.ramp_solver
    if mode=="archived":
        rec=OUT/"T2_ramp.json"
        mode="crosschecked" if rec.exists() and "measured_case" in json.loads(rec.read_text()) else "strict"
    todo=[c for c in CASES if c!="T6" and not (mode=="crosschecked" and c=="T2_ramp")]
    if mode=="crosschecked":todo+=["T2_reference_alt","T2_ramp_alt"]
    with ThreadPoolExecutor(arg.jobs) as pool:
        list(pool.map(run,todo))
    if mode=="crosschecked":adopt()
    package()
