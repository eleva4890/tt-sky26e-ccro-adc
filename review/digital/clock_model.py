"""Translate only the PDK's functional low-transparent UDP into synthesizable HDL."""
import re, os
from pathlib import Path
pdk = Path(os.environ["PDK_ROOT"]) / "sky130A/libs.ref/sky130_fd_sc_hd/verilog"
models = (pdk / "sky130_fd_sc_hd.v").read_text()
blocks = re.findall(r"module sky130_fd_sc_hd__dlclkp_1\s*\(.*?endmodule", models, re.S)
src = next(b for b in blocks if "VPWR" not in b and "notifier" not in b and "udp_dlatch$P " in b)
primitive = (pdk / "primitives.v").read_text()
udp = re.search(r"primitive sky130_fd_sc_hd__udp_dlatch\$P\s*\(.*?endprimitive", primitive, re.S)[0]
assert re.search(r"1\s+1\s*:\s*\?\s*:\s*1",udp) and re.search(r"0\s+1\s*:\s*\?\s*:\s*0",udp) and re.search(r"\?\s+0\s*:\s*\?\s*:\s*-",udp), udp
src,n = re.subn(r"sky130_fd_sc_hd__udp_dlatch\$P\s+\w+\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*\);",r"always @* if (\3) \1 = \2;",src)
assert n == 1
src = re.sub(r"wire (m0\s*;)",r"reg \1",src)
Path("review/digital/clock_model.v").write_text(src+"\n")

