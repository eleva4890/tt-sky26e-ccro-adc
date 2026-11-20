"""Generate the mixed-signal schematic connection from the routed readout's port list."""
from pathlib import Path
import re
import sys

def header(subckt, name):
    m=re.search(r"^\.subckt "+name+r"\s+([^\n]*(?:\n\+[^\n]*)*)",subckt,re.M|re.I)
    if not m:
        raise ValueError(f"Missing subcircuit {name}")
    return m.group(1).replace("\n+"," ").split()

def build(digital, destination):
    pinmap={"VGND":"VGND","VPWR":"VDPWR","clk":"clk","cs_n":"uio_out[1]",
            "err_clr":"ui_in[5]","osr_sel":"ui_in[0]","rst_n":"rst_n","sclk":"uio_out[2]",
            "sdo":"uio_out[0]","wrap_err":"uio_out[3]","dbg_mode[0]":"ui_in[1]","dbg_mode[1]":"ui_in[2]"}
    pinmap.update({f"tap_{s}[{k}]":f"{s}{k}" for s in "pn" for k in range(15)})
    pinmap.update({f"debug[{k}]":f"uo_out[{k}]" for k in range(8)})
    extracted=Path(digital).read_text()
    order=header(extracted,"adc_readout")
    tie_order=header(extracted,"sky130_fd_sc_hd__conb_1")
    if len(tie_order)!=6 or set(tie_order)!={"VGND","VPWR","VNB","VPB","HI","LO"}:
        raise ValueError("Tie cell port mismatch")
    if set(order)!=set(pinmap) or len(order)!=len(pinmap):
        raise ValueError("Readout port mismatch")
    buses=["ui_in","uo_out","uio_in","uio_out","uio_oe","ua"]
    ports=["VDPWR","VGND","clk","ena","rst_n"]+[f"{bus}[{i}]" for bus in buses for i in range(8)]
    assert len(ports)==53
    text=["* Schematic binding for final layout and LVS. Supply pin order is explicit.",
          ".subckt tt_um_eleva_ccro_adc "+" ".join(ports),
          "Xana ua[0] ua[1] ui_in[3] ui_in[4] VDPWR VGND",
          "+ "+" ".join(f"{s}{i}" for s in "pn" for i in range(15))+" adc_analog",
          "Xdig "+" ".join(pinmap[n] for n in order)+" adc_readout"]
    low=[f"uio_out[{i}]" for i in range(4,8)]+[f"uio_oe[{i}]" for i in range(4,8)]
    high=[f"uio_oe[{i}]" for i in range(4)]
    for i,net in enumerate(low):
        hi=high[i] if i<len(high) else f"unused_hi{i}"
        pins={"LO":net,"HI":hi,"VPB":"VDPWR","VNB":"VGND","VGND":"VGND","VPWR":"VDPWR"}
        text.append(f"Xconst{i} "+" ".join(pins[p] for p in tie_order)+" sky130_fd_sc_hd__conb_1")
    for i in range(2):
        text.append(f"Xprotect_b{i} VGND ui_in[{i+3}] sky130_fd_pr__diode_pw2nd_05v5 perim=2.64e+06 area=4.347e+11")
    text.append(".ends tt_um_eleva_ccro_adc")
    Path(destination).write_text("\n".join(text)+"\n")
if __name__=="__main__":
    build(*sys.argv[1:])
