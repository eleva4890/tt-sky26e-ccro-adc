"""Write the release report from audited numeric evidence after the release gate passes."""
from release_gate import audit, rows, ROOT, A

def main():
    d=audit()
    m=rows(A/"front_mismatch.csv")
    offsets=[float(r["offset_mV"]) for r in m]
    caps=[float(r["external_metal_C_fF"]) for r in rows(A/"interface_caps.csv")]
    measured=d["loaded_diff_kHz_by_mV"]
    h=d["static_dynamic_delta_dB"]
    zero=next(r for r in rows(A/"final_small.csv") if float(r["diff_V"])==0)
    loaded={int(r["harmonic"]):float(r["relative_dBc"]) for r in rows(A/"final_loaded_dynamic.csv")}
    slow=rows(A/"final_slow.csv")[0]
    extra=rows(A/"final_loaded_fast.csv")[0]
    budget=d["noise_budget_range_dB"]
    code=d["mixed_frame_codes"]
    body=f"""# First-prototype signoff

The released SKY130A 1×2 tile is `tt_um_eleva_ccro_adc`, 161.00 × 225.76 µm with two analog inputs. Its GDS SHA-256 is `{d['gds_sha256']}`. The local physical signoff passed. Silicon characterization and shuttle acceptance are separate milestones.

## Physical and digital checks

| Check | Result and evidence |
|---|---|
| Precheck and full DRC | 17/17 passed. Magic DRC and KLayout BEOL DRC each reported zero violations. All 53 terminals matched the template. No met5 was used. [Precheck](../results/top_precheck.md) · [Full DRC](../results/top_drc.txt) |
| Top LVS and antenna | Netgen uniquely matched {d['devices']:,} devices and {d['nets']:,} nets. Zero antenna violations. [Top LVS](../results/top_lvs.txt) · [Antenna](../results/top_antenna.txt) |
| Connectivity | All 34 external signals and 30 phase taps connected, with zero shorted external-port groups. [Connectivity](../results/top_connectivity.txt) |
| Routed timing | Three corners at 32 MHz with digital SPEF, tile lumped loads and opposite switching on adjacent nets. Worst setup +{d['setup_ns']:.2f} ns and hold +{d['hold_ns']:.2f} ns. [Tile loads](../results/tile_loads.csv) · [Setup](../results/readout/tile_sta_max.log) · [Hold](../results/readout/tile_sta_min.log) |
| Digital regression | RTL and routed gates each ran 13,800 clocks and 70 frames, covering both rates, ±30,720 codes, reset, wrap and dividers. [Regression](../results/readout/final_functional.txt) |
| Analog through SPI | Replayed all 30 extracted taps through routed gates at 32 MHz. The second and third words at ±0.20 V were {code[1]:+d}, {code[2]:+d} and {code[4]:+d}, {code[5]:+d}. [SPI trace](../results/audited/final_spi.txt) |

## Harmonics

Nominal bias, Vcm = 0.63 V, ±0.20 V differential, 27 °C. The DC estimate uses a fifth-order Chebyshev fit on 11 points. The dynamic result uses the differential phase trajectory over two periods of a 50 kHz tone.

| Extracted condition | HD2 (limit −66 dBc) | HD3 (limit −62 dBc) |
|---|---:|---:|
| TT, 1.80 V, DC sweep | {d['HD_TT_static'][2]:.2f} dBc | {d['HD_TT_static'][3]:.2f} dBc |
| SS, 1.62 V, DC sweep | {d['HD_SS_static'][2]:.2f} dBc | {d['HD_SS_static'][3]:.2f} dBc |
| TT, 1.80 V, 50 kHz | {d['HD_TT_50kHz'][2]:.2f} dBc | {d['HD_TT_50kHz'][3]:.2f} dBc |
| Same sine with top-level tap coupling | {loaded[2]:.2f} dBc | {loaded[3]:.2f} dBc |

The first three conditions include a 5 fF receiver load per tap. At TT the HD3 static/dynamic difference is {h[3]:.2f} dB against a 1 dB bound. The HD2 difference is {h[2]:.2f} dB. A seventh-order fit to the same samples gives {d['HD2_degree7_TT_dBc']:.2f} dBc. First-lot HD2 acceptance uses the two amplitude limits. The last row adds {min(caps):.2f}–{max(caps):.2f} fF per tap with neighbors stationary and leaves {-62-loaded[3]:.2f} dB HD3 margin. [TT](../results/audited/final_tt.csv) · [SS](../results/audited/final_ss.csv) · [Loaded transient](../results/audited/final_loaded_dynamic.csv)

## Characterization limits

| Test | Evidence |
|---|---|
| A0 ring transfer | {d['PVT_points']} points spanning TT/SS/FF, −20/27/85 °C and 6.5–13.5 µA. Each corner and temperature was fit independently. [Coefficients](../results/audited/a0_pvt_fit.csv) |
| A1 startup | Autonomous nominal 1 µs ramp. Zero-input mean {d['zero_f0_MHz']:.3f} MHz and minimum internal differential swing {float(zero['min_internal_diff_pp_V']):.3f} Vpp. The full 1 ms ramp matrix and board startup remain open. |
| A2/A3 speed | Slow bias at SF, −20 °C, 1.98 V reached {d['slow_min_MHz']*1000:.2f} kHz minimum and {float(slow['duty_min'])*100:.2f}–{float(slow['duty_max'])*100:.2f}% duty. FF, 85 °C maxima were {d['fast_max_MHz']['nominal']:.3f} MHz nominal and {d['fast_max_MHz']['fast']:.3f} MHz fast, or {float(extra['fmax30_MHz']):.3f} MHz fast with top-level coupling. [Slow](../results/audited/final_slow.csv) · [Fast](../results/audited/final_loaded_fast.csv) |
| A5 noise | At 20 MHz, OSR 128, −1 dBFS, nine model cases gave {min(budget):.2f}–{max(budget):.2f} dB SNDR with 45.33 µV rms front-end noise and assumed ring FoM. Measure oscillator jitter and actual SPI SNDR on silicon. [Noise](../results/audited/front_noise.txt) · [Budget](../results/audited/final_noise_budget.csv) |
| A6 small signal | For −10, −3, −1, 0, +1, +3 and +10 mV, respectively, loaded TT differences were {', '.join(f'{measured[k]:+.3f}' for k in (-10,-3,-1,0,1,3,10))} kHz. Correct sign at ±10 mV. Near-zero behavior depends on history. [Sweep](../results/audited/final_loaded_small.csv) |
| A7 mismatch | Fifty front-end mismatch draws using a common fitted ring transfer yielded {min(offsets):+.2f} to {max(offsets):+.2f} mV equivalent offset. {d['front_mismatch_in_range']}/50 lay within the characterized current range. Full-circuit HD2 spread and yield remain open. [Draws](../results/audited/front_mismatch.csv) |

The extracted analog model includes the layout devices and mutual capacitances. Core metal is equipotential. Distributed wiring resistance, package parasitics and board supply feedback require additional characterization. Manufacturing PDK `6d4d11780c40b20ee63cc98e645307a9bf2b2ab8`. Analog model PDK `8afc8346a57fe1ab7934ba5a6056ea8b43078e71`. [Capacitance matrix](../results/final_analog_matrix.csv) · [Release gate](../results/release_gate.json) · [Bench manual](ccro_adc_design_report.pdf)
"""
    (ROOT/"docs/verification_status.md").write_text(body,encoding="utf-8",newline="\n")
if __name__=="__main__":main()
