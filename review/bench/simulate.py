"""Run the SPICE emitted by Xschem, including legacy SKY130 symbol expressions."""
import re
import subprocess
import sys
from pathlib import Path

# Xschem 3.4.4 can emit the symbol's expr('... @W ... @nf ...') literally.
# Bind those two parameters on the same device card. ngspice evaluates the PDK
# formula, including int() and unit scaling, as a standard quoted expression.
EXPR = re.compile(r"expr\('([^'\n]*)'\)", re.I)
PARAM = re.compile(r"(?<!\S)(w|nf)=([^\s]+)", re.I)


def expand_card(match):
    card = match.group()
    values = {k.lower(): v for k, v in PARAM.findall(card)}

    def bind(expr):
        def instance_value(token):
            name = token[1].lower()
            if name not in values:
                raise ValueError(f"Unresolved {token[0]} in {card.split()[0]}")
            return "(" + values[name] + ")"

        return "'" + re.sub(r"@(\w+)", instance_value, expr[1]) + "'"

    return EXPR.sub(bind, card)


def main():
    deck = Path(sys.argv[1]).resolve()
    raw, log = (deck.with_suffix(ext) for ext in (".raw", ".log"))
    raw.unlink(missing_ok=True)
    text = deck.read_text()
    netlist = re.sub(r"(?im)^x[^\n]*\bsky130_fd_pr__\w*fet_\w+[^\n]*(?:\n\+[^\n]*)*", expand_card, text)
    if EXPR.search(netlist):
        raise ValueError("Unsupported unresolved symbol expression in Xschem netlist")
    ready = deck.with_suffix(".ngspice")
    ready.write_text(netlist)
    result = subprocess.run(["ngspice", "-b", "-o", log.name, ready.name], cwd=deck.parent)
    output = log.read_text(errors="replace")
    metrics = re.findall(r"(?im)^(?:fp_mhz|fn_mhz|delta_mhz|idd_ua) = [^\n]+", output)
    for line in metrics:
        print(line)
    print(f"Simulation log: {log}")
    if result.returncode or not raw.is_file() or len(metrics) != 4:
        raise SystemExit("Incomplete transient or missing measurements. Inspect the log and any available traces.")


if __name__ == "__main__":
    main()
