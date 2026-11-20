"""Pin reference and first-silicon procedures, with the characterization conditions on each page."""
import csv
import json
from pdf_report import ROOT, LEFT, R, CW, H, MUTE, TEAL, INK, PALE, obj

DATA = ROOT/"results/design_report"

def pins(d):
    d.start("実機評価　端子表","端子の方向と設定値","信号名はタイル側から見たもの。バスの左端が上位ビット。PMODの物理ピン番号は使用する基板の回路図で照合する。")
    y=d.table(148,["端子","方向","割当・初期設定"],[
        ("VDPWR / VGND","電源","1.80 Vコア電源／基準GND。VAPWRは使用しない。"),
        ("ua[0] / ua[1]","アナログ入力","正入力VIN_P／負入力VIN_N。ua[7:2]はタイルで未使用。本品の外部アナログ接続は2本。"),
        ("clk / rst_n / ena","入力","clkは標本化クロック。rst_nはLowでリセット。enaはシャトルの選択信号で、タイル内部の停止制御には使わない。"),
        ("ui_in[0] / [2:1] / [4:3]","入力","OSR_SEL（0→128、1→256）／DBG_MODE／BIAS_SEL。初期値はすべて0。"),
        ("ui_in[5] / [7:6]","入力","[5] ERR_CLR。Highを3 clk以上保持してLowに戻す。[7:6]は未使用、基板で0に設定。"),
        ("uo_out[7:0]","出力","全8本をADCが駆動。各モードのビット割当を下表に示す。"),
        ("uio[0] / [1] / [2] / [3]","出力","順にSDO、CS_N、SCLK、WRAP_ERR。測定器側は入力。"),
        ("uio[7:4] / uio_in[7:0]","高インピーダンス／入力","上位4本はタイルからHi-Z。uio_inは全ビット未使用。内部uio_out[7:4]=0、uio_oe[7:0]=0000_1111。")],[143,87,CW-230],8.8)
    y=d.sub(y+5,"DBG_MODE = ui_in[2:1]")
    y=d.table(y,["値","uo_out[7:0]","観測の目的"],[
        ("00","全ビット0","通常変換・FFT。SPIはuioから取得。"),
        ("01","[7:4] dP、[3:0] dN","各0〜15、起動マスク中は0。生遷移数を観測。"),
        ("10","[7:2] 0、[1] N/64、[0] P/64","非同期分周。両周波数を同時に測る。"),
        ("11","全ビット0","静音。00と同じデバッグ出力。")],[58,206,CW-264],8.6)
    d.p(LEFT,y,"00・01・11では分周器へのタップクロックをゲートする。SPIとWRAP_ERRはデバッグ出力から独立する。",size=9,leading=15,color=MUTE)

def modes(d):
    d.start("実機評価　設定表","バイアスと標本化クロック","左右の発振器は外部クロックと独立して動く。f₀は無入力時の代表値。測定に使う最大周波数は、実個体の正負入力端でも確認する。")
    freq=[]
    for i in (2,3):
        with (DATA/f"bias_tt_{i}.csv").open() as f:
            row=next(csv.DictReader(f))
        freq.append((float(row["fp_MHz"])+float(row["fn_MHz"]))/2)
    slow=obj("T2_reference")["tail"]
    y=d.table(154,["BIAS_SEL","単位数／側","f₀　MHz","初期 fs","差動入力の目安¹"],[
        ("00 標準","20","3.769","20 MHz","±0.20 V"),
        ("01 低速","1",f"{(slow['fp_MHz']+slow['fn_MHz'])/2:.3f}","1 MHz","±35 mV"),
        ("10 中速","5",f"{freq[0]:.3f}","5 MHz","±95 mV"),
        ("11 高速","40",f"{freq[1]:.3f}","32 MHz","まず±0.20 V")],[95,84,93,94,CW-366],9)
    y=d.p(LEFT,y,"¹ Vdiff = VIN_P − VIN_N のピーク値。TT・27 °C・1.8 V・Vcm=0.63 V。01と10の振幅は機能評価の開始条件。11で±0.35 Vまで拡大する案は各入力端の周波数と直線性を実機で確認してから試す。HD3の公称条件は00。",size=9.4,leading=16,color=MUTE)
    y=d.sub(y+18,"ADC取得前にP/N両方の最高周波数を測る")
    y=d.p(LEFT,y,"① rst_nを解除しDBG_MODE=10とする。uo_out[0]と[1]の周期を複数回測り、各周波数を64倍する。差動入力を負端、零点、正端に設定して大きい方を fmax とする。温度・電源・BIAS_SELを変えるたびに繰り返す。",size=10,leading=17)
    y=d.p(LEFT,y+7,"② 必要条件は fs > 2 fmax。デューティ比が50%から外れる場合も考慮し、本設計では fmax ≤ 0.4 fs を運用目安とする。標準モードの確認例4.645 MHzでは理想下限9.29 MHz、10 MHzは下限目安、余裕込みで11.62 MHz以上。初回は20 MHzとする。",size=10,leading=17)
    y=d.p(LEFT,y+7,"③ DBG_MODE=00に戻し、起動時のWRAP_ERRを同期クリアして取得する。設定変更後は入力と発振の安定を待つ。OSRはリセット中に設定する。",size=10,leading=17)
    y=d.sub(y+18,"WRAP_ERRが0でも折り返す場合")
    d.p(LEFT,y,"タップが同じ標本区間で偶数回反転するとXORは0を返す。例えば理想的にちょうど1周期進むと実遷移は30でも観測は0になり、14以上で立つ警告が出ない。警告の有無だけでクロック下限を判定すると、もっともらしい誤コードを採用してしまう。",size=10,leading=17)

def safety(d):
    d.start("実機評価　通電・配線","初日通電の接続と操作順","対象は1.8 Vコアと、基板の電圧変換を通るデジタルI/O。実装基板の版・回路図・コネクタのピン1を記録してから接続する。")
    y=d.sub(157,"端子に許す電圧")
    y=d.p(LEFT,y,"ua[0]とua[1]は、立上り・立下り・過渡のオーバーシュートを含め、各瞬間に VGND ≤ Vpin ≤ VDPWR とする。両端子とも定常0.63 Vから始める。独立Nウェルや保護接合への順方向電流、無通電時の逆給電を避ける。VDPWR評価端1.62／1.98 Vはシミュレーション条件。破壊電圧・許容注入電流・ESD耐量のチップ絶対最大定格は未確定。",size=10,leading=17)
    y=d.sub(y+14,"準備 → 通電 → 停止")
    y=d.table(y,["順番","配線・操作"],[
        ("1　無通電で配線","W1/W2は出力OFF、DIOはHi-Z、GNDを先に共通化。W1からua[0]、W2からua[1]へ、各ピンの直前に1 kΩを1本ずつ直列に入れる。GND線を短くする。"),
        ("2　デジタル接続","AD2 DIOは3.3 V固定。現物回路図で3.3 V対応を確認したPMOD側と、指定のレベル変換経路を使う。1.8 Vコアに直結しない。RP2040／RP2350の共有GPIOは入力・プルなし、PIO/PWM/クロック駆動を止め、DIPも競合しない位置へ。"),
        ("3　TT電源を先にON","電流制限を有効にし、AWGを切ったまま板の電源とGNDを測定。タイル選択、rst_n=0、clk=Low、設定00。PMOD側とコア側の実電圧を確認する。"),
        ("4　外部入力をON","両AWGをDC 0.63 V・振幅0から有効化。抵抗のチップ側を2chで観測してVcm/Vdiffを確認。p.30の電流確認後、分周チェック（p.28）を行い、目的の振幅へ上げる。"),
        ("5　停止・異常時","外部DIOをHi-Z、AWGをOFFにしてからTTをOFF。電流制限到達、電圧降下、急な発熱・電流増加があれば入力を切り、直ちに電源を切って配線と電源競合を点検する。")],[120,CW-120],9.1)
    y=d.p(LEFT,y,"基板の版により電圧変換の位置は異なる。ASICの3.3 V I/Oパッドで変換する構成もある。PMODヘッダの電源端子へAD2の電源を重ねて接続しない。アナログピンは専用のUA端子を使う。",size=9,leading=15,color=MUTE)
    for caption,url in [("Digilent AD2　DIO仕様","https://files.digilent.com/manuals/WaveForms/3.25.1/start3.html"),("Tiny Tapeout　GPIO仕様と3.3 V I/O","https://tinytapeout.com/specs/gpio/"),("公式デモ基板　版別回路図","https://github.com/TinyTapeout/tt-demo-pcb")]:
        d.txt(LEFT,y+8,caption,8.5,"JB",TEAL)
        d.c.linkURL(url,(LEFT,H-y-11,R,H-y+2),relative=0,thickness=0);y+=18

def current(d):
    d.start("実機評価　電源電流","コア電流で通電状態を見分ける","標準バイアス、静音モード、OSR 128。電流はコア枝の時間平均。立上り突入と電源コンデンサの充電が収まってから読み取る。")
    with (DATA/"digital_current.csv").open() as f: rows=list(csv.DictReader(f))
    table=[]
    for key,label,analog in (("reset_clk_low","リセット保持・clk Low",42.86),("run_zero","20 MHz・無入力",42.86),("run_pos_fs","20 MHz・+0.20 V",None)):
        samples=[r for r in rows if r["state"]==key]
        assert len(samples)==3
        values=[float(r["digital_uA"]) for r in samples]
        typ=float(next(r for r in samples if r["liberty"].startswith("tt"))["digital_uA"])
        table.append((label,f"{typ:.3f}" if typ<1 else f"{typ:.1f}",f"{min(values):.3f}〜{max(values):.3f}" if typ<1 else f"{min(values):.1f}〜{max(values):.1f}",f"{analog+typ:.1f}" if analog else "約202"))
    y=d.table(151,["状態","デジタルTT µA","3ライブラリ µA","コア計TT µA"],table,[157,109,138,CW-404],9)
    y=d.p(LEFT,y,"無入力アナログ42.86 µA（TT・27 °C）。リセット中もリングは発振する。デジタルは配線後ゲートの128 µsのVCD、内部SPEF、タイル出力負荷、Libertyの内部・切替・漏れ電力を使用。3組はSS 100 °C/1.60 V、TT 25 °C/1.80 V、FF −40 °C/1.95 V。リング入力に同じTT周波数を再生した感度比較。グリッチ・非同期入力で消費するエネルギーやI/Oパッドのモデルには限界がある。",size=9.35,leading=16,color=MUTE)
    y=d.sub(y+14,"室温1.80 Vでの暫定判定窓")
    y=d.p(LEFT,y,"コア単体で測れる場合の初日目安は、リセット保持・clk停止で30〜60 µA、20 MHz・無入力で140〜260 µA。TTの約43／201 µAを中心に約±30%で丸めた点検用範囲である。下回れば選択・クロック・発振を確認し、上回れば入力競合とレール電圧を確認する。シリコンの正常分布は初回ロットで更新する。",size=10,leading=17)
    y=d.sub(y+14,"共用レールしか測れないとき")
    y=d.p(LEFT,y,"1.8 V枝のシャントで I = ΔV/R を計算する。USB電流にはMCU・LED・レギュレータも含まれる。同じ基板でタイル非選択時の電流、選択してリセット保持した電流、20 MHz運転時の電流を順に保存する。シャトルのMUX・クロック木が同時に切り替わる場合、その寄与も差分に残る。",size=10,leading=17)
    y=d.p(LEFT,y+6,"同じタイルの運転値と停止値の差は室温で約158 µAが目安。基板背景を分離できない場合は、上の絶対窓で故障を判定しない。電流制限は使用する電源枝・基板の許容値と背景電流に合わせて設定する。",size=10,leading=17)
    d.p(LEFT,y+7,"パッド負荷、基板、プローブ、電源電圧・温度・クロックとバイアス設定を電流値に添えて記録する。",size=9,leading=15,color=MUTE)

def noise(d):
    d.start("実機評価　雑音予算","SNDRの残差を発生源ごとに見る","p.19と同じTT曲線、−1 dBFS、10.010 kHz、20 MHz、OSR 128、seed 27。単位を入力換算µV rmsにそろえた。")
    result=json.loads((DATA/"noise_terms.json").read_text())
    table=[]
    for key,label,detail in [("front","入力段・バイアス","抽出した入力換算雑音スペクトル"),("jitter","左右リングの周期ジッタ","各側106.69 ps rms、FoM仮定 −155 dBc/Hz"),("quant","位相量子化と出力丸め","理想連続位相からの差と符号付きビット切捨て"),("transfer","変換曲線の歪み等","無雑音の5次曲線で残る高調波・窓残差"),("cross","交差項","有限記録内の成分間相関による電力差"),("total","総残差","SNDR 62.17 dBに対応")]:
        a=result[key]; rms=a["input_uVrms"]
        table.append((label,"—" if rms is None else f"{rms:.2f}",f"{a['percent']:.2f}%",detail))
    y=d.table(155,["出力換算した成分","µV rms","残差電力比","出所"],table,[138,66,85,CW-289],8.8)
    y=d.p(LEFT,y,"入力段単体の45.33 µV rmsは10 Hz〜78.125 kHzを平坦に積分した値。上表はCIC・窓・除外ビンを通した出力電力を、入力正弦波の実効値と基本波電力で入力換算した。分母には歪みを含む。単独波形の電力と交差項を合計すると100%になる。SSN注入は別試験（p.17–18）。",size=9.5,leading=16,color=MUTE)
    y=d.sub(y+16,"実機で予測を下回ったときの切り分け")
    y=d.p(LEFT,y,"① 同一入力を測定器でも収録する。信号源単体のHD3と比較し、入力振幅を下げた時に第3高調波の相対レベルが改善するか確認する。過入力、Vcm、入力スイッチの直線性も記録する。",size=9.8,leading=17)
    y=d.p(LEFT,y+6,"② 分周出力で各リングの周期変動と両者の相関を測る。64周期の合計と単周期ジッタは測定帯域が異なる。ジッタが独立という仮定を、温度・供給電圧・バイアスを変えて点検する。",size=9.8,leading=17)
    d.p(LEFT,y+6,"③ 電源を同時収録し、fs・出力レートとその高調波の線スペクトルを比較する。広帯域床はOSR・信号源インピーダンス・入力振幅を一つずつ変えて確認する。ロック帯を避けたDC入力でも雑音を記録する。",size=9.8,leading=17)
