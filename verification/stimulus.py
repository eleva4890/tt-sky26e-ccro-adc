"""Generate pin-level stimuli and a numerical CIC/SPI oracle independent of the serial comb."""
import random
import sys

def generate(stream):
    rng=random.Random(2605)
    tap_p=tap_n=0
    phase=0
    samples=[]
    old1=old2=0
    next_word=0
    frame_start=-100
    rate=0
    done_block=False
    clear_pipe=[0,0]
    rate_pipe=[0,0]
    reset_pipe=[0,0]
    hist=[(0,0)]*3
    age=0
    wrap=0
    frames=0
    for tick in range(13800):
        reset=int(not (tick<6 or 10750<=tick<10758))
        select=int(4600<=tick<10600 or tick>=10800)
        mode=1 if tick%47<38 else (3 if tick%47<44 else 0)
        clear=int(tick%419 in range(275,283))
        if tick<1500 or 5100<tick<6800:
            dp,dn=15,0
        elif tick<3100 or 6800<=tick<8700:
            dp,dn=0,15
        else:
            dp,dn=rng.randrange(16),rng.randrange(16)
        for bit in rng.sample(range(15),dp):
            tap_p^=1<<bit
        for bit in rng.sample(range(15),dn):
            tap_n^=1<<bit
        # These pre-edge counts feed the synchronous integrator.
        def counts(pair,prev):
            return tuple((a^b).bit_count() for a,b in zip(pair,prev))
        pos,neg=counts(hist[1],hist[2])
        hist=[(tap_p,tap_n),hist[0],hist[1]]
        if not reset:
            reset_pipe=[0,0]
        running=reset_pipe[1]
        reset_pipe=[reset,reset_pipe[0]]
        if not running:
            age=0
            wrap=phase=rate=old1=old2=0
            done_block=False
            samples=[]
            frame_start=-100
            rate_pipe=clear_pipe=[0,0]
        else:
            delta=pos-neg if age>=4 else 0
            if clear_pipe[1]:
                wrap=0
            elif age>=4 and max(pos,neg)>=14:
                wrap=1
            age+=1
            if rate!=rate_pipe[1] and (not done_block or phase==97):
                rate=rate_pipe[1]
                phase=old1=old2=0
                done_block=False
                samples=[]
                frame_start=-100
            else:
                r=256 if rate else 128
                samples.append(delta)
                if phase==r-1:
                    # CIC2 impulse is triangular over 2R-1 input clocks.
                    newest=samples[-r:][::-1]
                    older=samples[-2*r:-r][::-1]
                    value=sum((i+1)*v for i,v in enumerate(newest))
                    value+=sum((r-1-i)*v for i,v in enumerate(older))
                    next_word=(value>>(5 if rate else 3))&65535
                    frame_start=tick+33
                    done_block=True
                    frames+=1
                    samples=samples[-r:]
                phase=(phase+1)%r
            rate_pipe=[select,rate_pipe[0]]
            clear_pipe=[clear,clear_pipe[0]]
        k=tick-frame_start
        active=0<=k<64
        sdo=(next_word>>(15-k//4))&1 if active else 0
        sclk=int(active and k%4>=2)
        pins=(wrap<<3)|(sclk<<2)|(int(not active)<<1)|sdo
        a,b=counts(hist[1],hist[2])
        debug=(a*16+b) if mode==1 and age>=4 else 0
        stream.write(f"{reset:x} {select:x} {clear:x} {mode:x} {tap_p:04x} {tap_n:04x} {pins:x} {debug:02x}\n")
    return frames

if __name__=="__main__":
    with open(sys.argv[1],"w") as stream:
        print(f"Checked stimulus contains {generate(stream)} completed decimation windows")
