"""Bench photographs, signal connections and calculated WaveForms timing examples."""
import csv
from math import pi, sin
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

from pdf_report import H, INK, MUTE, TEAL, WHITE

HERE = Path(__file__).resolve().parent
BUNDLE = (HERE.parent / "figures/bench_ad2.png").exists()
DATA = HERE.parent if BUNDLE else HERE.parents[1] / "results/design_report"
ORANGE = "#ae5731"
BLUE = "#286584"


def marker(doc, label, x, y, target_x, target_y):
    doc.rule(x,y,target_x,target_y,TEAL,1.3)
    doc.circle(target_x,target_y,2.4,WHITE,TEAL)
    doc.circle(x,y,7.5,TEAL)
    doc.txt(x-2.8,y+3,label,8,"JB",WHITE)


def equipment(doc):
    doc.txt(57,14,"Tiny Tapeout ETR v3.2",12,"JB")
    doc.txt(339,14,"Digilent Analog Discovery 2",12,"JB")
    # Both originals are shown uncropped, in the orientation published by their authors.
    for name,x,y,width,height in (("bench_etr32",69,22,193,210),("bench_ad2",337,25,204,204)):
        doc.c.drawImage(ImageReader(str(DATA/"figures"/(name+".png"))),
                        x,H-y-height,width,height,mask="auto")
    marker(doc,"1",76,36,168,38)     # top ANALOG header
    marker(doc,"2",264,200,166,209)  # center BIDIR
    marker(doc,"3",268,36,241,35)    # board USB-C
    marker(doc,"4",552,181,440,204)  # AD2 front flywire connector
    return 239


def wiremap(doc, insets=True):
    doc.txt(44,14,"ANALOG DISCOVERY 2",10,"JB",BLUE)
    doc.txt(236,14,"INTERFACE",10,"JB",MUTE)
    doc.txt(407,14,"TT ETR v3.2",10,"JB",TEAL)
    rows = [
        ("W1", "1 kΩ", "ANALOG / ua[0] / VIN_P", ORANGE, True),
        ("W2", "1 kΩ", "ANALOG / ua[1] / VIN_N", BLUE, True),
        ("GND", "common ground", "GND  /  J12 pin 5", MUTE, True),
        ("DIO 0", "level interface", "J12.1  /  b0  /  SDO", TEAL, False),
        ("DIO 1", "level interface", "J12.2  /  b1  /  CS_N", TEAL, False),
        ("DIO 2", "level interface", "J12.3  /  b2  /  SCLK", TEAL, False),
        ("DIO 3", "level interface", "J12.4  /  b3  /  WRAP_ERR", TEAL, False),
    ]
    for i,(lead,mid,pin,color,forward) in enumerate(rows):
        y=34+i*23
        doc.rect(42,y-13,509,21,"#f1f5f5" if i%2==0 else "#ffffff")
        doc.txt(50,y+1,lead,11,"JB",color)
        doc.rule(114,y-3,223,y-3,color,1.1)
        doc.rule(301,y-3,385,y-3,color,1.1)
        if lead=="GND":
            doc.rule(223,y-3,301,y-3,color,1.1)
        else:
            doc.rect(223,y-11,78,16,"#ffffff",color)
            doc.txt(246 if forward else 228,y+1,mid,9.3,"JB",color)
        if lead!="GND":
            x=385 if forward else 114
            d=-5 if forward else 5
            doc.rule(x,y-3,x+d,y-6,color,1.1)
            doc.rule(x,y-3,x+d,y,color,1.1)
        doc.txt(397,y+1,pin,9.5,"JB",INK)
    if not insets:
        return 186
    doc.txt(57,201,"AD2  /  flywire legend",10,"JB",BLUE)
    doc.txt(337,201,"ETR  /  BIDIR, b3 ... b0",10,"JB",TEAL)
    for name,box,x,y,width in (("bench_ad2",(152,451,450,560),56,207,180),
                               ("bench_etr32",(315,744,552,900),353,207,125)):
        with Image.open(DATA/"figures"/(name+".png")) as im:
            crop=im.crop(box)
            height=width*crop.height/crop.width
            doc.c.drawImage(ImageReader(crop),x,H-y-height,width,height,mask="auto")
    return 293


def wavegen(doc):
    x0,x1=98,532
    def y(v):
        return 110-(v-.63)*420
    for val in (.53,.63,.73):
        doc.rule(x0,y(val),x1,y(val),"#cdd9db",.7)
        doc.right(x0-10,y(val)+3,f"{val:.3f} V",9,"JP",MUTE)
    for sign,col,label in ((1,ORANGE,"W1 / VIN_P"),(-1,BLUE,"W2 / VIN_N")):
        path=doc.c.beginPath()
        for i in range(201):
            x=x0+(x1-x0)*i/200
            v=.63+sign*.10*sin(2*pi*i/200)
            if i==0:path.moveTo(x,H-y(v))
            else:path.lineTo(x,H-y(v))
        doc.c.setStrokeColor(HexColor(col));doc.c.setLineWidth(1.9);doc.c.drawPath(path)
        lx=115 if sign==1 else 304
        doc.rule(lx,31,lx+25,31,col,2)
        doc.txt(lx+30,34,label,10,"JB",col)
    for frac,t in ((0,"0"),(.25,"25"),(.5,"50"),(.75,"75"),(1,"100 µs")):
        x=x0+(x1-x0)*frac
        doc.txt(x-5,172,t,9,"JP",MUTE)
    return 185


def frame(doc):
    with (DATA/"characterization/step_spi_words.csv").open() as stream:
        row=next(r for r in csv.DictReader(stream)
                 if (r["osr"],r["reset_delay_ticks"],r["cs_start_tick"])==("128","0","995"))
    word=int(row["signed_code"])
    assert word==2121 and int(row["cs_end_tick"])==1059
    bits=f"{word & 0xffff:016b}"
    x0,dx=99,26
    def wave(values,baseline,color):
        prev=values[0]
        for j,v in enumerate(values):
            x=x0+(j-4)*dx/4
            doc.rule(x,baseline-15*prev,x,baseline-15*v,color,1.3)
            doc.rule(x,baseline-15*v,x+dx/4,baseline-15*v,color,1.3)
            prev=v
    for k in range(5):
        x=x0+k*4*dx
        doc.rule(x,36,x,148,"#d4dfe2",.7)
    for n in range(4):
        doc.txt(x0+dx*(n*4+1.8),24,f"{(word >> (12-4*n)) & 15:X}",12,"JB",INK)
    doc.txt(43,26,"HEX",9,"JB",MUTE)
    for y,name,vals,col in (
        (69,"CS_N",[1]*4+[0]*64+[1]*4,TEAL),
        (102,"SCLK",[0]*4+[0,0,1,1]*16+[0]*4,BLUE),
        (137,"SDO",[0]*4+[int(b) for b in bits for _ in range(4)]+[0]*4,ORANGE)):
        doc.txt(42,y-4,name,10,"JB",col)
        wave(vals,y,col)
    for j,b in enumerate(bits):
        x=x0+dx*(j+.5)
        doc.circle(x,87,1.9,BLUE)
        doc.txt(x-2.7,155,b,8,"JP",INK)
    doc.txt(x0-4,175,"0",9,"JP",MUTE)
    doc.right(x0+16*dx+15,175,"3.2 µs",9,"JP",MUTE)
    return 186


def commands(doc,*entries):
    width=514
    height=12+len(entries)*13
    doc.rect(39,doc.y,width,height,"#eff4f4")
    for i,entry in enumerate(entries):
        assert doc.c.stringWidth(entry,"Courier",8.5) < width-18, entry
        doc.txt(48,doc.y+13+13*i,entry,8.5,"Courier",INK)
    doc.y+=height+8


DRAWINGS={"bench_gear":equipment,"bench_wires":wiremap,"bench_inputs":wavegen,"bench_frame":frame}

def compact(doc):
    """Stack the credited equipment views and direction diagram on one bench page."""
    c = doc.c
    for draw, scale, y in ((equipment, .68, 0), (lambda d: wiremap(d, insets=False), .91, 168)):
        c.saveState()
        c.translate((1-scale)*297.64, (1-scale)*H-y)
        c.scale(scale, scale)
        draw(doc)
        c.restoreState()
    return 339
