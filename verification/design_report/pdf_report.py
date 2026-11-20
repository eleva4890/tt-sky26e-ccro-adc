"""Compose the Japanese design report. ReportLab, Pillow, and embeddable Japanese TTF/TTC fonts required."""
from pathlib import Path
import argparse, csv, json, os, re
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"results/torture"; ASSETS=ROOT/"results/design_report/figures"
for n,e,d in [("JP","REPORT_JP_FONT","C:/Windows/Fonts/meiryo.ttc"),("JB","REPORT_JP_BOLD","C:/Windows/Fonts/meiryob.ttc")]:
    pdfmetrics.registerFont(TTFont(n,os.environ.get(e,d),subfontIndex=0))
W,H=A4; LEFT=43; R=W-43; CW=R-LEFT
INK="#173641"; TEAL="#087c74"; MUTE="#4b6571"; RULE="#c5d6d5"; PALE="#f0f6f5"; GOLD="#a65332"; WHITE="#ffffff"
def obj(k):return json.loads((DATA/(k+".json")).read_text(encoding="utf-8"))
def rows(k):
    with (ROOT/"results/audited"/k).open(encoding="utf-8") as f:return list(csv.DictReader(f))
def lines(text,width,font,size):
    result=[]
    for para in str(text).split("\n"):
        current=""
        words=re.findall(r"(?:[−±+–]?\d+(?:[.,]\d+)*|[A-Za-zµ][A-Za-z0-9_]*|.)[。、，；）％%.,!?;:)]*",para)
        for word in words:
            # Very long identifiers can still wrap inside a narrow evidence column.
            parts=list(word) if pdfmetrics.stringWidth(word,font,size)>width else [word]
            for part in parts:
                if current and pdfmetrics.stringWidth(current+part,font,size)>width:
                    result.append(current.rstrip());current=""
                if current or not part.isspace():current+=part
        result.append(current.rstrip())
    return result

class Doc:
    def __init__(self,path):
        path.parent.mkdir(parents=True,exist_ok=True)
        self.c=canvas.Canvas(str(path),pagesize=A4,pageCompression=1,invariant=1)
        self.c.setTitle("SKY26e 1×2タイル 差動CCROベースADC　設計・実機評価マニュアル 第3版")
        self.c.setAuthor("SKY26e CCRO ADC design verification")
        self.no=0;self.open=False
    def txt(self,x,y,t,size=10,font="JP",color=INK):
        self.c.setFillColor(HexColor(color));self.c.setFont(font,size);self.c.drawString(x,H-y,str(t))
    def right(self,x,y,t,size=10,font="JP",color=INK):
        self.txt(x-pdfmetrics.stringWidth(str(t),font,size),y,t,size,font,color)
    def rule(self,x,y,x2,y2,color=RULE,w=1):
        self.c.setStrokeColor(HexColor(color));self.c.setLineWidth(w);self.c.line(x,H-y,x2,H-y2)
    def rect(self,x,y,w,h,fill=PALE,stroke=None):
        self.c.setFillColor(HexColor(fill));self.c.setStrokeColor(HexColor(stroke or fill));self.c.rect(x,H-y-h,w,h,stroke=int(bool(stroke)),fill=1)
    def circle(self,x,y,r,fill=INK,stroke=None):
        self.c.setFillColor(HexColor(fill));self.c.setStrokeColor(HexColor(stroke or fill));self.c.circle(x,H-y,r,stroke=int(bool(stroke)),fill=1)
    def p(self,x,y,t,width=None,size=10,leading=17,color=INK,font="JP"):
        for line in lines(t,width or CW,font,size):
            self.txt(x,y,line,size,font,color);y+=leading
        return y
    def sub(self,y,title):
        self.txt(LEFT,y,title,13,"JB",TEAL);return y+24
    def image(self,name,x,y,w,h):
        p=ASSETS/(name+".png")
        with Image.open(p) as im: iw,ih=im.size
        scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale
        self.c.drawImage(str(p),x+(w-dw)/2,H-y-dh,dw,dh,mask="auto")
        return y+dh
    def table(self,y,headers,data,widths,sz=8.6):
        assert abs(sum(widths)-CW)<1
        for i,row in enumerate([headers]+list(data)):
            wrapped=[lines(v,w-14,"JB" if i==0 else "JP",sz) for v,w in zip(row,widths)]
            height=max(28,max(map(len,wrapped))*(sz+4)+12)
            if y+height>786:raise ValueError(("table overflow",self.no,y,height,row))
            if i==0:self.rect(LEFT,y,CW,height,INK)
            elif i%2:self.rect(LEFT,y,CW,height,"#f2f6f5")
            x=LEFT
            for v,w in zip(wrapped,widths):
                for j,s in enumerate(v):self.txt(x+7,y+sz+8+j*(sz+4),s,sz,"JB" if i==0 else "JP",WHITE if i==0 else INK)
                x+=w
            y+=height
        self.rule(LEFT,y,R,y);return y+18
    def start(self,sec,title,deck):
        if self.open:self.endpage()
        self.no+=1;self.open=True
        self.c.bookmarkPage("p"+str(self.no));self.c.addOutlineEntry(title,"p"+str(self.no),0,False)
        self.txt(LEFT,37,"SKY26e   /   CCRO ADC",9,"JB",TEAL);self.right(R,37,sec,9,"JP",MUTE)
        self.rule(LEFT,47,R,47)
        self.txt(LEFT,90,title,24,"JB")
        self.p(LEFT,118,deck,size=10.3,leading=16,color=MUTE)
    def endpage(self):
        self.rule(LEFT,799,R,799)
        self.txt(LEFT,818,"tt_um_eleva_ccro_adc    •    製造前シミュレーション",8,"JP",MUTE)
        self.right(R,818,f"SKY130A   /   {self.no:02d}",8,"JB",MUTE)
        self.c.showPage();self.open=False
    def done(self):
        if self.open:self.endpage()
        self.c.save()
def arrow(d,x,y,x2,y2,color=TEAL):
    import math
    d.rule(x,y,x2,y2,color,1.2);a=math.atan2(y2-y,x2-x)
    for off in (-.53,.53):d.rule(x2,y2,x2-6*math.cos(a+off),y2-6*math.sin(a+off),color,1.2)
def box(d,x,y,w,h,title,detail):
    d.rect(x,y,w,h,PALE,RULE);d.txt(x+8,y+18,title,9.6,"JB");d.txt(x+8,y+34,detail,8,"JP",MUTE)
def mos(d,x,y,gate,pm=True,left=True):
    # Centered vertical source-drain channel, gate contact on either side.
    side=-1 if left else 1; gx=x+side*6
    d.rule(x,y-20,x,y-10,INK);d.rule(x,y+10,x,y+20,INK)
    d.rule(x,y-10,x+side*2,y-10,INK);d.rule(x+side*2,y-10,x+side*2,y+10,INK,2)
    d.rule(x,y+10,x+side*2,y+10,INK)
    d.rule(gx,y-10,gx,y+10,INK)
    if pm:d.circle(gx+side*3,y,2.5,WHITE,INK)
    d.rule(gx+side*(5 if pm else 0),y,gx+side*22,y,INK)
    if gate:
        if left:d.right(gx-25,y+3,gate,8,"JP")
        else:d.txt(gx+25,y+3,gate,8)
def resistor(d,x1,y,x2):
    unit=(x2-x1)/10
    pts=[(x1,y)]+[(x1+i*unit,y+(4 if i%2 else -4)) for i in range(1,10)]+[(x2,y)]
    for a,b in zip(pts,pts[1:]):d.rule(*a,*b,INK,1)
def ground(d,x,y):
    d.rule(x,y,x,y+5,INK);d.rule(x-8,y+5,x+8,y+5,INK);d.rule(x-5,y+8,x+5,y+8,INK);d.rule(x-2,y+11,x+2,y+11,INK)
def capacitor(d,x,y):
    d.rule(x,y,x,y+10,INK);d.rule(x-8,y+10,x+8,y+10,INK);d.rule(x-8,y+14,x+8,y+14,INK);d.rule(x,y+14,x,y+20,INK);ground(d,x,y+20)
def inv(d,x,y,w=31):
    for a,b in [((x,y-10),(x,y+10)),((x,y+10),(x+w-5,y)),((x+w-5,y),(x,y-10))]:d.rule(*a,*b,INK,1.2)
    d.circle(x+w-2.5,y,2.5,WHITE,INK)
def cover(d,reg):
    d.start("設計レポート・実機評価マニュアル　第3版","1×2タイル 差動CCROベースADC","SKY26e 向け初回試作　｜　差動15段CCRO・位相差分型読み出し")
    d.image("gds_tile",LEFT,166,242,350)
    d.txt(310,191,"差動入力を時間に変える",15,"JB")
    d.p(310,220,"入力電圧で左右リングに流す電流を変え、周波数差を30個の位相タップから読み取る。OSR 128の標準設定では、20 MHzのクロックから毎秒156,250個の符号付きコードを得る。",225,10.5,18)
    d.rule(310,350,R,350)
    d.txt(310,381,"−62.64 dBc",23,"JB",TEAL)
    d.txt(310,404,"外部タップ配線負荷込みのHD3",9,"JP",MUTE)
    d.txt(310,440,"TT・27 °C・50 kHz・差動±0.20 V",9,"JP",MUTE)
    d.txt(310,478,"15 / 15",20,"JB");d.txt(399,478,"公式precheck 合格",10)
    d.txt(LEFT,538,"最終GDSの選択マスク層。外形 161.00 × 225.76 µm。",8.3,"JP",MUTE)
    y=d.sub(588,"試作判定")
    d.p(LEFT,y,"最終GDSのDRC・LVS・アンテナ検査は合格した。性能は公称条件、外乱試験、実機で測る項目に分けて評価した。零点付近の感度と動作中のOSR切替には、標準動作域からは分からない制約がある。",size=11,leading=20)
    d.rect(LEFT,700,CW,60,PALE)
    d.txt(LEFT+13,722,"設計識別子",9,"JB",TEAL);d.txt(LEFT+105,722,"tt_um_eleva_ccro_adc",10,"JB");d.right(R-13,722,"2026年11月20日",8.5,"JP",MUTE)
    d.txt(LEFT+13,746,"GDS  SHA-256",8.5,"JB",MUTE);d.txt(LEFT+105,746,reg["gds_sha256"],7.2)
def specs(d,reg):
    d.start("仕様表","仕様と確認範囲","製造前に確認した設計値。電気特性には測定点と解析方法を併記した。")
    y=d.table(149,["項目","仕様・設計値","確認条件と結果"],[
      ("プロセス・占有枠","SKY130A、1×2タイル","161.00 × 225.76 µm。アナログ入力2本。"),
      ("電源・入力","公称1.80 V、評価端1.62 / 1.98 V","標準 Vcm=0.63 V、Vdiff=±0.20 V。"),
      ("標本化・出力レート","20 MHz、OSR 128 / 256","156.25 / 78.125 kS/s。32 MHzで配線後STA。"),
      ("発振周波数","公称 3.769 MHz","無入力・標準バイアス。FF・85 °Cの最高4.645 MHz。"),
      ("高調波歪み","HD2 ≤ −66、HD3 ≤ −62 dBc","配線負荷込みTT・50 kHzで−90.51 / −62.64 dBc。"),
      ("SNDR / ENOB","当初目標は実測>56 dB／>9 bit、モデル>60 dB","雑音予算は60.04〜63.12 dB。T3では別途、基準54 dB、許容悪化3 dB。実機は未測定。"),
      ("電流の代表値","TT無入力時アナログ42.86 µA","20 MHzデジタル約158 µA、コア計約201 µA。停止時と測定窓はp.30。"),
      ("コード・SPI","符号付き16 bit、Mode 0、MSB先頭","5 MHz SCLK。CSロー中に16回の立上り。"),
      ("設計余裕","32 MHzの外部負荷込み3コーナー","最小セットアップ +6.11 ns、最小ホールド +0.07 ns。")],
      [101,169,CW-270],8.6)
    y=d.sub(y+16,"接続と標準設定")
    y=d.table(y,["外部端子","用途"],[("ua[0] / ua[1]","VIN_P / VIN_N。0.63 Vを中心に ±Vdiff/2 で駆動。"),("ui_in[4:3]、[2:1]、[0]","バイアス、デバッグ、OSR。全ビット0で標準・静音・OSR 128。"),("uio[3:0]","上位からWRAP_ERR、SPI_SCLK、SPI_CS_N、SPI_SDO。"),("clk / rst_n","標本化クロックと非同期アサート・同期解除リセット。")],[170,CW-170],8.6)
    d.p(LEFT,y,"全端子・DBG_MODEはp.27、BIAS_SEL・fs下限はp.28、保護接続・通電はp.29、電流窓はp.30。16 bitは出力語長。",size=9,leading=14,color=MUTE)
def frontend(d):
    d.start("回路図　1 / 3","差動入力段と電流バイアス","実装の接続を素子単位で簡略表示した。回路網の全文は提出ZIPの抽出SPICEに収録した。")
    x1,x2=183,403
    d.rule(x1,175,x2,175,TEAL,1.4);d.txt(253,166,"VDPWR  1.8 V",9,"JB",TEAL)
    for x,dirleft,gb,inlab,side in [(x1,True,"VB / Gx","VIN_N","P"),(x2,False,"VB / Gx","VIN_P","N")]:
        d.rule(x,175,x,190,INK);mos(d,x,210,gb,True,dirleft);d.rule(x,230,x,280,INK)
        mos(d,x,300,inlab,True,dirleft);d.rule(x,320,x,359,INK);d.circle(x,249,2.4);d.circle(x,344,2.4)
        d.txt(x+8,241,"s"+side.lower(),9,"JB");d.txt(x+8,338,"r"+side.lower(),9,"JB",TEAL)
        xt=x+(-80 if dirleft else 80);d.rule(x,344,xt,344,INK);capacitor(d,xt,344)
        box(d,x-53,360,106,44,"15段 CCRO "+side,"rail = r"+side.lower())
    resistor(d,222,249,279);resistor(d,307,249,364);d.rule(x1,249,222,249,INK);d.rule(279,249,307,249,INK);d.rule(364,249,x2,249,INK)
    d.circle(293,249,2);d.txt(282,239,"mid",8);d.txt(223,272,"Rdeg/2",8);d.txt(314,272,"Rdeg/2",8)
    d.txt(54,424,"回路図 1",8.5,"JB",TEAL)
    d.p(110,424,"各側の上段は40個の単位PMOSを1・4・15・20個の群で制御する。下段の入力LVT PMOSは各側4並列。入力ゲートを交差させ、正の差動入力でP側の周波数が上がる。",428,8.7,15,color=MUTE)
    y=d.table(482,["素子 / ノード","物理実装"],[("単位電流源","PMOS W/L=1/2 µm。常時ONの1単位に3群を加算する。"),("標準／低速／中速／高速","BIAS_SEL=00／01／10／11に対し片側20／1／5／40単位。"),("入力PMOSと縮退抵抗","W/L=6/1 µmを4並列。sp・snからmidへ各L/W=80/0.69 µm。TT、27 °C、1 mVで各39.70 kΩ、直列79.40 kΩ。"),("リング電源容量","rp・rnから接地へ各21.8 × 21.8 µm。PDKのTTモデルを1 kHzで評価し、各964.85 fF（0.965 pF）。midは実装で追加MIMなし。"),("バイアス生成","基準抵抗は96.21 kΩ。βマルチプライヤと起動枝の接続・W/Lは次頁。")],[151,CW-151],8.7)
    d.p(LEFT,y+8,"ボディ接続は入力PMOSが各側のソース、電流源PMOSがVDPWR。抽出ネットのsp、sn、rp、rn、midは測定デッキと同名。",size=9.1,leading=15,color=MUTE)
def oscillator(d):
    d.start("回路図　3 / 3","発振段と位相読み出し","各リングは擬似差動15段。1周期に30回のタップ遷移を生じる。")
    for yy,lab,out in [(203,"a[k−1]","a[k]"),(316,"b[k−1]","b[k]")]:
        d.txt(55,yy+3,lab,9);d.rule(92,yy,140,yy,INK);inv(d,140,yy);d.rule(171,yy,303,yy,INK)
        d.txt(308,yy+3,out,9,"JB",TEAL)
    # Cross-coupled inverters use distinct branches with explicit net labels,
    # avoiding an ambiguous wire crossing in the schematic.
    for yy,src,dest in [(244,"b[k]","a[k]"),(276,"a[k]","b[k]")]:
        d.txt(141,yy+3,src,8, "JB",TEAL);d.rule(164,yy,187,yy,INK);inv(d,187,yy,23)
        d.rule(210,yy,245,yy,INK);d.txt(251,yy+3,dest,8,"JB",TEAL)
    d.txt(61,266,"弱帰還",8.5,"JB",MUTE)
    d.rule(352,169,352,347)
    tx=443;d.txt(410,166,"CMOS反転器",9,"JB",TEAL);d.txt(tx-7,190,"rail",8)
    d.rule(tx,195,tx,203,INK);mos(d,tx,223,"IN",True);mos(d,tx,277,"IN",False)
    d.rule(tx,243,tx,257,INK);d.circle(tx,250,2);d.rule(tx,250,tx+45,250,INK);d.txt(tx+48,253,"OUT",8);ground(d,tx,297)
    d.p(LEFT,354,"主反転器のPMOS/NMOS幅は8.4/4.2 µm。クロスカップルは1.68/0.84 µm、全てL=0.55 µm。各a[k]・b[k]から接地へ4.5 × 4.5 µmのMIMを1個（TT公称43.45 fF）。段14を段0へ戻す。PMOSウェルはVDPWR。",size=9.4,leading=17)
    d.sub(443,"30タップから16ビットコードまで")
    for x,tt,desc in [(LEFT,"CVSL × 30","1.8 Vにレベル変換"),(184,"2段同期＋XOR","前サンプルと比較"),(325,"popcount × 2","P、N各0〜15")]:
        box(d,x,466,122,43,tt,desc)
    arrow(d,LEFT+122,487,183,487);arrow(d,306,487,324,487)
    d.rule(447,487,500,487,TEAL);d.rule(500,487,500,529,TEAL);d.rule(104,529,500,529,TEAL);arrow(d,104,529,104,549)
    for x,tt,desc in [(LEFT,"dP − dN","符号付き5 bit"),(184,"CIC2・21 bit","OSR 128 / 256"),(325,"SPI・16 bit","clk/4・MSB先頭")]:
        box(d,x,550,122,43,tt,desc)
    arrow(d,165,571,183,571);arrow(d,306,571,324,571)
    d.p(LEFT,637,"標本ごとの遷移数の差を2段で積分し、間引き後の2段差分でコードを作る。OSR 128では[18:3]、256では[20:5]を取り出す。どちらも一定の差分±15に対し±30,720コード。",size=10,leading=18)
    d.p(LEFT,718,"WRAP_ERRは片側14遷移以上でラッチする。起動直後の4クロックは差分を0にマスクする。",size=9.4,color=MUTE)
