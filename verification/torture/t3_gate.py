"""Replay the two synchronized T3 tap streams through routed gates and decode the SPI waveforms."""
import csv, gzip, json, tempfile
from pathlib import Path
import numpy as np
from bench import OUT,ROOT,WORK,digest,raw
from t6 import Model,simulate

def sampled(name):
    w=raw(WORK/name/"waves.raw")
    th=(w["v(vdd)"]+w["v(vg)"])/2
    grid=(.025+np.arange(2688)*.05)*1e-6
    return [sum((np.interp(grid,w["time"],w[f"v({s}{i})"]-th)>0).astype(int)<<i for i in range(15)) for s in "pn"]
def sndr(codes):
    x=np.array(codes[-16:],dtype=float)
    p=np.abs(np.fft.rfft(x-x.mean()))**2;p[-1]*=.5
    return float(10*np.log10(p[2]/(p[1:].sum()-p[2])))
def main():
    fp={c:json.loads((OUT/(c+".json")).read_text())["raw_sha256"] for c in ("T3_clean","T3_dirty")}
    fp["routed_gates_sha256"]=digest(ROOT/"layout/readout/adc_readout.nl.v")
    signals=[sampled(c) for c in ("T3_clean","T3_dirty")]
    models=[Model(),Model()];expected=[]
    with tempfile.TemporaryDirectory() as tmp:
        work=Path(tmp)
        with (work/"vectors").open("w") as f:
            for k in range(2688):
                rst=int(k>=5)
                v=[[p[k],n[k]] for p,n in signals]
                f.write(" ".join(f"{a:x}" for a in [rst,0,0,*v[0],*v[1]])+"\n")
                expected.append([m.step(k,rst,0,*pins) for m,pins in zip(models,v)])
        trace=simulate(work,"gates").read_text().splitlines()
    assert len(trace)==len(expected)
    folder=ROOT/"results/design_report/waveforms";folder.mkdir(parents=True,exist_ok=True)
    words=[[],[]];shift=[0,0];prev=[2,2];count=[0,0];wrap_tick=[None,None]
    with gzip.open(folder/"T3_gate.csv.gz","wt",newline="") as f:
        write=csv.writer(f)
        write.writerow(["tick","sample_time_ns","clean_cs_n","clean_sclk","clean_sdo","dirty_cs_n","dirty_sclk","dirty_sdo"])
        for k,row in enumerate(trace):
            ix,ca,cb=row.split();v=[int(ca,16),int(cb,16)]
            assert int(ix)==k and [s&7 for s in v]==expected[k],(k,v,expected[k])
            write.writerow([k,50*k+30,*[bit for o in v for bit in ((o>>1)&1,(o>>2)&1,o&1)]])
            for j,(old,s) in enumerate(zip(prev,v)):
                if s&8 and wrap_tick[j] is None:wrap_tick[j]=k
                if old&2 and not s&2:shift[j]=count[j]=0
                if not s&2 and s&4 and not old&4:
                    count[j]+=1;shift[j]=2*shift[j]+(s&1)
                if not old&2 and s&2:
                    assert count[j]==16
                    words[j].append((shift[j]+32768)%65536-32768)
            prev=v
    assert all(len(v)>=16 for v in words)
    post_start_counts=[max((int(bank[k])^int(bank[k-1])).bit_count() for bank in pair for k in range(512,2688)) for pair in signals]
    result=dict(input_sha256=fp,checked_clocks=len(trace),complete_frames=[len(a) for a in words],
        clean_codes=words[0][-16:],dirty_codes=words[1][-16:],clean_sndr_dB=sndr(words[0]),
        dirty_sndr_dB=sndr(words[1]),sample_offset_ns=25,reset_release_tick=5,oracle_errors=0,
        first_wrap_flag_tick=wrap_tick,max_transition_count_after_tick_512=post_start_counts)
    (OUT/"T3_gate.json").write_text(json.dumps(result,indent=2)+"\n")
    print(result)
if __name__=="__main__":main()
