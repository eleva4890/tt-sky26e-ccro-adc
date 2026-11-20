"""Full-chip analog macro torture benches. Dimensions in microseconds except SPICE suffixes."""
from pathlib import Path
import hashlib, json, os, re, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/torture"
WORK=Path(os.environ.get("TORTURE_WORK","/tmp/ccro-torture-v1"))
CORE=ROOT/"layout/integration/final_analog_c.spice"
PDK=Path(os.environ["PDK_ROOT"])/"sky130A/libs.tech/ngspice"
CAPS=(ROOT/"results/audited/interface_caps.spice").read_text()
TAPS=[f"{side}{i}" for side in "pn" for i in range(15)]
INTERNAL=[f"xadc.{s}{ab}{i}" for s in "pn" for ab in "ab" for i in range(15)]
def digest(p):
    with p.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()
def voltage(s):return f"v({s})"
def raw(path):
    with path.open("rb") as f:
        header=[]
        while True:
            line=f.readline()
            if not line: raise ValueError("incomplete raw header")
            if line.strip()==b"Binary:":break
            header.append(line.decode())
        h="".join(header)
        n=int(re.search(r"No. Variables:\s+(\d+)",h)[1])
        points=int(re.search(r"No. Points:\s+(\d+)",h)[1])
        names=[s.split()[1].lower() for s in h.split("Variables:\n")[-1].splitlines() if s.strip()]
        data=np.fromfile(f,dtype="<f8").reshape(points,n)
    assert len(names)==n and np.all(np.isfinite(data))
    return dict(zip(names,data.T))
def make(case):
    tag=case.split("_")[0]
    core=CORE.read_text()
    vdd=1.8; temp=27; corner="tt"; mode=0; stop=10.; begin=0.; step=8.; tol=".0005"
    sup="pwl(0 0 1u 1.8)"; dsrc="0"; cm=".63"; rc=1500; pf=5.; ic=""; extra=""
    probes=[voltage(n) for n in ["vdd","vg","xadc.rp","xadc.rn","xadc.vb","p0","n0"]]
    # Source/input references track the quiet package ground. Receiver metal capacitances
    # return to the local ground for the SSN scenario.
    network="Vg vg 0 0\nVs vdd 0 "+sup
    saves=list(probes)
    if tag=="T1":
        _,corner,bias=case.split("_"); mode=int(bias)
        network="Vg vg 0 0\nVs vdd 0 1.8"
        ic=".ic "+" ".join(f"v({n})=.35" for n in INTERNAL)
        saves += list(map(voltage,INTERNAL))
        stop,step=(8,8) if not mode else (175,120)
    elif case in ("T2_ramp","T2_reference","T2_ramp_alt","T2_reference_alt"):
        mode=1
        network="Vg vg 0 0\nVs vdd 0 pwl(0 0 10m 1.8)"
        stop,begin,step=10100,9950,500
        if case.startswith("T2_reference"):
            network="Vg vg 0 0\nVs vdd 0 pwl(0 0 1u 1.8)"
            stop,begin,step=100,10,100
        if case.endswith("_alt"):
            # Independent full-PEX convergence study. Preserve the physical source,
            # all extracted devices/loads and the entire 10-ms supply trajectory.
            tol=".003";step=50;begin=0
            extra="\n.option itl4=100 trtol=12 vntol=3u abstol=3p"
        saves+=list(map(voltage,TAPS[1:15]+TAPS[16:]))
    elif case=="T2_brown":
        network="Vg vg 0 0\nVs vdd 0 pwl(0 0 1u 1.8 6u 1.8 6.01u .6 56.01u .6 56.02u 1.8)"
        stop,step=63,12
        saves+=list(map(voltage,TAPS[1:15]+TAPS[16:]))
    elif case=="T2_leak":
        mode=1; corner="ff";temp=85; vdd=1.98
        network="Vg vg 0 0\nVs vdd 0 pwl(0 0 1u 1.98)"
        # Split each bank's device drain from the original node with a zero-volt
        # current probe. All other transistors and capacitors retain their endpoints.
        for side,node in (("p","sp"),("n","sn")):
            for key,gates,count in [("off","g4|g15|g20",39),("on","vb",1)]:
                pat=rf"(?m)^(X\d+) {node} ({gates}) v v sky130_fd_pr__pfet_01v8 (?=[^\n]*\bw=1 l=2\b)"
                core,num=re.subn(pat,rf"\1 probe_{side}{key} \2 v v sky130_fd_pr__pfet_01v8 ",core)
                reverse=rf"(?m)^(X\d+) v ({gates}) {node} v sky130_fd_pr__pfet_01v8 (?=[^\n]*\bw=1 l=2\b)"
                core,nrev=re.subn(reverse,rf"\1 v \2 probe_{side}{key} v sky130_fd_pr__pfet_01v8 ",core)
                assert num+nrev==count,(node,key,num,nrev)
                core=core.replace(".ends",f"V{side}{key} probe_{side}{key} {node} 0\n.ends",1)
                saves.append(f"i(v.xadc.v{side}{key})")
        stop,begin,step=25,4,3
    elif case in ("T5_hold","T5_hold_mid"):
        # Acquire at zero input, then test whether a small detuning escapes
        # the naturally established phase relation for a full nominal beat.
        dsrc="pwl(0 0 12u 0 12.01u .001)"
        if case=="T5_hold_mid":
            core=core.replace(".ends","Xtest_mid mid g sky130_fd_pr__cap_mim_m3_1 w=10 l=10\n.ends",1)
        stop,begin,step=180,10,6
        tol=".0015";extra="\n.option itl4=100 trtol=9"
        saves+=list(map(voltage,TAPS[1:15]+TAPS[16:]))
    elif tag=="T5":
        _,mid,add=("T5","0","0") if case.startswith("T5_tracking") else case.split("_")
        if int(mid):core=core.replace(".ends","Xtest_mid mid g sky130_fd_pr__cap_mim_m3_1 w=10 l=10\n.ends",1)
        if add=="removed":
            core,num=re.subn(r"(?m)^C\d+ rp rn 4\.1989f$","* direct rail coupling removed for sensitivity analysis",core)
            assert num==1
        elif float(add):core=core.replace(".ends",f"Ctest_coup rp rn {add}f\n.ends",1)
        dsrc=".001";stop,begin,step=25,13,3
        if case.startswith("T5_tracking"):dsrc="pwl(0 0 1u .001)"
        if case=="T5_tracking_2ns":step=2
        saves+=list(map(voltage,TAPS[1:15]+TAPS[16:]))
    elif case=="T4_step":
        dsrc="pwl(0 0 2u 0 2.01u .6 5u .6 5.01u .1 9u .1 9.01u -.6 12u -.6 12.01u -.1)"
        cm="v(cmctl)*v(vdd)/1.8"
        extra="Vcmctl cmctl 0 pwl(0 .63 16u .63 16.01u .48 21u .48 21.01u .78 26u .78 26.01u .63)"
        stop=31;step=5
        saves+=list(map(voltage,TAPS[1:15]+TAPS[16:]))
    elif tag=="T4":
        # 50 kHz near the nominal 78.125-kHz output Nyquist limit. Identical
        # 10-pF pin shunt in both simulations isolates the series-R contribution.
        rc=0 if case.endswith("ideal") else 1500;pf=10;tol=".0003"
        dsrc="sin(0 .2 50000 1u)";stop,begin,step=53,11,2
        saves+=list(map(voltage,TAPS[1:15]+TAPS[16:]))
    elif tag=="T3":
        # 16 coherent 156.25-kS/s output frames, retaining one tone cycle per
        # eight frames (19.53125 kHz), with an extra 3 frames for CIC settlement.
        stop,step=136,2;tol=".0003"
        dsrc="sin(0 .17825019 19531.25 1u)"
        network=("Vs supply 0 pwl(0 0 1u 1.8)\nRpkg supply ps 5\nLpkg ps vdd 2n\n"
                 "Rg pg 0 5\nLg vg pg 2n")
        if case.endswith("dirty"):
            network+="\nIclk vdd vg pulse(0 1m 1u 1n 1n 24n 50n)\nIout vdd vg pulse(0 1m 1u 1n 1n 3199n 6400n)"
        saves+=list(map(voltage,TAPS[1:15]+TAPS[16:]))
    else:raise ValueError(case)
    common=cm if case=="T4_step" else f"({cm})*v(vdd,vg)/{vdd}"
    # At the quiet source, the common mode follows the ideal supply during startup
    # and stays fixed when the package rails bounce.
    if tag=="T3":common=".63*v(supply)/1.8"
    input_sources=f"Bp ep 0 v={common}+.5*v(diff)\nBn en 0 v={common}-.5*v(diff)"
    if case=="T2_leak" or case in ("T2_ramp_alt","T2_reference_alt"):
        input_sources="Ep ep 0 vdd 0 "+str(.63/vdd)+"\nEn en 0 vdd 0 "+str(.63/vdd)
        if case=="T2_leak":extra+="\n.option itl4=100"
    if case in ("T5_hold","T5_hold_mid"):
        input_sources="Ecm cm 0 vdd vg .35\nEpos ep cm diff 0 .5\nEneg en cm diff 0 -.5"
    io="\n".join(line.replace(" 0 "," vg ") for line in CAPS.splitlines())
    loads="\n".join(f"Cl{i} {p} vg 5f" for i,p in enumerate(TAPS))
    drv="Rp ep vinp 1500\nRn en vinn 1500" if rc else "Vp ep vinp 0\nVn en vinn 0"
    external_caps=f"Cp vinp 0 {pf}p\nCn vinn 0 {pf}p"
    if case.startswith("T4_literal_"):
        drv="Rp ep xp 1500\nRn en xn 1500" if rc else "Vp ep xp 0\nVn en xn 0"
        # Literal series RC blocks the pad's DC bias. An identical high-Z common-mode
        # return in both controls sets the DC condition without shorting the AC input.
        external_caps=("Cp xp vinp 10p\nCn xn vinn 10p\nBcmref cmref 0 v=.63*v(vdd)/1.8\n"
                       "Rbp vinp cmref 100meg\nRbn vinn cmref 100meg")
    vs=" ".join(dict.fromkeys(saves))
    deck=f"""CCRO {case}
.lib "{PDK/'sky130.lib.spice'}" {corner}
.include core.spice
.option scale=1u method=gear reltol={tol} klu
.temp {temp}
{network}
{extra}
Vinput diff 0 {dsrc}
{input_sources}
Eb0 b0 vg vdd vg {mode&1}
Eb1 b1 vg vdd vg {mode>>1}
{drv}
{external_caps}
Xadc vinp vinn b0 b1 vdd vg {' '.join(TAPS)} eleva_adc_analog
{loads}
{io}
{ic}
.control
set num_threads=1
set filetype=binary
save {vs}
tran {step}n {stop}u {begin}u {step}n
write waves.raw all
quit
.endc
.end
"""
    return deck,core,stop
def run(case):
    OUT.mkdir(parents=True,exist_ok=True)
    path=WORK/case;path.mkdir(parents=True,exist_ok=True)
    deck,core,stop=make(case)
    fingerprint=hashlib.sha256((deck+core+(PDK/"spinit").read_text()).encode()).hexdigest()
    meta=path/"completed.json"
    if not (meta.exists() and json.loads(meta.read_text())["input_sha256"]==fingerprint and (path/"waves.raw").exists()):
        (path/"test.cir").write_text(deck);(path/"core.spice").write_text(core)
        (path/".spiceinit").write_text((PDK/"spinit").read_text()+"\nset num_threads=1\n")
        rawfile=path/"waves.raw"
        if rawfile.exists():rawfile.unlink()
        with (path/"run.log").open("wb") as log:
            p=subprocess.run(["ngspice","-b","test.cir"],cwd=path,stdout=log,stderr=subprocess.STDOUT)
        if p.returncode or not rawfile.exists():raise ValueError(case+" "+(path/"run.log").read_text(errors="replace")[-1300:])
    waves=raw(path/"waves.raw")
    if waves["time"][-1]<stop*.999999e-6:raise ValueError(f"{case} incomplete {waves['time'][-1]}")
    meta.write_text(json.dumps(dict(input_sha256=fingerprint,stop_us=stop,points=len(waves["time"]))))
    from score import evaluate
    data=evaluate(case,waves)
    data.update(case=case,deck_sha256=fingerprint,pex_sha256=digest(CORE),
                raw_sha256=digest(path/"waves.raw"),stored_points=len(waves["time"]),
                actual_stop_us=float(waves["time"][-1]*1e6))
    (OUT/(case+".json")).write_text(json.dumps(data,indent=2,allow_nan=False)+"\n")
    print(case,data.get("status"),flush=True)
if __name__=="__main__":
    from argparse import ArgumentParser
    ap=ArgumentParser();ap.add_argument("cases",nargs="+");ap.add_argument("--jobs",type=int,default=2);arg=ap.parse_args()
    with ThreadPoolExecutor(arg.jobs) as pool:
        fs=[pool.submit(run,c) for c in arg.cases]
        for f in as_completed(fs):f.result()
