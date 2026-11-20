"""Express the schematic's two-terminal primitive instances in the extraction deck's syntax."""
import re
import sys
from pathlib import Path

extracted=Path(sys.argv[1]).read_text()
reference=Path(sys.argv[2])
text=reference.read_text()
for prefix,model in [("D","sky130_fd_pr__diode_pw2nd_05v5"),("R","sky130_fd_pr__res_generic_po")]:
    if not re.search(r"(?m)^"+prefix+r"\S*\s+\S+\s+\S+\s+"+model+r"\b",extracted):
        continue
    pattern=r"(?m)^X(\S+\s+\S+\s+\S+\s+"+model+r"\b[^\n]*)"
    def convert(m):
        line=prefix+"ref_"+m[1]
        return line.replace(" perim="," pj=") if prefix=="D" else line
    text,n=re.subn(pattern,convert,text)
    if not n: raise ValueError("No reference elements for "+model)
    print(model,n,"reference declarations changed to native",prefix)
reference.write_text(text)
