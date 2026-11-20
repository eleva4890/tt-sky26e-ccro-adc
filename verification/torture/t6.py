"""Generate ordered ring phases, drive both DUTs, and check the serialized triangular CIC response."""
from pathlib import Path
import csv, gzip, json, os, random, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[2]
SEED=260611
TICKS=27200
RESET=[(0,5),(12521,12524),(16005,16009),(19004,19010)]

class Model:
    def __init__(self):
        self.reset=[0,0]
        self.tap=[(0,0)]*3
        self.rate_pipe=[0,0]
        self.clear()
    def clear(self):
        self.rate=self.phase=self.age=0
        self.active=False
        self.samples=[]
        self.start=-100
        self.word=0
        self.rate_pipe=[0,0]
    def step(self,tick,rst,sel,p,n):
        if not rst:self.reset=[0,0]
        running=self.reset[1]
        self.reset=[rst,self.reset[0]]
        older,previous=self.tap[1:]
        v=(older[0]^previous[0]).bit_count()-(older[1]^previous[1]).bit_count()
        self.tap=[(p,n)]+self.tap[:2]
        if not running:self.clear()
        else:
            if self.age<4:v=0
            self.age+=1
            if self.rate!=self.rate_pipe[1] and (not self.active or self.phase==97):
                self.rate=self.rate_pipe[1]
                self.phase=0
                self.active=False
                self.samples=[]
                self.start=-100
            else:
                r=128<<self.rate
                self.samples.append(v)
                if self.phase==r-1:
                    block=self.samples[-r:][::-1]
                    prev=self.samples[-2*r:-r][::-1]
                    value=sum((j+1)*a for j,a in enumerate(block))+sum((r-1-j)*a for j,a in enumerate(prev))
                    self.word=(value>>(5 if self.rate else 3))&65535
                    self.samples=self.samples[-r:]
                    self.start=tick+33
                    self.active=True
                self.phase=(self.phase+1)%r
            self.rate_pipe=[sel,self.rate_pipe[0]]
        pos=tick-self.start
        if not 0<=pos<64:return 2
        return (int(pos%4>=2)<<2)|((self.word>>(15-pos//4))&1)

def generate(work):
    rng=random.Random(SEED)
    clocks=[]
    models=[Model(),Model()]
    bubble=[]
    mode_events=[]
    last=-1000;s=0;tap=[0,0];ptr=[0,0];dbg=0
    target_phases=[39,105,18,100,119,102,71,99,51,110,80,106,37,101,29,110,95,100]
    rate_rng=random.Random(SEED+1)
    target_phases.extend(rate_rng.randrange(2,126) for _ in range(8))
    mode_i=0
    with (work/"vectors").open("w") as f:
        for t in range(TICKS):
            rst=int(not any(a<=t<b for a,b in RESET))
            if 7900<t<TICKS-650 and mode_i<len(target_phases) and t-last>610 and models[0].active and models[0].phase==target_phases[mode_i] and all(abs(t-b)>600 for _,b in RESET[1:]):
                s^=1;mode_i+=1;last=t;mode_events.append((t,s))
            if rng.random()<.035: dbg=rng.choice([d for d in range(4) if d!=dbg])
            for bank in range(2):
                advance=rng.choices([0,1,2,3,4],[2,20,40,30,8])[0]
                if t==7380 and bank==0:advance=0
                for _ in range(advance):
                    tap[bank]^=1<<ptr[bank];ptr[bank]=(ptr[bank]+1)%15
            noisy=tap.copy()
            if (500<t<7350 and (not bubble or t-bubble[-1]>5) and rng.random()<.033
                and t%1000<260):
                bank=rng.randrange(2)
                bit=(ptr[bank]+rng.choice([-2,-1,0,1]))%15
                noisy[bank]^=1<<bit;bubble.append(t)
            if t==7380:
                # One isolated toggle on the last transitioned tap followed by
                # its return, with no true transition on that tap at either clock.
                noisy[0]^=1<<((ptr[0]-1)%15);bubble.append(t)
            f.write(" ".join(f"{v:x}" for v in [rst,s,dbg,*tap,*noisy])+"\n")
            expected=[m.step(t,rst,s,*v) for m,v in zip(models,[tap,noisy])]
            clocks.append((expected,models[0].rate,dbg))
    return clocks,bubble,mode_events

def analyze(path,clocks,bubbles,changes):
    frames=[];mismatches=[];bad=0;word=[0,0];edges=0;old=2;last_edge=-1
    max_acc_diff=0;acc_after=None;directed={};second={};errors=[];start=None
    for t,row in enumerate(path.read_text().splitlines()):
        v=row.split();assert int(v[0])==t
        sig=[int(x,16) for x in v[1:3]]
        expected,rate,_=clocks[t]
        if sig!=expected:
            bad+=1
            if len(mismatches)<5:mismatches.append([t,sig,expected])
        if (sig[0]&6)!=(sig[1]&6):errors.append([t,"different clock/CS"])
        if len(v)>3 and "x" not in "".join(v[3:]):
            diff=(int(v[4],16)-int(v[3],16)+2**20)%2**21-2**20
            max_acc_diff=max(max_acc_diff,abs(diff))
            if t in (7379,7399,7780):
                directed[str(t)]=diff
                second[str(t)]=(int(v[6],16)-int(v[5],16)+2**20)%2**21-2**20
            if t==7780:acc_after=diff
        cs=sig[0]&2;oldcs=old&2
        if oldcs and not cs:start=t;edges=0;word=[0,0]
        if not cs and sig[0]&4 and not old&4:
            if edges and t-last_edge!=4:errors.append([t,"SCLK spacing"])
            last_edge=t;edges+=1
            word=[(w<<1)|(x&1) for w,x in zip(word,sig)]
        if cs and not oldcs:
            if any(a<=t<b for a,b in RESET):start=None
            elif edges!=16 or t-start!=64:errors.append([t,"malformed packet"])
            else: frames.append((start,t,rate,*word))
        old=sig[0]
    assert t+1==len(clocks)
    ref=[(b,128<<clocks[b+5][1]) for _,b in RESET]
    def recovery(t,r):
        packet=next(x for x in frames if x[0]>=t and (128<<x[2])==r)
        return dict(tick=t,osr=r,spi_start_clocks=packet[0]-t,spi_complete_clocks=packet[1]-t,limit_clocks=2*r)
    mode=[recovery(t,128<<sel) for t,sel in changes]
    resets=[recovery(t,r) for t,r in ref]
    # Intervals of >=2R input clocks free of bubbles, allowing one R-word
    # serialization latency. Also count differing values outside proven CIC support.
    bad_persistent=[];diff_words=0;long_clean=0;max_age=0
    for st,en,r,clean,noisy in frames:
        last_b=max((b for b in bubbles if b<st),default=-10000)
        age=st-last_b
        if st>500 and st<7400 and age>2*(128<<r)+36:long_clean+=1
        if clean!=noisy:
            diff_words+=1;max_age=max(max_age,age)
            if age>2*(128<<r)+36:bad_persistent.append(st)
    passes=lambda rows: all(a["spi_complete_clocks"]<=a["limit_clocks"] for a in rows)
    return dict(ticks=len(clocks),frames=len(frames),oracle_mismatched_ticks=bad,first_mismatches=mismatches,
        malformed=errors[:6],malformed_count=len(errors),different_frame_words=diff_words,
        quiet_recovered_frames=long_clean,persistent_bad_frames=bad_persistent,max_age_of_affected_frame_at_CS_clocks=max_age,
        peak_internal_acc1_difference_counts=max_acc_diff if acc_after is not None else None,
        internal_acc1_difference_after_last_burst=acc_after,directed_acc1_difference=directed,
        directed_acc2_difference=second,
        bubble_count=len(bubbles),mode_changes=mode,
        reset_events=resets,dbg_transitions=sum(a[2]!=b[2] for a,b in zip(clocks,clocks[1:])),
        bubble_pass=not bad_persistent and diff_words>0 and long_clean>0 and bad==0,
        reset_pass=passes(resets) and bad==0,mode_pass=passes(mode) and not errors and bad==0)

def simulate(work,tag):
    pdk=Path(os.environ["PDK_ROOT"])/"sky130A/libs.ref/sky130_fd_sc_hd/verilog"
    iv=Path(os.environ.get("IVERILOG","/tmp/sky26e-ccro-tools/usr/bin/iverilog"))
    vvp=iv.parent/"vvp"
    args=[str(iv),"-g2012","-s","t6_tb","-o",str(work/"sim")]
    base=os.environ.get("IVERILOG_BASE","/tmp/sky26e-ccro-tools/usr/lib/x86_64-linux-gnu/ivl")
    if Path(base).is_dir():args+=["-B",base]
    if tag=="rtl":args+=[ROOT/"rtl/adc_readout.v"]
    else:args+=["-DNETLIST","-DFUNCTIONAL","-DUNIT_DELAY=#0.1",pdk/"primitives.v",pdk/"sky130_fd_sc_hd.v",ROOT/"layout/readout/adc_readout.nl.v"]
    subprocess.run([*args,Path(__file__).with_name("t6_tb.v")],check=True)
    output=work/(tag+".out")
    subprocess.run([str(vvp),str(work/"sim"),"+SRC="+str(work/"vectors"),"+OUT="+str(output)],check=True)
    return output

def main():
    with tempfile.TemporaryDirectory() as temp:
        work=Path(temp)
        clocks,bubbles,changes=generate(work)
        result={}
        for tag in ("rtl","gates"):
            output=simulate(work,tag)
            result[tag]=analyze(output,clocks,bubbles,changes)
        wave_dir=ROOT/"results/design_report/waveforms";wave_dir.mkdir(parents=True,exist_ok=True)
        with gzip.open(wave_dir/"T6_gate.csv.gz","wt",newline="") as stream:
            writer=csv.writer(stream)
            writer.writerow(["tick","sample_time_ns","rst_n","osr_sel","dbg_mode","tap_p","tap_n","bubble_p","bubble_n",
                             "clean_cs_n","clean_sclk","clean_sdo","bubble_cs_n","bubble_sclk","bubble_sdo","bubble_wrap"])
            for line,vec in zip((work/"gates.out").read_text().splitlines(),(work/"vectors").read_text().splitlines(),strict=True):
                ix,ca,cb=line.split();t=int(ix);a=int(ca,16);b=int(cb,16)
                writer.writerow([t,50*t+30,*[int(x,16) for x in vec.split()],(a>>1)&1,(a>>2)&1,a&1,(b>>1)&1,(b>>2)&1,b&1,b>>3])
        result["seed"]=SEED
        result["status"]="PASS" if all(result[x][k] for x in ("rtl","gates") for k in ("bubble_pass","reset_pass","mode_pass")) else "FAIL"
        out=ROOT/"results/torture";out.mkdir(parents=True,exist_ok=True)
        (out/"T6.json").write_text(json.dumps(result,indent=2)+"\n")
        print(result["status"],[(k,result[k]["first_mismatches"],result[k]["malformed"]) for k in ("rtl","gates")])
if __name__=="__main__": main()
