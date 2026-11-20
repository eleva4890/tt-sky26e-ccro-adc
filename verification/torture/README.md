# Reproduce stress tests T1–T6

To regenerate the English measurement tables in this checkout, run `python3 verification/torture/report.py --report-only` with NumPy installed. The command validates the simulation inputs against their recorded hashes.

The frozen submission contains the original generated decks, per-case measurements and their hashes. Extract it separately for a byte-for-byte historical run. From that directory run `sha256sum -c SHA256SUMS`. The numerical testbench uses the same final extracted analog circuit and routed gate netlist as the current publication.

```bash
export PDK_ROOT=/path/to/model-pdk-root
export TORTURE_WORK=/tmp/ccro-torture-v1
python3 verification/torture/run_all.py --help
```

Use ngspice 42, Icarus Verilog 12, Python 3 with NumPy and the SKY130A model PDK at `8afc8346a57fe1ab7934ba5a6056ea8b43078e71`. Each case stores numerical settings, the time window, input checksums and measurements. The main suite covers 38 cases, with an additional routed-gate replay for supply injection. The fact that a simulation finished is separate from the test verdict. [Conditions and results](../../docs/torture_T1-T6.md)
