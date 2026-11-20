"""Extract the immutable review inputs and verify published hashes before use."""
import hashlib
import os
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARCHIVE_NAME = "SKY26e_CCRO_ADC_1x2_Submission_T1-T6.zip"
ARCHIVE = ROOT / "release" / ARCHIVE_NAME
if not ARCHIVE.is_file():
    ARCHIVE = ROOT.parent / ARCHIVE_NAME
ARCHIVE_HASH = "99ea0b138ca29e901c7b90f03a7e7ebcae2ff22461448c5a385148b60a98b36d"
GDS_HASH = "3d8a8502549ad4229debe27ae7c428059759af6e9657fcf2ff3c616e27a74d25"
digest = lambda data: hashlib.sha256(data).hexdigest()
for name in ["inputs", "logs", "xschem", "netlists", "digital"]:
    (HERE / name).mkdir(exist_ok=True)
assert digest(ARCHIVE.read_bytes()) == ARCHIVE_HASH
lines = [f"{ARCHIVE_HASH}  {ARCHIVE.name}"]
with zipfile.ZipFile(ARCHIVE) as archive:
    member = "gds/tt_um_eleva_ccro_adc.gds"
    data = archive.read(member)
    assert digest(data) == GDS_HASH
    assert (ROOT / member).read_bytes() == data, member
    (HERE / "inputs" / Path(member).name).write_bytes(data)
    lines.append(f"{GDS_HASH}  ZIP:{member}")
    for path in ("rtl/adc_readout.v", "layout/readout/adc_readout.nl.v", "analog/adc_analog_physical_lvs.spice",
                 "analog/top.spice", "layout/integration/top_floorplan.def", "layout/readout/adc_readout.lef",
                 "layout/analog_cells/eleva_adc_analog.lef","verification/check_io.py","verification/top_extract.tcl"):
        h = digest((ROOT / path).read_bytes())
        assert h == digest(archive.read(path)), path
        lines.append(f"{h}  ZIP + project: {path}")
pdk = Path(os.environ["PDK_ROOT"]) / "sky130A"
deck = pdk / "libs.tech/netgen/sky130A_setup.tcl"
lines.extend([f"{digest(deck.read_bytes())}  {deck.resolve()}", f"PDK {pdk.resolve()}"])
(HERE / "logs/input_hashes.txt").write_text("\n".join(lines) + "\n")
