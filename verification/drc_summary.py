"""Summarize KLayout marker counts without dropping repeated physical violations."""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
import sys
root=ET.parse(sys.argv[1]).getroot()
counts=Counter(item.findtext("category","").strip("'") for item in root.findall("./items/item"))
desc={c.findtext("name"):c.findtext("description","") for c in root.findall("./categories/category")}
for name,count in counts.most_common():
    print(f"{name:26} {count:6}  {desc.get(name,'')}")
print("TOTAL",sum(counts.values()))
