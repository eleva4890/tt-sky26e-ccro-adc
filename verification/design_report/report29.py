"""Typeset the page-wise Markdown master and original figures on a fixed A4 grid."""
import argparse
import json
import re
from pathlib import Path
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader
import os
import reportlab

font_dir = Path(reportlab.__file__).parent / "fonts"
os.environ.setdefault("REPORT_JP_FONT", str(font_dir / "Vera.ttf"))
os.environ.setdefault("REPORT_JP_BOLD", str(font_dir / "VeraBd.ttf"))
from pdf_report import Doc, H, W, INK, TEAL, MUTE, RULE, WHITE, lines, arrow
from PIL import Image
from xschem_figures import CircuitFigures
import principles
import bench_figures

HERE = Path(__file__).resolve().parent
BUNDLE = (HERE.parent/"figures/gds_tile.png").is_file()
PROJECT = HERE.parents[1]
ASSETS = HERE.parent/"figures" if BUNDLE else PROJECT/"results/design_report/figures"
AUDIT = HERE.parent/"baseline" if BUNDLE else PROJECT/"results"
BLUE, RED = "#28587d", "#993e32"
LEFT, RIGHT = 39, W-39
WIDTH = RIGHT-LEFT
TAGS = {"S":"SIGN-OFF","P":"PEX-SIM","G":"GATE-SIM","M":"MODEL-EST","T":"SILICON-TBD"}
TITLE = "SKY26e 1×2 Tile Differential CCRO-Based ADC — Pre-Silicon Design & Verification Report"

class Report(Doc):
    def __init__(self, path):
        super().__init__(path)
        self.c.setTitle(TITLE)
        self.circuits = CircuitFigures(self.c, ASSETS)

    def badges(self, right, y, keys):
        for key in reversed(keys.split()):
            name = "["+TAGS[key]+"]"
            width = stringWidth(name,"JB",7.05)+9
            self.rect(right-width,y-8.2,width,12.3,"#eaf1f1",RULE)
            self.txt(right-width+4.5,y+.4,name,7.05,"JB",INK)
            right -= width+4
        return right

    def page(self, part, name, title, keys, takeaway):
        if self.open:self.endpage()
        self.no+=1; self.open=True
        self.c.bookmarkPage("p"+str(self.no));self.c.addOutlineEntry(f"{self.no:02d}  {title}","p"+str(self.no),0)
        self.txt(LEFT,29,part+"  |  "+name,9,"JB",TEAL)
        self.right(RIGHT,29,"tt_um_eleva_ccro_adc / Rev 3.6",8,"JB",MUTE)
        self.rule(LEFT,38,RIGHT,38)
        self.badges(RIGHT,53,keys)
        title_size=min(21,21*WIDTH/stringWidth(title,"JB",21))
        self.txt(LEFT,83,title,title_size,"JB")
        if self.no==1 and not self.tutorial:
            self.txt(LEFT,105,"— Pre-Silicon Design & Verification Report",14,"JB",TEAL)
        self.y=self.p(LEFT,130 if self.no==1 and not self.tutorial else 108,takeaway,WIDTH,10.6,16,INK,"JB")+8

    def endpage(self):
        if self.y>797:raise ValueError(f"page {self.no} exceeds text frame: {self.y:.1f}")
        self.rule(LEFT,802,RIGHT,802)
        self.txt(LEFT,819,"SKY26e   /   DIFFERENTIAL CCRO ADC",7.7,"JB",MUTE)
        self.right(RIGHT,819,f"PRE-SILICON   /   {self.no:02d}  ·  {self.total_pages}",8,"JB",MUTE)
        self.c.showPage();self.open=False

    def band(self, title, keys):
        self.y+=10
        edge=self.badges(RIGHT,self.y,keys)
        assert LEFT+stringWidth(title,"JB",10.5)<edge-3,(self.no,title)
        self.txt(LEFT,self.y,title,10.5,"JB",TEAL)
        self.rule(LEFT,self.y+6,RIGHT,self.y+6)
        self.y+=12

    def grid(self, title, keys, widths, table):
        self.band(title,keys)
        fractions=list(map(int,widths.split(",")))
        widths=[WIDTH*w/sum(fractions) for w in fractions]
        destinations = {'Signoff decision': 2, 'Datasheet': 3, 'Circuit and layout': 9, 'Verification': 14, 'First silicon': 20, 'Schematics and data': 25}
        for idx,row in enumerate(table):
            if len(row)!=len(widths):raise ValueError((self.no,row))
            font="JP" if idx else "JB"
            wrapped=[lines(cell,w-12,font,8.7) for cell,w in zip(row,widths)]
            height=max(map(len,wrapped))*12.15+8
            self.rect(LEFT,self.y,WIDTH,height,INK if not idx else ("#eff4f3" if idx%2 else WHITE))
            x=LEFT
            for items,w in zip(wrapped,widths):
                for j,s in enumerate(items):
                    color=WHITE if not idx else (RED if s.startswith("FAIL") else INK)
                    self.txt(x+6,self.y+12+j*12.15,s,8.7,font,color)
                x+=w
            if self.no==1 and row[0] in destinations:
                self.c.linkRect("","p"+str(destinations[row[0]]),
                                (LEFT,H-self.y-height,RIGHT,H-self.y),relative=0,thickness=0)
            self.y+=height
        self.y+=8

    def note(self,title,body,safety=False):
        color=RED if safety else BLUE
        items=lines(body,WIDTH-24,"JP",9.3)
        height=28+14*len(items)
        self.rect(LEFT,self.y,WIDTH,height,"#fff6f2" if safety else "#f1f6fa",color)
        self.txt(LEFT+10,self.y+15,title,10,"JB",color)
        for j,s in enumerate(items):self.txt(LEFT+10,self.y+32+14*j,s,9.3)
        self.y+=height+9

    def paragraph(self,body):
        self.y=self.p(LEFT,self.y+8,body,WIDTH,9.6,15.4)+5

    def figure(self,title,keys,assets,height,caption):
        self.band(title,keys)
        height=float(height)
        names=assets.split(",")
        col=(WIDTH-12*(len(names)-1))/len(names)
        for i,name in enumerate(names):
            file=ASSETS/(name+".png")
            with Image.open(file) as im: iw,ih=im.size
            factor=min(col/iw,height/ih)
            dw,dh=iw*factor,ih*factor
            self.c.drawImage(ImageReader(str(file)),LEFT+i*(col+12)+(col-dw)/2,H-self.y-(height+dh)/2,dw,dh)
        self.y+=height+11
        self.y=self.p(LEFT,self.y,caption,WIDTH,8.45,12.1,MUTE)+5

    def drawing(self,title,keys,name,caption):
        self.band(title,keys)
        self.c.saveState(); self.c.translate(0,-self.y)
        height=DRAWINGS[name](self)
        self.c.restoreState(); self.y+=height+11
        self.y=self.p(LEFT,self.y,caption,WIDTH,8.45,12.1,MUTE)+5

    def jump(self,title,page):
        self.txt(LEFT,self.y+8,title,8.9,"JB",TEAL)
        self.c.linkRect("", "p"+page, (LEFT,H-self.y-12,LEFT+stringWidth(title,"JB",8.9),H-self.y+1),
                        relative=0,thickness=0)
        self.y+=18

    def link(self,title,url):
        self.txt(LEFT,self.y+8,title,8.9,"JB",TEAL)
        self.c.linkURL(url,(LEFT,H-self.y-12,RIGHT,H-self.y+2),relative=0,thickness=0)
        self.y+=19

def datapath(d):
    for i,(name,sub) in enumerate((("2-FF sync","15 taps per ring"),("XOR + count","dP, dN = 0…15"),("Subtract + CIC2","21 bit, 2 stages"),("SPI TX","16 bit, clk/4"))):
        x=LEFT+i*131
        d.rect(x,15,117,48,"#eaf3f3",RULE);d.txt(x+7,35,name,11,"JB");d.txt(x+7,52,sub,8.6)
        if i<3:arrow(d,x+117,39,x+130,39)
    return 79

def cover(d):
    im=ASSETS/"gds_tile.png"
    d.c.drawImage(ImageReader(str(im)),LEFT+12,H-230,158,221.54)
    for i,(val,lab) in enumerate((("15 / 15","Official shuttle precheck"),("−62.64 dBc","HD3 at TT, 50 kHz, with extracted tap loads"),("62.17 dB","SNDR for the central noise-model case"),("156.25 kS/s","Output rate at 20 MHz and OSR 128"))):
        y=34+i*55
        d.rule(252,y-22,RIGHT,y-22);d.txt(252,y,val,17,"JB",INK);d.txt(252,y+15,lab,8.8,"JP",MUTE)
    return 237

DRAWINGS={"digital":datapath,"cover":cover, **principles.DRAWINGS, "bench_compact":bench_figures.compact, **bench_figures.DRAWINGS}
STANDARDS=["Requirement","Simulation / check","Margin","Verdict"]

def render(path, tutorial=False):
    reg=json.loads((AUDIT/"release_gate.json").read_text())
    master=(HERE/("tutorial_sections.md" if tutorial else "report_sections.md")).read_text(encoding="utf-8")
    for key in ("gds_sha256","analog_pex_sha256"):
        master=master.replace("{{"+key+"}}",reg[key])
    doc=Report(path)
    doc.tutorial = tutorial
    if tutorial:
        doc.c.setTitle("SKY26e Differential CCRO ADC | Operating principles")
    schematics = []
    pages = re.split(r"(?m)^# ", master)[1:]
    doc.total_pages = 9 if tutorial else 29
    for page in pages:
        rows=[s.strip() for s in page.splitlines() if s.strip()]
        part,section,title,keys=rows[0].split(" | ")
        doc.page(part,section,title,keys,rows[1].strip("*"))
        i=2
        while i<len(rows):
            line=rows[i];i+=1
            if not line.startswith("<!--"):
                doc.paragraph(line);continue
            cmd,*args=[s.strip() for s in line[4:-3].split("|")]
            if cmd in ("table","verify"):
                table=[]
                while i<len(rows) and rows[i].startswith("|"):
                    row=[v.strip() for v in rows[i].strip("|").split("|")];i+=1
                    if not all(re.fullmatch(r"[-: ]+",v) for v in row):table.append(row)
                if cmd=="verify" and table[0]!=STANDARDS:table.insert(0,STANDARDS)
                doc.grid(args[0],args[1],args[2],table)
            elif cmd=="benchcmd":bench_figures.commands(doc,*args)
            elif cmd=="eq":principles.equations(doc,*args)
            elif cmd=="jump":doc.jump(*args)
            elif cmd=="fig":doc.figure(*args)
            elif cmd=="draw":doc.drawing(*args)
            elif cmd=="sheet":schematics.append(args)
            elif cmd in ("safe","note"):doc.note(args[0],args[1],cmd=="safe")
            elif cmd=="url":doc.link(*args)
            else:raise ValueError(line)
        if schematics:
            assert doc.no == 24 and not tutorial
            doc.circuits.appendix(doc, schematics)
            doc.no += len(schematics)
            schematics.clear()
            doc.c.setPageSize((W, H))
    assert doc.no == doc.total_pages
    doc.done()

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--out", type=Path)
    cli.add_argument("--tutorial", action="store_true", help="Build the separate nine-page operating-principles guide")
    args = cli.parse_args()
    directory = Path(".") if BUNDLE else PROJECT/"docs"
    filename = "tutorial.pdf" if args.tutorial else ("design_report.pdf" if BUNDLE else "ccro_adc_design_report.pdf")
    render(args.out or directory / filename, tutorial=args.tutorial)


if __name__ == "__main__":
    main()
