"""Accept the independent full-duration ramp solver only if its reference matches the stricter run."""
from pathlib import Path
import json
from bench import WORK, OUT, raw
import numpy as np

def qualify():
    names=["T2_reference","T2_reference_alt","T2_ramp_alt"]
    if not all((OUT/(n+".json")).exists() for n in names):return None
    strict,alt,ramp=[json.loads((OUT/(n+".json")).read_text()) for n in names]
    anchor=("fp_MHz","fn_MHz","min_tap_MHz","max_tap_MHz","vb_V","min_swing_V")
    err={k:abs(alt["tail"][k]/strict["tail"][k]-1) for k in anchor}
    if max(err.values())>.01:return None
    if len({x["pex_sha256"] for x in (strict,alt,ramp)})!=1:return None
    w=raw(WORK/"T2_ramp_alt/waves.raw")
    t=w["time"];sup=w["v(vdd)"]-w["v(vg)"]
    v_err=float(np.max(np.abs(sup-1.8*np.minimum(t/.01,1.0))))
    if t[0]>1e-9 or t[-1]<.01009999 or v_err>1e-5:return None
    return dict(reference_relative_differences=err,reference_limit=.01,trajectory_error_V=v_err,
        simulated_start_s=float(t[0]),simulated_end_s=float(t[-1]),
        timestep_max_ns=50,reltol=.003,reference_reltol=.0005,
        strict_reference_sha256=strict["deck_sha256"],alternate_reference_sha256=alt["deck_sha256"])
def adopt():
    proof=qualify()
    if proof is None:raise ValueError("Independent ramp solver has not met its numerical cross-check")
    alt=json.loads((OUT/"T2_ramp_alt.json").read_text())
    alt.update(case="T2_ramp",measured_case="T2_ramp_alt",numerical_cross_check=proof)
    (OUT/"T2_ramp.json").write_text(json.dumps(alt,indent=2,allow_nan=False)+"\n")
    print("T2_ramp: continuous full-PEX alternative qualified",proof)
if __name__=="__main__":adopt()
