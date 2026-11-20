"""Application information and dynamic-performance pages for the Japanese ADC report."""
import json
from pdf_report import ROOT, LEFT, R, CW, H, TEAL, MUTE, INK, PALE, WHITE, RULE, box, arrow, rows

REFS = [
    ("[1]  多相VCOの位相読み出し", "B. Saux, J. Borgmans, J. Raman, P. Rombouts, IEEE TCAS-I, 2024.",
     "A 3.5 GS/s 1-1 MASH VCO ADC With Second-Order Noise Shaping. §IV-B、図15は各相のサンプリングとXOR差分、§Vは試作チップの測定を扱う。本設計の一次位相差分とCIC2の役割を説明する際に参照した。論文の二段MASHの性能値は本チップに適用していない。",
     "著者版全文　arXiv:2409.15066", "https://arxiv.org/html/2409.15066v1"),
    ("[2]  符号化とシリアル出力", "Texas Instruments, ADS127L11, SBAS946C, Rev. C.",
     "§6.10のタイミング図と表8-15の符号表を参考に、受信エッジ、ビット順、極性を本設計のRTL・配線後波形から記載した。ADS127L11は外部からSCLKを入力する。本チップではADCがSCLKとCS_Nを生成する。",
     "データシート　タイミング図・出力コード表", "https://www.ti.com/lit/ds/symlink/ads127l11.pdf"),
    ("[3]  FFTの提示条件", "Texas Instruments, ADS890xB, SBAS728B, Rev. B.",
     "図5-21にはADS8900Bの代表FFTと入力周波数を掲載している。本書はこの形式を参考に、各スペクトラムについて入力振幅、解析点数、周波数分解能、電力の基準、評価帯域を明示した。",
     "データシート　図5-21", "https://www.ti.com/lit/ds/symlink/ads8900b.pdf"),
    ("[4]  コヒーレント取得と窓関数", "Analog Devices, Coherent Sampling vs. Window Sampling.",
     "観測窓内の周期数、周波数ビン、非同期取得のスペクトル漏れの関係を参照した。配線後の整数周期記録には矩形窓を、10.010 kHzの雑音予算には既存評価器の4項Blackman–Harris窓を使った。",
     "技術資料　Spectral Leakage and Windowing", "https://www.analog.com/en/resources/technical-articles/coherent-sampling-vs-window-sampling.html"),
]


def results():
    return json.loads((ROOT/"results/design_report/spectra/summary.json").read_text())


def guide(d):
    d.start("目次","設計値と波形をたどる","項目名を選択すると該当ページへ移動する。スペクトラムには、データの出所と観測条件を記した。")
    sections=[
        (3,7,"仕様・動作原理・接続","変換利得、CIC2の通過帯域、SPIの受信方法、入力電圧の校正。"),
        (8,11,"回路図と最終マスク","入力段、バイアスと受信器、発振段、デジタル読み出しの接続と配置。"),
        (12,14,"公称特性と検証判定","静特性・歪み、通常検証の範囲、T1〜T6の合否。"),
        (15,19,"起動・電源・出力スペクトラム","完全同相起動、低速ランプ、電源注入、配線後SPIのFFTと雑音モデルの長時間FFT。"),
        (20,23,"過入力・微小入力・デジタル異常系","飽和復帰、零点近傍のロック、バブルと設定切替からの復帰。"),
        (24,26,"設計レビュー・データ・参考文献","初回シリコンの測定順、波形・数値データの読み方、データシートと原著論文。"),
        (27,31,"実機評価マニュアル","端子・全モード、クロックの下限、AD2接続・通電順、電流の暫定窓、雑音内訳。")]
    for i,(first,last,title,note) in enumerate(sections):
        y=153+i*63
        d.rule(LEFT,y,R,y)
        d.txt(LEFT,y+24,f"{first:02d}–{last:02d}",12,"JB",TEAL)
        d.txt(LEFT+72,y+23,title,12,"JB");d.p(LEFT+72,y+42,note,CW-76,9,14,MUTE)
        d.c.linkRect("",f"p{first}",(LEFT,H-y-61,R,H-y),relative=0,thickness=0)
    y=d.sub(625,"同じSNDRでも、観測したデータが異なる")
    d.p(LEFT,y,"18ページは抽出アナログ波形を配線後ゲートへ入力して復号した16語。19ページは抽出静特性と仮定した位相雑音から生成した32,761点の予測。シリコンの測定値は初回試作後に取得する。",size=10.1,leading=18)


def principle(d):
    d.start("動作原理","差動電圧がコードになるまで","正の差動入力を与えたときの信号の向きと、各段で量子化される物理量を追う。")
    for x,title,note in [(LEFT,"差動入力","電圧差  VIN_P − VIN_N"),(LEFT+177,"リング2組","周波数差  fP − fN"),(LEFT+354,"位相読み出し","1標本間の遷移数差")]:
        box(d,x,151,151,48,title,note)
    arrow(d,LEFT+151,175,LEFT+176,175);arrow(d,LEFT+328,175,LEFT+353,175)
    y=d.sub(249,"1　入力電圧を発振速度の差に変える")
    y=d.p(LEFT,y,"VIN_Pを上げ、VIN_Nを下げると、VIN_Nをゲートに持つP側の入力PMOSがより強く導通する。分割した縮退抵抗が左右の枝電流の差を抑え、入力特性を線形化する。P側リングは速く、N側は遅くなる。共通の中心周波数は差分で相殺される。",size=10.2,leading=18)
    y=d.sub(y+20,"2　15段の位相を30個の遷移として数える")
    y=d.p(LEFT,y,"1リングでは1周期に15タップが各2回反転する。連続した標本間で各タップが高々1回反転する領域では、XORとビット数の合計が遷移カウントになる。1タップが同じ区間に2回反転するとXORでは見えなくなる。",size=10.2,leading=18)
    d.rect(LEFT,y+6,CW,78,PALE)
    d.txt(LEFT+14,y+29,"平均遷移数差    E[dP − dN] ≈ 30 × (fP − fN) / fs",12,"JB",TEAL)
    d.p(LEFT+14,y+51,"fs = 20 MHz。一定の周波数差1 MHzは平均1.5遷移／標本で、定常出力は約3,072コード。",CW-25,9,15)
    y=d.sub(y+120,"3　位相差分による一次の雑音整形")
    y=d.p(LEFT,y,"累積位相を遷移単位で Φ[n]、その量子化誤差を e[n] と置く。隣接標本の差を取ると、カウントは Φ[n] − Φ[n−1] ＋ e[n] − e[n−1] になる。誤差の伝達関数 1 − z⁻¹ はDCに零点を持つ。後段のCIC2が高域を減衰させてから出力レートを落とす。",size=10,leading=18)
    d.p(LEFT,y+10,"実遷移が15を超えると折り返し、WRAP_ERR=0のまま誤コードが出る。ADC取得前にDBG_MODE=10でP/N分周を測り、fs > 2 fmax、運用目安 fmax ≤ 0.4 fs を確認する（p.28）。零点付近では別にリング間ロックが生じる（T5）。多相読み出しは文献[1]図15。",size=9.2,leading=16,color=MUTE)


def filter_page(d):
    spec=results()["cic"]
    d.start("デジタルフィルタ","出力レートと使用帯域","20 MHzでサンプルした遷移数差を、2段積分・間引き・2段差分で処理する。次の図はCIC単体の理論応答。")
    d.image("cic_bandwidth",LEFT,146,CW,176)
    y=d.table(337,["OSR R","出力レート","−3 dB周波数","Nyquist点利得","群遅延"],[
        (str(r),f"{20000/r:.3f} kS/s",f"{spec[str(r)]['cutoff_hz']/1000:.2f} kHz",f"{spec[str(r)]['nyquist_db']:.2f} dB",f"{(r-1)/20:.2f} µs") for r in (128,256)],[74,119,114,109,CW-416],8.7)
    y=d.sub(y+13,"帯域の読み方")
    y=d.p(LEFT,y,"DC利得で正規化した振幅は |sin(πRf/fs) / (R sin(πf/fs))|²。最初の零点は fs/R、出力ナイキスト周波数はその半分にある。T3の19.53125 kHzではOSR 128のCIC減衰は0.45 dB。群遅延 (R−1)/fs はフィルタ単体の値で、タップ同期やSPI送出の待ち時間は別に生じる。",size=10,leading=17)
    y=d.sub(y+16,"OSRを変えてもDCのコード倍率は同じ")
    y=d.p(LEFT,y,"無正規化CIC2のDC利得は R²。OSR 128では21 bit結果を3 bit、256では5 bit右へシフトする。128²/8 = 256²/32 = 2,048 のため、一定の遷移数差 +1 は、どちらも定常的に +2,048 コードになる。",size=10,leading=17)
    d.p(LEFT,y+11,"通過帯域の平坦性が必要な測定では、測定周波数のCIC利得を記録する。スペクトラムの高調波にも、それぞれの周波数で異なる減衰がかかる。",size=9.2,leading=16,color=MUTE)


def format_page(d):
    ex=results()["gate"]["clean"]; code=ex["second"];word=code&65535
    d.start("出力フォーマット","SPIの1語を復号する","ADCがCS_NとSCLKを駆動し、受信側はSDOを読む。転送はMode 0、MSB先頭、16 bitの2の補数。")
    d.image("spi_word_example",LEFT,149,CW,144)
    d.p(LEFT,303,f"配線後T3の無注入記録、第6フレーム。縦の点線がサンプル位置。16回の立上りで {word:016b} = 0x{word:04X} を取り込み、符号変換すると {code:,} になる。",size=9.5,leading=16,color=MUTE)
    y=d.table(358,["受信項目","本チップの規約"],[
        ("端子","uio[1] = CS_N、uio[2] = SCLK、uio[0] = SDO。基板側は入力に設定する。uio[3]のWRAP_ERRは独立した状態出力。"),
        ("フレーム","CS_Nの立下りで開始。先頭の立上りで符号ビットD15を取り込み、16回目でD0を取り込む。次のCS_N立下りで受信カウンタを戻す。"),
        ("20 MHz時の時間","SCLK 5 MHz、周期200 ns。CS_Nロー幅3.2 µs。最初のSCLK立上りはCS_N立下りの100 ns後。フレーム間隔はOSR 128で6.4 µs、256で12.8 µs。"),
        ("符号変換","受信語uが0x8000以上なら u − 65536、それ以外はu。0xFFFF = −1、0x0000 = 0、0x0001 = +1。"),
        ("コードの両端","16 bitの表現域は−32,768〜+32,767。デジタルに一定の遷移数差±15を入力したときの定常コードは0x8800（−30,720）／0x7800（+30,720）。")],[117,CW-117],9)
    d.p(LEFT,y+6,"RP2040用の収録例は連続2語を32 bitに詰め、先の語を上位16 bitへ置く。保存ファイルでは32 bit単位がリトルエンディアンになる。線上のMSB順とファイルのバイト順を区別して復号する。受信例の実機動作は初回試作で確認する。",size=9.2,leading=16,color=MUTE)


def calibration(d):
    d.start("アプリケーション情報","入力電圧への換算と校正","標準バイアス、Vcm = 0.63 V、fs = 20 MHz。直流の差動入力と、デジタル語が表す量の関係を示す。")
    example=[]
    for r in rows("final_tt.csv"):
        v=float(r["diff_V"])
        if v in (-.20,-.16,.0,.16,.20):
            df=float(r["fp_MHz"])-float(r["fn_MHz"])
            example.append((f"{v:+.2f} V",f"{float(r['fp_MHz']):.4f}",f"{float(r['fn_MHz']):.4f}",f"{round(3072*df):+,d}"))
    y=d.table(154,["差動入力","Pリング MHz","Nリング MHz","DC換算コード"],example,[120,120,120,CW-360],9.2)
    y=d.p(LEFT,y+4,"TTの11点静特性から抜粋。右列は左右周波数差を3,072コード/MHzで換算・丸めた値。±0.20 V入力では約±4,240コードとなる。実SPIの各語には遷移量子化と切捨てが加わるため、電圧への換算にはチップごとの平均利得を使う。",size=9.4,leading=16,color=MUTE)
    y=d.sub(y+20,"チップごとに利得とオフセットを求める")
    y=d.p(LEFT,y,"① VIN_P = 0.63 V + Vdiff/2、VIN_N = 0.63 V − Vdiff/2 とする。OSRはリセット中に選択し、解除後の先頭2フレームを除く。零入力と±0.16 Vで複数フレームの平均コード C₀、C₊、C₋ を記録する。",size=9.8,leading=17)
    y=d.p(LEFT,y+8,"② 2点の傾き G = (C₊ − C₋) / 0.32 V、切片 B = (C₊ + C₋) / 2 を求める。線形域では Vdiff ≈ (C − B) / G。上表の傾きは約21.2 kコード/Vで、1コードの換算値は約47 µV。これは線形域の平均利得から得た尺度である。",size=9.8,leading=17)
    y=d.p(LEFT,y+7,"③ 物理0 Vを中心にまず±20 mVを掃引し、平均コードが0を挟む電圧から実測Vosを補間する。ゼロの平坦域があれば両端・中点を記録し、中点をVosと定義。符号反転を挟めなければ範囲を広げる。Vos±1、±3、±10 mVを正負両側から同じ保持時間で往復し、方向別のロック端と不感帯幅を記録する。",size=9.5,leading=16)
    y=d.sub(y+10,"オフチップ3次補正")
    d.p(LEFT,y,"ロック域外の5〜11点で x=(C−B)/G とし、既知電圧に V̂=a₀+a₁x+a₂x²+a₃x³ を最小二乗で当てる。単調な校正範囲内だけに適用し、独立の正弦波で補正前後のHD3・SFDR・SNDRを比較する。ロック帯では逆変換が一意にならない。20 MHz→32 MHzでは同じ周波数差のコードは20/32倍（p.13）。",size=9.1,leading=15)


def measured_spectrum(d):
    a=results()["gate"];quiet=a["clean"];inj=a["dirty"]
    d.start("動特性　配線後ゲート","SPI出力から計算したSNDR","T3の局所電源・接地に各5 Ω＋2 nH。無注入と20 MHz／156.25 kHzを各1 mA注入した条件の比較。")
    d.image("spi_sndr_spectrum",LEFT,147,CW,191)
    d.p(LEFT,350,"各点はその条件の基本波電力を0 dBcとした片側のビン電力。2系列の印は重なりを避けるため横にずらした。入力周波数19.53125 kHzはビン2に一致する。",size=9.2,leading=15,color=MUTE)
    y=d.table(396,["復号した16語","無注入","電流注入"],[
        ("SNDR",f"{quiet['sndr']:.2f} dB",f"{inj['sndr']:.2f} dB"),
        ("基本波／残差（コードrms）",f"{quiet['tone_rms']:.2f} ／ {quiet['residual_rms']:.3f}",f"{inj['tone_rms']:.2f} ／ {inj['residual_rms']:.3f}"),
        ("SFDR・最大スプリアス",f"{quiet['sfdr']:.2f} dBc・58.594 kHz",f"{inj['sfdr']:.2f} dBc・58.594 kHz")],[196,152,CW-348],9)
    y=d.sub(y+9,"FFTの条件と再計算")
    y=d.p(LEFT,y,"TT・27 °C、差動入力0.17825 Vピーク（定格0.20 Vの−1 dB）、OSR 128。各20フレームのうち第5〜20語を採用した。156.25 kS/s、16点、矩形窓、観測時間102.4 µs、ビン幅9.765625 kHz。平均を引き、正周波数の電力を両側分足し、ナイキストは1回だけ数える。",size=9.6,leading=16)
    y=d.p(LEFT,y+7,"SNDR = 10 log₁₀(P[2] / ΣP[k])。分母はビン1および3〜8で、高調波を含む。ビン6には第3高調波と折り返した第5高調波が重なる。この短い記録から連続的な雑音床やシリコン全帯域のSNDRは確定できない。",size=9.6,leading=16)
    d.p(LEFT,y+8,"生のCS_N・SCLK・SDO、復号した16語、ビン別電力を同梱した。スペクトラムの示し方は文献[3]、窓と取得条件は文献[4]を参照。",size=8.8,leading=15,color=MUTE)


def model_spectrum(d):
    m=results()["model"]
    d.start("動特性　雑音モデル","長時間コード列の予測スペクトラム","A5雑音予算の中央条件を同じ乱数seedで再計算。抽出したTT静特性、入力段の周波数別雑音、仮定した周期ジッタを使う。")
    d.image("budget_sndr_spectrum",LEFT,147,CW,191)
    d.p(LEFT,346,"縦軸は各ビンの電力を基本波主ローブの積算電力で割ったdBc/bin。窓を掛けるため、基本波の電力は隣接する複数のビンに分布する。",size=9.2,leading=15,color=MUTE)
    y=d.table(390,["評価項目","中央条件の結果","評価項目","中央条件の結果"],[
        ("SNDR",f"{m['sndr']:.2f} dB","SNR",f"{m['snr']:.2f} dB"),
        ("SFDR",f"{m['sfdr']:.2f} dBc","HD3",f"{m['hd3']:.2f} dBc"),
        ("出力FFT点数",f"{m['n']:,}","ビン幅",f"{m['bin_hz']:.3f} Hz")],[114,138,121,CW-373],9)
    y=d.sub(y+10,"記録と積算帯域")
    y=d.p(LEFT,y,f"入力10.010 kHz・0.17825 Vピーク、fs = 20 MHz、OSR 128、出力156.25 kS/s。{m['samples']:,}語から先頭4語を除き、約209.67 msを解析した。周期形4項Blackman–Harris窓、基本波ビン {m['tone_bin']} の前後5ビンを積算。DC側の先頭6ビンを除き、約28.6 Hzからナイキスト近傍78.125 kHzまでの残りを雑音・歪み電力に入れた。",size=9.45,leading=16)
    y=d.p(LEFT,y+8,f"仮定したリングFoMは−155 dBc/Hz、各側の周期ジッタは {m['sigma_ps']:.2f} ps rms、seedは{m['seed']}。11点静特性の5次近似でリング周波数を求めるため、T5の履歴依存ロックはこのモデルに含まれない。",size=9.45,leading=16)
    y=d.p(LEFT,y+8,"SNRは第2〜5高調波域を除いて雑音を補間した推定値。SFDRは基本波以外の最大11ビン群との電力比。9条件のSNDRは60.04〜63.12 dB。中央条件の入力段・ジッタ・量子化・歪み別の電力比はp.31。",size=9,leading=15,color=MUTE)
    y=d.sub(y+16,"初回シリコンで同じ帯域を測るには")
    d.p(LEFT,y,"安定後のSPIを32,768語連続取得する。信号源をサンプルクロックに同期できる場合は2,099周期（10,008.812 Hz）で矩形窓を使う。独立クロックなら窓関数と集計ビンを明記する。信号源単体の残留歪み、チップの電源・温度、実入力振幅を出力コード列とともに保存する。",size=9.3,leading=16)


def references(d):
    d.start("参考文献","データシートと原著論文","各資料の適用箇所を示す。図・数値表は、本設計の記録または記載した理論式から作成した。")
    y=158
    for title,author,note,label,url in REFS:
        d.txt(LEFT,y,title,12,"JB",TEAL)
        d.txt(LEFT,y+21,author,9.5)
        end=d.p(LEFT,y+42,note,size=9.2,leading=16)
        d.txt(LEFT,end+3,label,9,"JB",TEAL)
        d.c.linkURL(url,(LEFT,H-end-7,R,H-end+11),relative=0,thickness=0)
        d.rule(LEFT,end+18,R,end+18);y=end+42
