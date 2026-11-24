"""Assemble design, verification and lessons into a single PDF; --preview uses only available pages."""
from pdf_report import *
import datasheet
import bench_manual
def bias_receiver(d):
    d.start("回路図　2 / 3","電流基準とレベル変換","同じ名前のネットラベルは電気的に接続する。両パネルは最終抽出・設計SPICEの接続から作成した。")
    for center,label in [(168,"βマルチプライヤ"),(422,"CVSL 位相受信器")]:
        d.txt(center-53,165,label,11,"JB",TEAL)
        a,b=center-46,center+46
        d.rule(a,196,b,196,TEAL,1.4);d.txt(center-20,188,"VDPWR",8,"JB",TEAL)
        for x,left,pg,ng,node in ([(a,True,"vb","vn","vb"),(b,False,"vb","vn","vn")] if center==168 else [(a,True,"R","a[k]","L"),(b,False,"L","b[k]","R")]):
            d.rule(x,196,x,210,INK);mos(d,x,230,pg,True,left);d.rule(x,250,x,285,INK)
            d.circle(x,262,2.3);d.txt(x+8,268,node,9,"JB",TEAL);mos(d,x,305,ng,False,left)
            if center==168 and left:
                d.rule(x,325,x,339,INK);d.txt(x+8,336,"rs",8)
                pts=[(x,339),(x-4,342),(x+4,346),(x-4,350),(x+4,354),(x-4,358),(x,361)]
                for p,q in zip(pts,pts[1:]):d.rule(*p,*q,INK)
                ground(d,x,361)
            else:ground(d,x,325)
    d.rule(LEFT+CW/2,147,LEFT+CW/2,388)
    y=d.table(405,["回路","素子・接続と動作"],[
      ("基準電流　W/L [µm]","上段PMOSは各2/2、共通ゲートvbで左枝がダイオード接続。下段NMOSは左8/2、右2/2、共通ゲートvnで右枝がダイオード接続。"),
      ("基準抵抗","rsから接地へL/W=97.1/0.69 µmを2本直列。TT・27 °C、1 mVで各48.10 kΩ、計96.21 kΩ。"),
      ("CVSLの左右節点","上段PMOS W/L=0.42/2.4 µmを交差結合。下段LVT NMOS W/L=4/0.15 µmにa[k]とb[k]を入れ、VDPWR振幅へ変換する。"),
      ("バッファと負荷","LはCMOSバッファを経てタップ出力へ、Rは対称なダミーバッファへ接続する。各リング15個。最終配線の追加タップ負荷は3.09〜8.11 fF。")],[130,CW-130],9)
    d.txt(LEFT,645,"起動枝の接続　W/L [µm]",11,"JB",TEAL)
    # Draw the physical current paths. Repeated gate labels are the same electrical net.
    x1,x2=143,350
    for x,upper,lower in ((x1,"VDPWR","kick"),(x2,"vb","VGND")):
        d.txt(x+8,676,upper,8,"JB",TEAL);d.rule(x,665,x,678,INK)
        mos(d,x,698,"VGND" if x==x1 else "kick",x==x1)
        d.rule(x,718,x,731,INK);d.txt(x+8,731,lower,8,"JB",TEAL)
    d.rule(x1,731,x1,738,INK);mos(d,x1,755,"vn",False);ground(d,x1,775)
    d.txt(x1+12,704,"P 0.42/12",8);d.txt(x1+12,758,"LVT N 5/0.15",8);d.txt(x2+12,704,"N 0.5/1",8)
    d.p(267,753,"vnが低いと弱いPがkickを上げ、右のNがvbを下げる。vnが上がるとLVT Nがkickを下げて起動枝を解除する。",272,8.5,14,color=MUTE)
def layout(d,r):
    d.start("レイアウト","最終マスクと実装領域","製造候補GDSの図形をKLayoutで階層展開し、選択した7層を同じ座標で描画した。")
    d.image("gds_tile",LEFT,150,264,394)
    d.rule(LEFT+2,536,LEFT+84,536,INK,1.6)
    for x in (LEFT+2,LEFT+84):d.rule(x,533,x,539,INK,1)
    d.txt(LEFT+92,539,"50 µm",8,"JP",MUTE)
    px=310;d.txt(px,173,"デジタル読み出し",12,"JB")
    d.p(px,196,"左下 (4.25, 125.76) µm。\n150 × 100 µmに同期器・CIC・SPIを配置。\nフィラーを除くセル面積は8,964 µm²。",R-px-6,9.2,16)
    d.txt(px,266,"アナログコア",12,"JB")
    d.p(px,290,"左下 (0, 0) µm。外形161 × 121 µm。\n下側に入力段とバイアス、\n上側に左右のCCROとCVSLを置いた。",R-px-6,9.2,16)
    d.image("gds_ring_detail",px+2,354,112,113)
    d.rule(px+4,476,px+24,476,INK,1.3);d.txt(px+29,479,"5 µm",7.5,"JP",MUTE)
    d.p(px+123,379,"P側の拡大図\nx = 1〜28 µm\ny = 86〜114 µm",102,8.3,15,color=MUTE)
    geo=json.loads((ASSETS/"geometry.json").read_text())
    x=LEFT
    for l in geo["layers"]:
        d.rect(x,555,10,9,l["color"]);d.txt(x+14,563,l["name"],8.4);x+=70
    y=d.table(593,["検査","結果","検査","結果"],[("公式precheck","15 / 15","全体DRC・アンテナ","0 / 0 件"),("トップLVS","10,390素子一致","対応ネット","5,137ネット一致"),("外部端子・タップ","64 / 64導通","使用メタル","最大met4")],[103,120,130,CW-353],8.8)
    d.p(LEFT,y,"中央の縦met4はVGND（x=92.80 µm）、左端はVDPWR（x=0.60 µm）。共に幅1.20 µm、y=2〜217 µm。最終GDSで端子から導通する全配線層を追跡し、外部clkの下端はy=169.535 µm、SPI 3本はy≥200.005 µm。アナログ領域（y≤121 µm）に入らない。境界の高速信号はCVSLからの30タップ。rp–rnの抽出結合は4.1989 fF。",size=9.4,leading=16)
def nominal(d,r):
    d.start("公称特性","利得・歪み・零点近傍","標準バイアス。静特性は11入力点、動特性は50 kHz正弦波2周期の連続位相から評価した。")
    y=d.image("transfer",LEFT,156,CW,199)
    d.p(LEFT,y+17,"左は差動入力に対する左右周波数差。右は電源に追従して入力を立ち上げたA6の配線負荷込みデータ。±3 mVでは約±20 kHz、±1 mVでは数Hzだった。別の起動条件との比較はT5に示す。",size=9.2,leading=16,color=MUTE)
    y=d.table(399,["解析条件","HD2","HD3","HD3規格までの余裕"],[
      ("TT 1.80 V、静特性","−78.46 dBc","−63.73 dBc","+1.73 dB"),
      ("SS 1.62 V、静特性","−75.06 dBc","−82.60 dBc","+20.60 dB"),
      ("TT 1.80 V、50 kHz","−91.18 dBc","−62.97 dBc","+0.97 dB"),
      ("同上、外部タップ負荷込み","−90.51 dBc","−62.64 dBc","+0.64 dB")],[174,98,98,CW-370],8.7)
    y=d.sub(y+18,"雑音とばらつきの限界")
    y=d.p(LEFT,y,"20 MHz・OSR 128・−1 dBFSで、入力換算雑音45.33 µV rmsと仮定したリングFoMを組み合わせた9条件のSNDRは60.04〜63.12 dBだった。T3の決定論的な過渡波形と、この雑音予算は異なる測定量である。",size=9.6,leading=17)
    d.p(LEFT,y+13,"抽出入力段のミスマッチ50回で入力換算オフセットは−11.04〜+13.02 mV。左右リングの個体差を含む歩留まり、パッドを含む実機HD3、長時間の位相雑音は未確定。",size=9.6,leading=17)
def baseline_tests(d):
    d.start("通常検証","A1〜A6・D1〜D4 の確認範囲","追加試験の出発点となった測定。未確認の条件と、初回試作で採用した判定を各行に記した。")
    y=d.table(148,["項目","証拠と残った条件"],[
       ("A1　自律起動","標準バイアスの1 µs電源ランプで自律起動し、左右の平均は3.769 MHz。全段の最小差動振幅は1.485 Vpp。指定した3コーナー×1 µs・1 msの全組合せは未確認。完全同相初期値と10 msランプはT1・T2で評価した。"),
       ("A2　受信器の低速端","SF・−20 °C・1.98 V、低速バイアスで30タップすべてが動作。最小103.98 kHz、デューティ50.06〜50.17%、振幅はほぼ電源幅。"),
       ("A3　速度と余裕","FF・85 °C・1.98 Vで、標準4.645 MHz、高速7.777 MHz。上限は各8.0 MHzと12.8 MHz。最終配線の追加負荷を含む高速端は7.776 MHz。"),
       ("A4　直線性","SS・1.62 Vの電流源PMOSの最小VSDは0.261 V、基準は0.2 V。TTの静的・動的HD3の差は0.76 dB。HD2の差は12.72 dBで推定手法間の一致目安を超えた。初回試作は各条件の高調波振幅で判定した。"),
       ("A5　雑音","9条件の雑音予算で最小60.04 dB。リングの素子雑音を含む1,000周期のジッタと、チップでのSNDRは未確認。"),
       ("A6　零点近傍","電源追従入力での配線負荷込み差周波は+1 mVで+1.17 Hz、+3 mVで+20.05 kHz。1 mVでの比例応答を確立できず、起動条件と結合の影響をT5で再評価した。"),
       ("D1〜D3　デジタル","RTLと配線後ゲートを各13,800クロック照合。Wrapと解除、両OSR、±30,720の端点、SPIの70フレームを確認。抽出タップを実ゲートに再生した32 MHzの定常値は、+0.20 Vで+2647、−0.20 Vで−2649コード。"),
       ("D4　面積・速度","デジタルマクロは150 × 100 µm、フィラーを除くセル面積8,964 µm²。32 MHz・3コーナーの余裕はセットアップ最小+6.11 ns、ホールド最小+0.07 ns。")],
       [113,CW-113],8.6)
    d.p(LEFT,y+6,"20 MHzの約+4,236コードに対して32 MHzでは約+2,647。DC利得は同じでも、毎標本の遷移数差が1/fsに比例し、20/32倍となる。FF・85 °C、Vcm=0.63〜0.631 Vの全振幅HD3・入力対飽和余裕は未確認。高速端の周波数検証はA3の範囲。",size=9,leading=15,color=MUTE)

def stress_power(d):
    d.start("T1","完全同相からの差動発振","外部からの起動パルスを与えず、全段の初期電圧が一致する状態からの逆相への移行を測った。")
    y=d.image("startup",LEFT,148,CW,155)
    d.p(LEFT,y+14,"T1のTT・BIAS_SEL=00。Pリング第0段のA/Bは0.35 Vから同時に出発する。灰色の基準線はリング内の電源rp。",size=8.8,leading=15,color=MUTE)
    table=[];phases=[];ic=[]
    for corner in ("tt","ss","ff","sf","fs"):
        row=[corner.upper()]
        for bx in (0,1):
            a=obj(f"T1_{corner}_{bx}")
            stages=[k for v in a["banks"].values() for k in v["stages"]]
            phases.extend(abs(v["final_phase_deg"]-180) for v in stages if v.get("final_phase_deg",-999)>=0)
            ic.extend(v["ic_error_V"] for v in a["banks"].values())
            lat=[v["confirmed_cycles"] for v in stages if v.get("confirmed_cycles") is not None]
            row.append(f"{a['status']}   {max(lat):.2f}周期" if lat else a["status"])
        table.append(row)
    y=d.table(353,["コーナー","標準00　最遅段","低速01　最遅段"],table,[110,194,CW-304],8.2)
    y=d.sub(y+20,"全段で逆相になったことをどう判定したか")
    y=d.p(LEFT,y,f"各リングのA/B 30ノード、計60ノードを0.35 Vに設定した。初期差・設定誤差は最大 {max(ic):.2e} V。各段の振幅がリング電源の20%以下から80%以上へ達し、相補位相が180°±15°、周期が最終値の±15%に入ることを確認した。",size=9.7,leading=17)
    d.p(LEFT,y+14,f"起動所要周期は、この条件が持続する最初の2周期の終了までを数えた。測定できた最終周期の逆相誤差は全条件で最大 {max(phases):.2f}°。評価対象は実際のレイアウト非対称を含む抽出回路と指定した初期値である。",size=9.7,leading=17)
def power(d):
    d.start("T2","電源ランプ・瞬断・高温リーク","低速バイアスで緩やかな電源投入、標準バイアスで動作中の瞬断を試した。")
    y=d.image("slow_ramp",LEFT,146,CW,136)
    r=obj("T2_ramp");rl=r["tail"];ref=obj("T2_reference")["tail"];b=obj("T2_brown");leak=obj("T2_leak")
    note="電源投入時からの全区間を保存した。" if r.get("measured_case") else "実測保存は末尾150 µs、破線は指定した全区間の電源軌跡。"
    d.p(LEFT,y+11,f"10 msランプ。{note} 最終P側 {rl['fp_MHz']*1000:.2f} kHz、1 µsランプ対照 {ref['fp_MHz']*1000:.2f} kHz。VBは {rl['vb_V']:.4f} V。",size=8.8,leading=15,color=MUTE)
    y=d.image("brownout",LEFT,334,CW,163)
    d.p(LEFT,y+11,f"0.6 Vを50 µs保持するとタップ遷移が停止した。復電後はP側 {b['after']['fp_MHz']:.4f} MHz、N側 {b['after']['fn_MHz']:.4f} MHz。全30タップの最小振幅は {b['after']['min_swing_V']:.3f} Vppだった。",size=8.8,leading=15,color=MUTE)
    y=d.table(559,["FF・85 °C・1.98 V","OFF 39単位","ON 1単位","実ON電流比"],[(s.upper()+"バンク",f"{v['off_nA']:.4f} nA",f"{v['on_nA']:.2f} nA",f"{v['off_percent_actual']:.4f}%") for s,v in leak["banks"].items()],[150,123,119,CW-392],8.7)
    y=d.p(LEFT,y+9,"電流源の出力端にゼロ電圧プローブを挿入し、発振の整数周期で符号付き平均を求めた。OFF側の上限は25 nAと実ON電流の5%。バイアス・発振周波数の復帰は対照の±5%で判定した。",size=9.4,leading=16)
    if "numerical_cross_check" in r:
        proof=r["numerical_cross_check"];dev=100*max(proof["reference_relative_differences"].values())
        d.p(LEFT,y+7,f"10 ms全区間はRELTOL=0.003、最大刻み50 ns。1 µs対照をRELTOL=0.0005でも解き、周波数・バイアス・振幅の6指標で差は最大 {dev:.3f}%。",size=8.7,leading=15,color=MUTE)
def ssn(d):
    d.start("T3","電源インピーダンスと変調","パッケージ相当の電源・接地のそれぞれに5 Ωと2 nHを直列に挿入した。")
    clean=obj("T3_clean");dirty=obj("T3_dirty")
    y=d.image("ssn",LEFT,148,CW,185)
    d.p(LEFT,y+13,"20 MHzと156.25 kHzのパルス電流を各1 mAで同時注入。左は電源・接地の波形、右は配線後ゲートのSPIから復号した16コードのスペクトル。基本波は19.53125 kHz。",size=9,leading=16,color=MUTE)
    y=d.table(387,["測定量","対照","電流注入"],[("局所電源変動",f"{clean['local_supply_pp_mV']:.2f} mVpp",f"{dirty['local_supply_pp_mV']:.2f} mVpp"),("CIC後の16点SNDR",f"{clean['sndr_dB']:.2f} dB",f"{dirty['sndr_dB']:.2f} dB"),("差周波変調・156.25 kHz",f"{clean['freqline_dBc']['0.15625']:.2f} dBc",f"{dirty['freqline_dBc']['0.15625']:.2f} dBc"),("差周波変調・20 MHz",f"{clean['freqline_dBc']['20']:.2f} dBc",f"{dirty['freqline_dBc']['20']:.2f} dBc")],[215,139,CW-354])
    y=d.sub(y+13,"判定窓と同期の見方")
    sl=min(z["min_excursion_cycles"] for z in dirty["lock_excursion"].values())
    budget=obj("T3_power_budget")
    y=d.p(LEFT,y,f"16出力コードの注入・対照差から、DCと基本波を除いた電力を求めた。これを54 dBの基準雑音に電力加算した悪化は、8位相と配線後ゲートで最大 {budget['max_loss_from_target_dB']:.3f} dB。許容値は3 dB。",size=9.8,leading=17)
    pairs=zip(clean["sample_phase_sweep"],dirty["sample_phase_sweep"])
    drop=max(aa["sndr_dB"]-bb["sndr_dB"] for aa,bb in pairs)
    y=d.p(LEFT,y+8,f"実測の無注入対照と直接比較した8位相での最大低下は {drop:.2f} dB。観測窓は102.4 µs、候補同期比に対する位相変化は最小 {sl:.2f} 周期。1周期を超えたため、この比での全窓にわたる同期は観測されなかった。",size=9.5,leading=17)
    gate=obj("T3_gate")
    d.p(LEFT,y+7,f"配線後ゲートのSPI再生は対照 {gate['clean_sndr_dB']:.2f} →注入 {gate['dirty_sndr_dB']:.2f} dB。2,688クロックのオラクル不一致は0件。短時間の引き込み、他の分数比、素子雑音込みのSNDRは実機で確認する。",size=9.1,leading=16,color=MUTE)
def overload(d):
    d.start("T4","過入力からの復帰とキックバック","入力を正負それぞれ0.6 V差動まで振り、定格内へ戻した後の全30タップを観測した。")
    t=obj("T4_step");wi=t["windows"]
    tab=[]
    for label,i in [("+0.6 Vから+0.1 Vへ",1),("−0.6 Vから−0.1 Vへ",3),("Vcm=0.48 V",4),("Vcm=0.78 V",5)]:
        a=wi[i];tab.append((label,f"{a['fp_MHz']:.4f}",f"{a['fn_MHz']:.4f}",f"{a['min_swing_V']:.3f} Vpp"))
    y=d.table(155,["入力条件","P側 MHz","N側 MHz","全タップ最小振幅"],tab,[176,86,86,CW-348])
    d.p(LEFT,y,f"定格に戻してから全タップが定常周期の±5%に入るまで、正側 {t['recovery_cycles'][0]:.2f} 周期、負側 {t['recovery_cycles'][1]:.2f} 周期。今回の復帰期限は2周期とした。",size=9.6,leading=17)
    y=d.image("dynamic",LEFT,379,CW,160)
    d.p(LEFT,y+10,"TT・50 kHz・±0.20 V、各入力の直列1.5 kΩと対地10 pF。30タップの立上り・立下り時刻から各リングの位相を求め、短い区間の傾きで周波数を表示した。",size=8.7,leading=15,color=MUTE)
    hd=[[obj("T4_"+pre+k)["hd3_dBc"] for k in ("ideal","series")] for pre in ("","literal_")]
    y=d.table(603,["入力容量の接続","0 Ω HD3","1.5 kΩ HD3","悪化量"],[(lab,f"{a:.3f} dBc",f"{b:.3f} dBc",f"{b-a:+.3f} dB") for lab,(a,b) in zip(["信号ピンから接地","信号経路に直列"],hd)],[151,119,119,CW-389])
    d.p(LEFT,y,"直列コンデンサ条件では各ピンに100 MΩのDCバイアス帰路を追加した。判定は同じ容量接続での抵抗差分1 dB未満。スイッチの電圧依存性はモデル外。",size=9.2,leading=16,color=MUTE)
def lock(d):
    d.start("T5","微小差動入力と注入ロック","+1 mVで中点容量と左右リング電源間の直接結合を変え、差周波と相対位相を測った。")
    y=d.image("locking",LEFT,150,CW,173)
    d.p(LEFT,y+13,"直接結合4.1989 fFに0、1、5、20、50 fFを追加し、直接結合除去も比較した。中点MIMは典型PDKの面積・周長式で206.58 fF（10 × 10 µm）。",size=9.2,leading=17,color=MUTE)
    tab=[]
    for k in ("removed",0,1,5,20,50):
        a,b=[obj(f"T5_{v}_{k}") for v in (0,1)]
        tab.append((f"{a['total_direct_fF']:.4f}",f"{a['phase_fit_kHz']:+.4f}",f"{b['phase_fit_kHz']:+.4f}","／".join("あり" if x["lock_indicator"] else "なし" for x in (a,b))))
    y=d.table(390,["結合合計 fF","Cmidなし kHz","Cmidあり kHz","ロック相当 なし／あり"],tab,[107,118,118,CW-343],8.4)
    y=d.sub(y+13,"設計判断")
    base=obj("T5_0_0");m=obj("T5_1_0")
    y=d.p(LEFT,y,f"実装値での差周波は {base['phase_fit_kHz']:+.3f} kHz、中点にMIMを加えると {m['phase_fit_kHz']:+.3f} kHz。線形域からの予想は6.9 kHz。5倍の要求値は20.9945 fF。直接結合を除いてもソースや電源を介した結合は残る。",size=9.6,leading=17)
    d.p(LEFT,y+13,"この掃引の観測窓は12 µsで、線形応答でも左右位相は0.083周期しか進まない。零入力で起動した後に信号を加え、予想ビートを1周期以上含む160 µsまで観測した結果を次頁に示す。",size=9.2,leading=16,color=MUTE)

def lock_history(d):
    d.start("T5　長時間試験","零入力で起動した後の微小信号応答","実装回路と、中点MIMだけを追加した抽出回路の両方で、12 µsに差動入力を0から+1 mVへ切り替えた。")
    y=d.image("long_phase",LEFT,150,CW,174)
    d.p(LEFT,y+16,"各リング15タップの立上りから位相を復元し、18 µsでの位相差をゼロとした。左は6.9 kHz/mVの線形感度から計算した基準を含む。右は抽出回路2条件の観測範囲。",size=9.2,leading=16,color=MUTE)
    base,mid=[obj(n) for n in ("T5_hold","T5_hold_mid")]
    tab=[(s,f"{r['delta_kHz']:+.4f} kHz",f"{r['relative_phase_span_cycles']:.4f} 周期","あり" if r["lock_indicator"] else "なし") for s,r in [("実装（中点MIMなし）",base),("中点MIM 206.58 fF",mid)]]
    y=d.table(396,["条件","差周波（回帰）","相対位相の変動幅","ロック相当"],tab,[142,127,140,CW-409],8.6)
    y=d.sub(y+16,"中点容量と5倍余裕の判定")
    mid_note="ロック相当の領域を抜けた。" if not mid["lock_indicator"] else "ロック相当の領域にとどまった。"
    y=d.p(LEFT,y,f"実装の直接結合4.1989 fFで、相対位相の変動は {base['relative_phase_span_cycles']:.4f} 周期。線形領域で予想する160 µs当たり1.104周期を大きく下回った。同じ入力履歴で中点MIMを追加した回路は{mid_note} 製造候補に対する5倍のロック余裕は未達とした。",size=10,leading=18)
    y=d.sub(y+17,"入力の立上りと解析刻みの感度")
    track,finer=[obj(n) for n in ("T5_tracking","T5_tracking_2ns")]
    d.p(LEFT,y,f"短窓で+1 mV入力を電源に追従させると、差周波は最大刻み3 nsで {track['phase_fit_kHz']:+.3f} kHz、2 nsで {finer['phase_fit_kHz']*1000:+.1f} Hz。解析刻みだけでロック相当の判定が反転した。旧A6は別の制御源構成で+1.17 Hz。実機では零点の両側からの往復掃引と保持時間をそろえて比較する。",size=9.6,leading=17)
def digital(d):
    d.start("T6","CICの回復とSPIの切替境界","同じ入力・設定をRTLと配線後ゲートの両方に与え、独立に計算したCIC2出力と毎クロック照合した。")
    a=obj("T6");r=a["rtl"];g=a["gates"]
    y=d.image("spi",LEFT,154,CW,155)
    d.p(LEFT,y+15,"配線後ゲートの実出力をCSの開始位置で切り出した。CSロー中の16回のSCLK立上りで、SDOをMSBから受信する。",size=9,leading=16,color=MUTE)
    y=d.table(366,["操作","観測結果"],[
      ("1クロックのバブル",f"{r['bubble_count']}回。{r['different_frame_words']}語に影響。影響範囲外で出力不一致{len(r['persistent_bad_frames'])}件。"),
      ("内部積分器",f"単独バブルの400クロック後も第1積分器の差は+2。第2積分器の差はtick 7399→7780で{r['directed_acc2_difference']['7399']}→{r['directed_acc2_difference']['7780']}（毎clk +2）。"),
      ("リセット解除","立上り1 ps前に4回解除。OSR 128で226、OSR 256で357クロック以内に最初の16 bitを完了。"),
      ("動作中の設定変更",f"OSR {len(r['mode_changes'])}回、DBG_MODE {r['dbg_transitions']}回。新しいOSR 128での完了は最長{max(v['spi_complete_clocks'] for v in r['mode_changes'] if v['osr']==128)}クロック。規定は256クロック。"),
      ("形式・コード照合",f"各{r['ticks']:,}クロック、{r['frames']}フレーム。形式異常{r['malformed_count']}件。SPI 3信号とWRAPの照合不一致はRTL {r['oracle_mismatched_ticks']}、ゲート {g['oracle_mismatched_ticks']}クロック。")],[150,CW-150],8.9)
    y=d.sub(y+10,"切替期限を超える理由")
    y=d.p(LEFT,y,"旧フレームが有効な間、現行RTLはphase=97でOSRを採用する。この直後の256→128要求は旧周期の残りを待つ。初回試作ではリセット中にOSRを選び、変換中は固定する。",size=9.5,leading=16)
    d.p(LEFT,y+6,"単発バブル後の積分器差+2と傾き+2のランプは正常な応答。21 bitの2の補数による剰余演算でも、間引き後の2階差分 d[k]−2d[k−1]+d[k−2] は直線を消去する。影響が過ぎてコードが戻れば再初期化は不要。T6の期限超過はOSR切替の別現象。",size=9.1,leading=15,color=MUTE)
def limits(d):
    d.start("設計レビュー","反省点と次に確かめること","再発防止に使える観測値と、それを受けた具体的な改版・実機試験を対応させた。")
    y=d.table(155,["設計上の反省","次の検証・改版"],[
       ("零点近傍では、過渡解析の刻みだけでもロック相当の判定が変わった。","個体ごとの実測Vosを基準に往復掃引し、同一保持時間でヒステリシスとロック幅を測る。"),
       ("公称HD3の配線負荷込み余裕は0.64 dB。","実スイッチの電圧依存性・温度・基板入力インピーダンスを含む試験と、複数チップでのHD2/HD3分布を優先する。"),
       ("パケットを壊さないOSR切替でも、新しい設定での出力期限を超えた。","改版ではCSがアイドルの間に切替を受理できる条件を定義する。全旧位相を総当たりし、最初の新フレームの開始と完了を別々に検証する。"),
       ("単発バブルの影響と継続的な異常を区別する。","第1積分器の定数差・第2積分器のランプ差は2階差分で消える。単発事象の復帰に再初期化は不要（p.23）。"),
       ("短い無雑音過渡と仮定したFoMは実機SNDRを確定しない。","低歪み信号源で長いSPIコード列を取得し、入力振幅・周波数・バイアス別にSNDRを確認する。発振分周出力から電源注入の引き込み範囲も測る。")],[202,CW-202],9.2)
    y=d.sub(y+17,"初回シリコンの測定順")
    for idx,txt in enumerate(["p.29の順に通電。p.30の電流窓、p.28の分周出力とクロック条件を順に確認する。","実測Vosを特定し、その前後±1、±3、±10 mVを負側・正側から往復する（p.7）。","高温でHD3が悪化したら、Vdiff固定でVcmを+50、+100 mVに変え、利得・HD3・fP/Nを再測定。改善の向きは実測する。","SPIビット化けはピン上のSCLK/SDOと受信タイミングを先に確認。内部ホールド余裕は+0.07 nsで、低速化では救えない。使用基板で独立調整が許される1.8 V枝だけを1.70／1.90 Vに変え、同一クロック・入力・温度で比較する。"],1):
        d.txt(LEFT,y,f"{idx:02d}",11,"JB",TEAL);y=d.p(LEFT+35,y,txt,CW-35,9.6,17)+12
def trace(d):
    d.start("付録","データの読み方と追跡方法","個別ケースの判定と波形データを、同じ設計・入力条件までさかのぼれるようにした。")
    y=d.table(153,["レポートZIP内の資料","利用方法"],[
      ("design_report.pdf","本書。回路図はベクトル図、レイアウト図は最終GDSの実形状。"),
      ("waveforms/*.csv.gz","アナログはtime_sと電圧[V]・電流[A]。ngspiceの可変時間刻みを保持し、有効数字9桁で出力。T6は20 MHzゲート出力と同じクロックの入力値。"),
      ("waveforms/index.json","各ケースの保存列、サンプル数、時刻範囲。T1は左右各15段のA・B、全60内部ノードを収録。"),
      ("measurements/*.json","T1全30段、T2電流、T3の16コード、T4のHD3、T5位相、T6の各操作別待ち時間。"),
      ("spectra/、analysis/","T3の復号フレームと各ビン電力、A5の長時間モデル出力コードとスペクトラム。analysis/spectra.pyで同梱データから再計算（NumPy・Matplotlib）。"),
      ("bench/、baseline/、design/","初日電流の9条件、バイアス・受動素子・GDS追跡の数値、雑音内訳をbench/に収録。baseline/に静特性等、design/にGDS・抽出SPICE・RTL、figures/に図を収録。"),
      ("SHA256SUMS","全収録メンバーのSHA-256。提出ZIPは別途、設計ソース・デッキ・各試験の実行手順を収録。")],[172,CW-172],9)
    y=d.sub(y+22,"再現条件")
    d.p(LEFT,y,"アナログはngspice 42とSKY130Aの素子・容量抽出モデル、デジタルはIcarus Verilog 12.0と標準セル機能モデルで評価した。各タップに5 fFの受信負荷と、タイルから抽出した配線容量行列を加えた。回路内の配線は等電位とし、T3でのみ外部電源・接地の直列インピーダンスを明示した。",size=9.7,leading=18)
    y+=109;d.txt(LEFT,y,"最終GDS  SHA-256",9,"JB",TEAL);d.txt(LEFT,y+20,"cbd199e4c27bd935dadd77fba74fee3222b007abc97d0b8967c3100e1abd0286",8.3)
    d.txt(LEFT,y+52,"アナログ抽出SPICE  SHA-256",9,"JB",TEAL);d.txt(LEFT,y+72,"ed36d6c519af4741a31c725f25a2e5b1c137f011aae624b7b618540125e7fe63",8.3)
def summary(d):
    manifest=obj("manifest")
    d.start("検証判定","T1〜T6 判定一覧","表の判定は各試験の指定条件に対するもの。製造検査とシリコンの保証値は別途扱う。")
    t2=obj("T2_leak");b=obj("T2_brown");c=obj("T3_clean");n=obj("T3_dirty");t4=obj("T4_step");m=obj("T5_0_0");s=obj("T6")["rtl"]
    a1=[obj(f"T1_{k}_{v}")["status"] for k in ("tt","ss","ff","sf","fs") for v in (0,1)]
    y=d.table(155,["試験","判定","判定を決めた観測"],[
      ("T1　完全同相起動",manifest["results"]["T1"],f"5コーナー×2バイアスで{a1.count('PASS')}/10条件が10周期内に全段逆相。"),
      ("T2　電源とリーク",manifest["results"]["T2"],f"10 msランプと0.6 V・50 µs瞬断を実行。FF高温のOFF側電流は最大{max(x['off_nA'] for x in t2['banks'].values()):.2f} nA。"),
      ("T3　電源電流注入",manifest["results"]["T3"],f"配線後ゲートSPIの16点SNDRは基準 {obj('T3_gate')['clean_sndr_dB']:.2f} dB、注入 {obj('T3_gate')['dirty_sndr_dB']:.2f} dB。8通りの標本化位相も検査。"),
      ("T4　入力外乱",manifest["results"]["T4"],f"過入力復帰は最大{max(t4['recovery_cycles']):.2f}周期。2種類のRC接続で抵抗によるHD3差を比較。"),
      ("T5　結合マージン",manifest["results"]["T5"],f"零入力から+1 mVに切り替えると、実装4.1989 fFでの位相変動は160 µsに {obj('T5_hold')['relative_phase_span_cycles']:.4f} 周期。線形領域の予想1.104周期。"),
      ("T6　RTL異常系",manifest["results"]["T6"],f"形式異常0件。256→128切替の新フレーム完了は最長{max(v['spi_complete_clocks'] for v in s['mode_changes'] if v['osr']==128)} clk、許容256 clk。")],[115,107,CW-222],9)
    y=d.sub(y+23,"この結果をどう使うか")
    d.p(LEFT,y,"製造ルール、LVS、通常のSPI動作を通過したマスクを初回試作に用いる。微小信号の線形性や動作中のOSR変更を前提とする用途には、本書の未達条件を適用する。実機の評価では、電源電流・零点近傍・コードFFTを同じチップで対応付けて記録する。",size=10.3,leading=19)
    d.p(LEFT,y+112,"デジタルセル面積には9,000 µm²の目安に対して36 µm²の余裕がある。今回は既存マスクで試作し、OSRはリセット中に選ぶ。設定切替回路を改版する場合は、新しい配線で面積・タイミング・DRC・LVSを再確認する。",size=9.5,leading=17,color=MUTE)
if __name__=="__main__":
    from report29 import render
    ap=argparse.ArgumentParser()
    ap.add_argument("--preview",action="store_true")
    opt=ap.parse_args()
    path=ROOT/("tmp/pdfs/preview.pdf" if opt.preview else "output/pdf/SKY26e_CCRO_ADC_Design_Report.pdf")
    render(path)
    print(path)
