"""Give NetlistSVG output an opaque page for dark-mode viewers and printing."""
import sys
import re
from pathlib import Path
for filename in sys.argv[1:]:
    p=Path(filename)
    src=p.read_text()
    opening,rest=src.split(">",1)
    w,h=map(int,re.search(r'width="(\d+)" height="(\d+)"',opening).groups())
    w,h=w+80,h+40
    opening=re.sub(r'width="\d+" height="\d+"',f'width="{w}" height="{h}" viewBox="-40 -20 {w} {h}"',opening)
    p.write_text(opening+f'>\n  <rect x="-40" y="-20" width="{w}" height="{h}" fill="white" stroke="none"/>\n'+rest)

