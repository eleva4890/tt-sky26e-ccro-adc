"""Build the stress-test report from completed extracted and digital simulations."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json, os, re, shutil, sys, tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from package import write_member
ROOT=Path(__file__).resolve().parents[2]
CASES=[f"T1_{c}_{b}" for c in ("tt","ss","ff","sf","fs") for b in (0,1)]
CASES+=["T2_reference","T2_ramp","T2_brown","T2_leak","T3_clean","T3_dirty","T4_step","T4_ideal","T4_series","T4_literal_ideal","T4_literal_series"]
CASES += [f"T5_{m}_{c}" for m in (0,1) for c in ("removed",0,1,5,20,50)]
CASES+=["T5_tracking","T5_tracking_2ns","T5_hold","T5_hold_mid","T6"]
FILES=["gds/tt_um_eleva_ccro_adc.gds","layout/integration/final_analog_c.spice","results/audited/interface_caps.spice",
       "rtl/adc_readout.v","layout/readout/adc_readout.nl.v","verification/dynamic.py","verification/a0.py",
       "tools/analyze_sndr.py","tools/vco_adc_model.py","results/release_gate.json"]
RELEASE="SKY26e_CCRO_ADC_1x2_Submission.zip"
RELEASE_SHA="eda8de0f78de6de2f11f341491d1ad6799b081cef817115cc4ef22c2271ccfa9"
BASE_MANIFEST_SHA="3c3cf46b87940eb1f1f270695d78d790458dae6b48ae3ef4f564f33f0376d123"
EXTRA_README="\n## 追加検証 T1〜T6\n\n完全同相起動、電源変動、過入力、微小入力ロック、デジタル異常系の判定と試作時の動作制限を収録した。[追加検証結果](docs/torture_T1-T6.md)\n".encode()
EXTRA_PDF="\n仕様表、回路図、最終GDSのレイアウト図、波形と改版課題を収録した。[詳細設計レポート](docs/ccro_adc_design_report.pdf)\n".encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def base_manifest():
    path=ROOT.parent/RELEASE
    if path.exists():
        assert sha(path.read_bytes())==RELEASE_SHA,"release archive changed"
        with ZipFile(path) as z: manifest=z.read("SHA256SUMS")
    else: manifest=(ROOT/"results/torture/original_submission.sha256").read_bytes()
    assert sha(manifest)==BASE_MANIFEST_SHA
    return manifest
def base_files():
    hashes={line[66:]:line[:64] for line in base_manifest().decode().splitlines()}
    members={}
    for name,expected in hashes.items():
        b=(ROOT/name).read_bytes()
        if name=="README.md":b=b.removesuffix(EXTRA_PDF).removesuffix(EXTRA_README)
        assert sha(b)==expected,name
        members[name]=b
    return members
def verify_input():
    base=base_files()
    return {name:sha(base[name]) for name in FILES}
def supply_budget(data):
    """Apply measured disturbance power to the specified 54-dB reference."""
    import numpy as np
    def paired(a,b):
        x,y=[np.asarray(record,dtype=float) for record in (a,b)]
        # Identical sample times. Remove DC and the coherent input tone. Double-sided
        # weights are common to interior bins; Nyquist has half their weight.
        ratio=np.abs(np.fft.rfft(y-x))**2
        ratio[[0,2]]=0
        ratio[-1]*=.5
        r=float(np.sum(ratio)/abs(np.fft.rfft(y)[2])**2)
        drop=float(10*np.log10(1+r*10**5.4))
        return dict(difference_to_tone_power_ratio=r,loss_from_54_dB=drop,projected_sndr_dB=54-drop)
    c,n=data["T3_clean"],data["T3_dirty"]
    phases=[]
    for a,b in zip(c["sample_phase_sweep"],n["sample_phase_sweep"],strict=True):
        assert a["offset_ns"]==b["offset_ns"]
        phases.append(dict(offset_ns=a["offset_ns"],quiet_dB=a["sndr_dB"],injected_dB=b["sndr_dB"],
                           quiet_to_injected_loss_dB=a["sndr_dB"]-b["sndr_dB"],**paired(a["codes"],b["codes"])))
    gate=data["T3_gate"]
    actual=dict(quiet_dB=gate["clean_sndr_dB"],injected_dB=gate["dirty_sndr_dB"],
        quiet_to_injected_loss_dB=gate["clean_sndr_dB"]-gate["dirty_sndr_dB"],**paired(gate["clean_codes"],gate["dirty_codes"]))
    all_pairs=[*phases,actual]
    return dict(target_dB=54,maximum_allowed_loss_dB=3,bins_excluded=[0,2],records_per_condition=16,
        reference_assumption="Disturbance in paired code differences adds in power to the nominal 54-dB noise and distortion budget.",
        phases=phases,routed_gate=actual,max_loss_from_target_dB=max(p["loss_from_54_dB"] for p in all_pairs),
        max_loss_from_measured_quiet_dB=max(p["quiet_to_injected_loss_dB"] for p in all_pairs),
        min_measured_injected_dB=min(p["injected_dB"] for p in all_pairs))
def report(data):
    t1=[data[c] for c in CASES if c.startswith("T1_")]
    t1ok=sum(v["status"]=="PASS" for v in t1)
    ref,ramp,brown,leak=[data["T2_"+s] for s in ("reference","ramp","brown","leak")]
    fast,slow=ref["tail"],ramp["tail"]
    err=max(abs(slow[k]/fast[k]-1) for k in ("fp_MHz","fn_MHz","vb_V"))
    ramp_ok=err<=.05 and slow["min_tap_MHz"]>0 and slow["min_swing_V"]>1.5
    t2ok=ramp_ok and brown["status"]==leak["status"]=="PASS"
    clean,dirty=data["T3_clean"],data["T3_dirty"]
    decrease=clean["sndr_dB"]-dirty["sndr_dB"]
    slip=min(v["min_excursion_cycles"] for v in dirty["lock_excursion"].values())
    phase_pairs=list(zip(clean["sample_phase_sweep"],dirty["sample_phase_sweep"],strict=True))
    min_dirty=min(b["sndr_dB"] for a,b in phase_pairs)
    worst_drop=max(a["sndr_dB"]-b["sndr_dB"] for a,b in phase_pairs)
    gate=data["T3_gate"]
    budget=data["T3_budget"]
    t3ok=budget["min_measured_injected_dB"]>=51 and budget["max_loss_from_target_dB"]<3 and slip>1
    step,ideal,series=[data["T4_"+s] for s in ("step","ideal","series")]
    hd0,hd1=ideal["hd3_dBc"],series["hd3_dBc"]
    lh0,lh1=[data["T4_literal_"+s]["hd3_dBc"] for s in ("ideal","series")]
    t4ok=step["status"]=="PASS" and max(hd1-hd0,lh1-lh0)<1
    v=data["T6"];r=v["rtl"];g=v["gates"]
    def maximum(rows,key):return max(x[key] for x in rows)
    t6ok=all(a[k] for a in (r,g) for k in ("reset_pass","bubble_pass","mode_pass"))
    def verdict(value):
        return "PASS" if value else "FAIL"

    summary = {"T1": verdict(t1ok == 10), "T2": verdict(t2ok),
               "T3": verdict(t3ok), "T4": verdict(t4ok),
               "T5": "5x margin unproven", "T6": verdict(t6ok)}
    if t3ok and budget["max_loss_from_measured_quiet_dB"] > 3:
        summary["T3"] = "Conditional"
    if any(data[k]["lock_indicator"] for k in ("T5_0_0", "T5_hold", "T5_tracking", "T5_tracking_2ns")):
        summary["T5"] = "FAIL"
    text = ["# Stress-test measurements on the released mask", "",
            "The analog results use extracted devices and capacitances. Digital results use RTL and the routed functional gate model. The supplied raw records retain their original numerical settings. [Case records](../results/torture) · [Waveform guide](../verification/design_report/waveform_guide.md)", "",
            "| Test | Verdict |", "|---|---|"]
    text.extend(f"| {key} | {value} |" for key, value in summary.items())
    text.extend(["", "## T1. Equal-node startup", "",
        "All 60 internal nodes started at 0.35 V without a kick, at 1.8 V and 27 °C with zero differential input. Each stage had to span 20–80% of its ring rail, settle at 180° ±15° and remain within 15% of the final period. The time below includes two consecutive qualifying periods. The cross-coupled devices are one fifth of the main inverter width. These ten runs include extracted asymmetry.", "",
        "| Corner | Bias | Maximum initial error (V) | Stages passing / 30 | Latest confirmation (periods) | Final phase error |",
        "|---|---|---:|---:|---:|---:|"])
    for case in t1:
        _, corner, bias = case["case"].split("_")
        banks = case["banks"].values()
        stages = [stage for bank in banks for stage in bank["stages"]]
        times = [stage["confirmed_cycles"] for stage in stages if stage.get("confirmed_cycles") is not None]
        angles = [abs(stage["final_phase_deg"] - 180) for stage in stages if stage.get("final_phase_deg", -1) >= 0]
        latest = f"{max(times):.2f}" if times else "—"
        angle = f"{max(angles):.2f}°" if angles else "—"
        text.append(f"| {corner.upper()} | {int(bias):02b} | {max(b['ic_error_V'] for b in banks):.2e} | {sum(s['pass_stage'] for s in stages)} | {latest} | {angle} |")
    text.extend(["", "## T2. Power ramp, brownout and leakage", "",
        "TT, 27 °C. The slow setting saw a 10 ms ramp to 1.8 V. The nominal setting saw a 50 µs hold at 0.6 V followed by a 10 ns recovery. Criteria were >1.5 Vpp on all taps and frequency and bias within 5% of the control.", "",
        "| Condition | P (MHz) | N (MHz) | vb (V) | Minimum tap swing (Vpp) |","|---|---:|---:|---:|---:|"])
    for name, result in (("1 µs slow control",fast),("10 ms slow ramp",slow),("Before dropout",brown["before"]),("During dropout",brown["during"]),("After recovery",brown["after"])):
        text.append(f"| {name} | {result['fp_MHz']:.5f} | {result['fn_MHz']:.5f} | {result['vb_V']:.5f} | {result['min_swing_V']:.3f} |")
    text.extend(["", f"Maximum ramp/control frequency or bias difference was {100*err:.3f}%. The 10.1 ms extracted run used a maximum 50 ns step and reltol 0.003. Its 1 µs control was cross-checked at reltol 0.0005. At FF, 85 °C, 1.98 V, per-device current probes measured the signed mean over whole ring periods. Both the 25 nA and 5% limits apply.", "", "| Bank | Sum of 39 off units (nA) | One on unit (nA) | Ratio |", "|---|---:|---:|---:|"])
    for name, bank in leak["banks"].items():
        text.append(f"| {name.upper()} | {bank['off_nA']:.3f} | {bank['on_nA']:.2f} | {bank['off_percent_actual']:.3f}% |")
    text.extend(["", "## T3. Simultaneous supply injection", "",
        f"Each rail included 5 Ω and 2 nH. Two 1 mA square waves ran at 20 MHz and 156.25 kHz. Input was 19.53125 kHz at −1 dBFS, sample rate 20 MHz, OSR 128. Local swing rose from {clean['local_supply_pp_mV']:.2f} to {dirty['local_supply_pp_mV']:.2f} mVpp. At the 25 ns sample phase the coherent 16-word SNDR loss was {decrease:.2f} dB.",
        "", f"Eight relative phases covered 0–43.75 ns. Minimum injected SNDR was {min_dirty:.2f} dB and maximum paired loss was {worst_drop:.3f} dB. Adding the paired disturbance power to a 54 dB reference budget gave a worst loss of {budget['max_loss_from_target_dB']:.3f} dB against a 3 dB limit. These two comparisons yield different verdicts.",
        "", f"Routed SPI yielded {gate['clean_sndr_dB']:.2f} dB clean and {gate['dirty_sndr_dB']:.2f} dB injected. The oracle matched over {gate['checked_clocks']} clocks per run. The first sticky flags occurred at ticks {gate['first_wrap_flag_tick']}. From tick 512 the peak counts were {gate['max_transition_count_after_tick_512']} against a threshold of 14.",
        "", "| Rail modulation frequency (MHz) | Clean (Hz) | Injected (Hz) | Injected (dBc) |","|---:|---:|---:|---:|"])
    for line, amp in dirty["freqline_amplitude_Hz"].items():
        text.append(f"| {float(line):g} | {clean['freqline_amplitude_Hz'][line]:.1f} | {amp:.1f} | {dirty['freqline_dBc'][line]:.2f} |")
    text.extend(["", f"For subharmonics 1/4 through 1/8 of 20 MHz and harmonics 16–33 of the output rate, the minimum excursion was {slip:.2f} cycles over 102.4 µs. This rules out continuous locking at those ratios over that window. The short coherent record resolves spurs; device-noise SNDR requires a long silicon capture.",
        "", "## T4. Overload, common-mode shift and input loading", "",
        f"After ±0.6 V differential overload the input returned to ±0.1 V. The slowest taps returned to within 5% of their final period after {step['recovery_cycles'][0]:.2f} and {step['recovery_cycles'][1]:.2f} periods. Limit 2 periods.",
        "", "| Interval | P (MHz) | N (MHz) | Minimum swing (Vpp) |", "|---|---:|---:|---:|"])
    conditions = ["+0.6 V","+0.1 V recovery","−0.6 V","−0.1 V recovery","Vcm 0.48 V","Vcm 0.78 V","Vcm 0.63 V recovery"]
    for name, result in zip(conditions,step["windows"],strict=True):
        text.append(f"| {name} | {result['fp_MHz']:.4f} | {result['fn_MHz']:.4f} | {result['min_swing_V']:.3f} |")
    text.extend(["", f"At TT, 27 °C, 50 kHz and ±0.20 V, 10 pF shunt per pin with 0 and 1.5 kΩ series resistance gave HD3 {hd0:.3f} and {hd1:.3f} dBc. Change {hd1-hd0:+.3f} dB. A second test put the capacitor in series and added a 100 MΩ DC return to 0.63 V per pin. HD3 was {lh0:.3f} and {lh1:.3f} dBc. The linear input network omits voltage-dependent switch resistance.",
        "", "## T5. Direct coupling and the 1 mV lock band", "",
        "Direct extracted rail coupling is 4.1989 fF. The mask has no added midpoint capacitor. The comparison adds a 10 × 10 µm, 206.58 fF MIM to ground. For startup at +1 mV, a response below 10% of 6.9 kHz/mV in the full 13–25 µs window and both halves indicates lock-like behavior.",
        "", "| Direct coupling change | Total fF | No midpoint MIM (kHz) | With MIM (kHz) | Lock-like, without / with |", "|---|---:|---:|---:|---|"])
    for c in ("removed",0,1,5,20,50):
        a,b = data[f"T5_0_{c}"],data[f"T5_1_{c}"]
        label = "Remove extracted capacitor" if c=="removed" else f"+{c} fF"
        text.append(f"| {label} | {a['total_direct_fF']:.4f} | {a['phase_fit_kHz']:+.4f} | {b['phase_fit_kHz']:+.4f} | {a['lock_indicator']} / {b['lock_indicator']} |")
    tracking = data["T5_tracking"]
    fine = data["T5_tracking_2ns"]
    text.extend(["", "The required 5× threshold is 20.9945 fF. A short-window sweep with the input present at startup cannot establish the physical threshold. For the long test, start at zero and apply +1 mV at 12 µs. Fit the relative phase over 18–178 µs. The expected linear beat is 1.104 cycles.", "",
        "| Zero-input startup | Fitted difference (kHz) | Relative phase span (cycles) | Lock-like |","|---|---:|---:|---|"])
    for name,key in (("As built","T5_hold"),("Midpoint MIM added","T5_hold_mid")):
        q=data[key]
        text.append(f"| {name} | {q['delta_kHz']:+.4f} | {q['relative_phase_span_cycles']:.4f} | {q['lock_indicator']} |")
    text.extend(["", f"With a supply-tracking input, changing only the solver step from 3 to 2 ns changed the 30-phase result from {tracking['phase_fit_kHz']:+.5f} to {fine['phase_fit_kHz']:+.5f} kHz. The single-tap edge estimator gave {tracking['delta_kHz']:+.5f} and {fine['delta_kHz']:+.5f} kHz. Startup history and timestep preclude a history-independent 5× claim. Locate the zero crossing on each die and sweep in both directions.",
        "", "## T6. Bubble errors, reset release and live changes", "",
        f"Seed {v['seed']}. Both RTL and routed gates ran {r['ticks']:,} clocks at 20 MHz with {r['bubble_count']} one-clock bubbles and {r['dbg_transitions']:,} debug changes. A triangular-weight CIC oracle compared each SPI clock. RTL and gate mismatches were {r['oracle_mismatched_ticks']} and {g['oracle_mismatched_ticks']}. {r['different_frame_words']} frames changed within the bubble response and {len(r['persistent_bad_frames'])} after it.",
        "", "The first integrator retained +2 after an isolated bubble. The second accumulated +762 over 381 clocks. Two decimated differences cancel the ramp under 21-bit modular arithmetic. Recovery of the output does not require a bubble-triggered reset.",
        "", "| Operation | Events | Latest CS start (clocks) | Latest word complete | Two-frame limit |", "|---|---:|---:|---:|---:|"])
    for name, events in (("Reset release",r["reset_events"]),("Live OSR change",r["mode_changes"])):
        for osr in (128,256):
            items=[e for e in events if e["osr"]==osr]
            if items:
                text.append(f"| {name}, OSR {osr} | {len(items)} | {maximum(items,'spi_start_clocks')} | {maximum(items,'spi_complete_clocks')} | {2*osr} |")
    text.extend(["", f"All {r['frames']} frames were checked for 16 bits, 64 clocks of CS low and four clocks between rising SCLK edges. Reset was released 1 ps before the rising clock edge. Functional gates do not quantify physical metastability. A live change waits for old-frame phase 97. Set OSR under reset and keep it fixed for acquisition.", "",
        "The analog model includes extracted capacitances, top-level tap coupling and 5 fF receiver loads. Distributed signal-net resistance and stochastic device noise remain outside these transient cases. The frozen archive contains the original per-case settings, wave hashes and comparison inputs.", ""])
    return "\n".join(text), summary

def main():
    checks=verify_input()
    out=ROOT/"results/torture"
    missing=[c for c in CASES if not (out/(c+".json")).is_file()]
    if missing:raise SystemExit("Missing cases: "+" ".join(missing))
    data={c:json.loads((out/(c+".json")).read_text()) for c in CASES}
    for c in CASES[:-1]:
        assert data[c]["pex_sha256"]==checks["layout/integration/final_analog_c.spice"],c
    gate=out/"T3_gate.json"
    if not gate.is_file() or any(json.loads(gate.read_text())["input_sha256"][c]!=data[c]["raw_sha256"] for c in ("T3_clean","T3_dirty")):
        from t3_gate import main as replay
        replay()
    data["T3_gate"]=json.loads(gate.read_text())
    budget=out/"T3_power_budget.json"
    data["T3_budget"]=supply_budget(data)
    budget.write_text(json.dumps(data["T3_budget"],indent=2,allow_nan=False)+"\n")
    txt,summary=report(data)
    md=ROOT/"docs/torture_T1-T6.md";md.write_text(txt,encoding="utf-8")
    man=out/"manifest.json"
    numerical=json.loads(man.read_text(encoding="utf-8")).get("simulation_inputs",{}) if man.exists() else {}
    if os.environ.get("PDK_ROOT"):
        pdk=(Path(os.environ["PDK_ROOT"])/"sky130A").resolve()
        rev=re.search(r"/versions/([0-9a-f]{40})/",pdk.as_posix()+"/")
        numerical={"pdk_release":rev[1] if rev else pdk.as_posix(),"files":{}}
        for name in ("libs.tech/ngspice/sky130.lib.spice","libs.tech/ngspice/spinit",
                     "libs.tech/ngspice/r+c/res_typical__cap_typical__lin.spice","libs.ref/sky130_fd_pr/spice/sky130_fd_pr__cap_mim_m3_1.model.spice",
                     "libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v","libs.ref/sky130_fd_sc_hd/verilog/primitives.v"):
            numerical["files"][name]=sha((pdk/name).read_bytes())
        iv=Path(os.environ.get("IVERILOG","/tmp/sky26e-ccro-tools/usr/bin/iverilog"))
        for name,path in (("ngspice",shutil.which("ngspice")),("iverilog",iv),("vvp",iv.parent/"vvp")):
            if path and Path(path).is_file():numerical["files"][name]=sha(Path(path).read_bytes())
    man.write_text(json.dumps(dict(release_sha256=RELEASE_SHA,input_sha256=checks,simulation_inputs=numerical,results=summary,case_count=len(CASES),additional_gate_replays=1),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    files=[md,man,gate,budget,*[out/(c+".json") for c in CASES],*[p for p in Path(__file__).parent.iterdir() if p.suffix in (".py",".v",".md",".sh")]]
    work=Path(os.environ.get("TORTURE_WORK","/tmp/ccro-torture-v1"))
    origins={c:data[c].get("measured_case",c) for c in CASES if c!="T6"}
    decks={f"decks/{c}/test.cir":(work/origins[c]/"test.cir").read_bytes() for c in CASES if c!="T6"}
    # Keep a single copy of each distinct core and identify it from every deck.
    index={}
    for c in CASES[:-1]:
        core=(work/origins[c]/"core.spice").read_bytes()
        name="decks/cores/"+sha(core)+".spice"
        decks[name]=core
        index[c]={"core_spice":name,"stimulus_sha256":sha(decks[f"decks/{c}/test.cir"]),
                  "binary_waveform_sha256":data[c]["raw_sha256"],"points":data[c]["stored_points"]}
    decks["decks/index.json"]=(json.dumps(index,indent=2)+"\n").encode()
    members=base_files()
    members["README.md"]+=EXTRA_README
    pdf=ROOT/"output/pdf/SKY26e_CCRO_ADC_Design_Report.pdf"
    if not pdf.exists():pdf=ROOT/"docs/ccro_adc_design_report.pdf"
    if pdf.exists():
        members["docs/ccro_adc_design_report.pdf"]=pdf.read_bytes()
        members["README.md"]+=EXTRA_PDF
    members["results/torture/original_submission.sha256"]=base_manifest()
    members.update({p.relative_to(ROOT).as_posix():p.read_bytes() for p in files})
    design=ROOT/"verification/design_report"
    members.update({p.relative_to(ROOT).as_posix():p.read_bytes() for p in design.iterdir() if p.suffix in (".py",".md",".tcl",".v",".cir")})
    for name in ("noise_terms.json","passives.txt","digital_current.csv","bias_tt_2.csv","bias_tt_3.csv","route_extent.json"):
        path=ROOT/"results/design_report"/name
        members[path.relative_to(ROOT).as_posix()]=path.read_bytes()
    members.update(decks)
    if "numerical_cross_check" in data["T2_ramp"]:
        for extra in ("T2_reference_alt","T2_ramp_alt"):
            f=out/(extra+".json")
            members[f.relative_to(ROOT).as_posix()]=f.read_bytes()
            members[f"decks/{extra}/test.cir"]=(work/extra/"test.cir").read_bytes()
    members["SHA256SUMS"]="".join(f"{sha(b)}  {name}\n" for name,b in sorted(members.items())).encode()
    archive=ROOT.parent/"SKY26e_CCRO_ADC_1x2_Submission_T1-T6.zip"
    with tempfile.NamedTemporaryFile(dir=archive.parent,suffix=".zip",delete=False) as f:tmp=Path(f.name)
    try:
        with ZipFile(tmp,"w",ZIP_DEFLATED) as z:
            for name,b in sorted(members.items()):write_member(z,name,b)
        with ZipFile(tmp) as z:
            assert z.testzip() is None and len(z.namelist())==len(members)
            for name,b in members.items():assert z.read(name)==b
        tmp.replace(archive)
    finally:tmp.unlink(missing_ok=True)
    print(sha(archive.read_bytes()),archive.name,summary)
def render_recorded_cases():
    """Regenerate the public report without repackaging the frozen submission."""
    out = ROOT / "results/torture"
    expected = json.loads((out / "manifest.json").read_text(encoding="utf-8"))["input_sha256"]
    for name in FILES:
        if sha((ROOT / name).read_bytes()) != expected[name]:
            raise ValueError(f"Input hash mismatch for {name}")
    data = {case: json.loads((out / (case + ".json")).read_text(encoding="utf-8"))
            for case in [*CASES, "T3_gate"]}
    for case in CASES[:-1]:
        if data[case]["pex_sha256"] != expected["layout/integration/final_analog_c.spice"]:
            raise ValueError(f"Analog extraction mismatch for {case}")
    data["T3_budget"] = supply_budget(data)
    body, _ = report(data)
    (ROOT / "docs/torture_T1-T6.md").write_text(body, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--report-only", action="store_true", help="Use the recorded simulation results")
    if parser.parse_args().report_only:
        render_recorded_cases()
    else:
        main()
