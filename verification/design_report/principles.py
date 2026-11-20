"""Vector teaching figures and a tap-to-SPI audit for the report."""
import csv
from functools import lru_cache
from pathlib import Path

from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from pdf_report import H, INK, MUTE, RULE, TEAL, WHITE, arrow


def equations(doc, *expressions):
    style = ParagraphStyle("formula", fontName="JP", fontSize=12, leading=20,
                           textColor=INK, splitLongWords=False)
    top = doc.y
    for expression in expressions:
        line = Paragraph(expression.replace("　", " &nbsp; "), style)
        width, height = line.wrap(495, 400)
        line.drawOn(doc.c, 54, H-doc.y-height-3)
        doc.y += height
    doc.rule(40, top+2, 40, doc.y+2, TEAL, 2.5)
    doc.y += 9


def data_rows(name):
    home = Path(__file__).resolve().parent
    folder = home.parent / "characterization"
    if not folder.is_dir():
        folder = home.parents[1] / "results/design_report/characterization"
    with (folder/name).open(newline="") as stream:
        return list(csv.DictReader(stream))


@lru_cache(maxsize=1)
def tap_record():
    raw = data_rows("step_taps.csv")
    assert [int(r["tick_50ns"]) for r in raw] == list(range(len(raw)))
    return [(int(r["p_hex"],16), int(r["n_hex"],16)) for r in raw]


def check_frames():
    taps = tap_record()
    x = [0] + [(a^b).bit_count()-(c^d).bit_count()
               for (a,c),(b,d) in zip(taps,taps[1:])]
    checked = {128:0, 256:0}
    example = None
    for row in data_rows("step_spi_words.csv"):
        rate = int(row["osr"])
        end = int(row["cs_end_tick"])
        last = end-99   # terminal +97 closes CS, raw taps reach delta two clocks later
        first = last-2*rate+2
        # Require a full post-reset window after synchronizer/configuration startup.
        if end <= 681 or first < 75+int(row["reset_delay_ticks"]):
            continue
        weighted = sum((rate-abs(j-rate+1))*x[last-j] for j in range(2*rate-1))
        code = weighted // (rate**2//2048)
        assert code == int(row["signed_code"]), (row, code)
        checked[rate] += 1
        if end==1059 and rate==128 and row["reset_delay_ticks"]=="0":
            example = first, last, weighted, code
    assert example == (706,960,16969,2121)
    assert checked == {128:47,256:20}
    return example


def flow(d):
    stages = [("v", "V", "0.100"),
              ("fP − fN", "MHz", "≈0.690"),
              ("mean(dP − dN)", "events / clk", "≈1.035"),
              ("C", "code", "≈2,120")]
    for i,(signal,unit,value) in enumerate(stages):
        x=40+i*133
        d.rect(x,8,112,58,"#eef5f6",RULE)
        d.txt(x+8,24,signal,10,"JB",TEAL)
        d.txt(x+8,45,value,15,"JB",INK)
        d.txt(x+8,60,unit,8,"JP",MUTE)
        if i<3: arrow(d,x+113,36,x+129,36)
    return 73


def differential(d):
    for x,s,node,gate in ((157,"sp","rp","VIN_N"),(425,"sn","rn","VIN_P")):
        d.txt(x-17,13,"VDPWR",8,"JB",MUTE)
        arrow(d,x,17,x,38)
        d.txt(x+8,31,"IB",10,"JP",TEAL)
        d.circle(x,43,2.8,TEAL)
        d.txt(x-21,47,s,11,"JB")
        d.rule(x,44,x,57,TEAL)
        d.rect(x-42,57,84,25,"#eef5f6",RULE)
        d.txt(x-32,73,"PMOS × 4",10,"JB")
        d.txt(x-116,73,gate,9,"JB",TEAL)
        arrow(d,x-80,69,x-44,69)
        arrow(d,x,83,x,101)
        d.txt(x+8,101,node,11,"JB")
    for a,b in ((157,196),(250,330),(385,425)):
        d.rule(a,43,b,43,TEAL)
    for x in (196,330):
        d.rect(x,35,55,16,WHITE,TEAL); d.txt(x+17,47,"RD",9,"JB")
    d.circle(290,43,2.4,TEAL); d.txt(279,32,"mid",9,"JB")
    return 109


def ring_edges(d):
    # Each delay is drawn at equal width. The two stages invert.
    x0, x1, unit = 108, 539, 11
    transitions=[(5,20,35),(5,20,35),(6,21,36)]
    for row,(name,start,edges) in enumerate(zip(("a[0]","b[0]","a[1]"),(0,1,1),transitions)):
        y=22+row*29
        d.txt(45,y+3,name,11,"JB")
        current=x0; high=start
        for e in edges:
            x=x0+unit*e
            d.rule(current,y-11*high,x,y-11*high,TEAL,1.6)
            d.rule(x,y-11*high,x,y-11*(1-high),TEAL,1.6)
            current=x; high=1-high
        d.rule(current,y-11*high,x1,y-11*high,TEAL,1.6)
    for e in (5,6,20,35):
        x=x0+e*unit
        d.rule(x,83,x,92,RULE,.8)
    x=x0+5*unit; z=x0+35*unit
    d.rule(x,94,z,94,MUTE);d.txt((x+z)/2-30,108,"T = 30 td",10,"JB")
    return 114


def tap_grid(d):
    taps=tap_record()
    assert taps[958:960] == [(0x555a,0x2aad),(0x52aa,0x2ad5)]
    x0=136
    for i in range(15):
        d.txt(x0+i*25+6,12,str(14-i),8,"JP",MUTE)
    for bank in range(2):
        a,b=taps[958][bank],taps[959][bank]
        for row,(prefix,word) in enumerate((("958",a),("959",b),("XOR",a^b))):
            y=16+bank*62+row*18
            d.txt(49,y+12,("P" if bank==0 else "N")+"   "+prefix,9,"JB")
            for i in range(15):
                bit=(word>>(14-i))&1
                color = (TEAL if row==2 else "#536d7a") if bit else "#f0f4f4"
                d.rect(x0+25*i,y,22,15,color)
                d.txt(x0+25*i+8,y+11,str(bit),8,"JB",WHITE if bit else MUTE)
            if row==2: d.txt(512,y+12,"= "+str(word.bit_count()),10,"JB",TEAL)
    return 140


def phase_steps(d):
    x0,dx,y0,dy=93,94,103,3.65
    for i in range(5):
        x=x0+i*dx
        d.rule(x,16,x,107,RULE,.55); d.txt(x-3,119,str(i),9,"JP",MUTE)
    d.txt(50,16,"q, Q",10,"JB")
    d.txt(x0+4*dx+15,119,"n",10,"JB")
    d.rule(x0,y0,x0+4*dx,y0-21*dy,"#a65028",1.4)
    # Plot the sampled, held integer phase, Q[0..4]=0,5,10,15,21.
    for i,(a,b) in enumerate(zip((0,5,10,15),(5,10,15,21))):
        x=x0+i*dx
        d.rule(x,y0-a*dy,x+dx,y0-a*dy,TEAL,1.7)
        d.rule(x+dx,y0-a*dy,x+dx,y0-b*dy,TEAL,1.7)
        d.circle(x+dx,y0-b*dy,2.1,TEAL)
        d.txt(x+dx-7,y0-b*dy-5,str(b),8,"JB")
    d.txt(95,13,"q(n) = 5.25 n",10,"JB","#a65028")
    d.txt(212,13,"Q[n] = floor(q(n))",10,"JB",TEAL)
    return 126


def triangle(d):
    x0,dx,y0,dy=98,59,82,14
    for k,h in enumerate((1,2,3,4,3,2,1)):
        x=x0+k*dx
        d.rect(x,y0-dy*h,28,dy*h,TEAL if k==3 else "#86b4b0")
        d.txt(x+10,y0-h*dy-4,str(h),10,"JB")
        d.txt(x+10,y0+15,str(k),9,"JP",MUTE)
    d.rule(76,y0,504,y0,MUTE,.8)
    d.txt(43,22,"h[k]",10,"JB");d.txt(509,y0+15,"k",10,"JB")
    return 105


def serial_word(d):
    _,_,_,code=check_frames()
    bits=f"{code:016b}"
    for i,bit in enumerate(bits):
        x=49+30*i+(i//4)*4
        d.txt(x+3,17,"D"+str(15-i),8,"JP",MUTE)
        d.rect(x,23,26,25,TEAL if bit=="1" else "#edf3f3")
        d.txt(x+9,40,bit,11,"JB",WHITE if bit=="1" else INK)
    for i,digit in enumerate(f"{code:04X}"):
        x=49+i*124
        d.rule(x,53,x+116,53,RULE,.8); d.txt(x+53,68,digit,11,"JB")
    return 77


DRAWINGS = dict(conversion=flow, differential=differential, ring_edges=ring_edges,
                tap_grid=tap_grid, phase_steps=phase_steps, triangle=triangle, serial_word=serial_word)
