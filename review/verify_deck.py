"""Optional network provenance check against the pinned public Ciel release.
Run with Ciel's Python environment (zstandard) or any Python with zstandard.
"""
import hashlib, json, os, tarfile, urllib.request
from pathlib import Path
import zstandard

p=Path(__file__).resolve().parent
revision="8afc8346a57fe1ab7934ba5a6056ea8b43078e71"
manifest=f"https://fossi-foundation.github.io/ciel-releases/sky130/{revision}/manifest.json"
url=next(a["url"] for a in json.load(urllib.request.urlopen(manifest))["assets"] if a["content"]=="common")
with urllib.request.urlopen(url,timeout=90) as resp, zstandard.ZstdDecompressor().stream_reader(resp) as decoded, tarfile.open(fileobj=decoded, mode="r|") as tar:
    for member in tar:
        if member.name.endswith("sky130A/libs.tech/netgen/sky130A_setup.tcl"):
            original=tar.extractfile(member).read()
            break
    else: raise ValueError("Deck absent from distribution")
deck=Path(os.environ["PDK_ROOT"])/"sky130A/libs.tech/netgen/sky130A_setup.tcl"
assert deck.read_bytes()==original
(p/"logs/deck_provenance.txt").write_text(f"{manifest}\n{url}\n{member.name}\nSHA-256 {hashlib.sha256(original).hexdigest()}\nPASS byte-for-byte identical to installed comparison deck\n")

