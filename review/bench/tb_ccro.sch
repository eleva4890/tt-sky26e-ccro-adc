v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Differential CCRO   /   transistor-level transient} 30 0 0 0 0.62 0.62 {}
T {TT at 27 C   |   1 us supply ramp   |   nominal bias 00   |   editable differential input} 30 54 0 0 0.35 0.35 {}
T {Supply and pin stimulus} 30 130 0 0 0.46 0.46 {}
C {devices/vsource.sym} 95 255 0 0 {name=VDD value="PWL(0 0 1u 'vsup')"}
N 95 225 95 205 {lab=vdd}
C {devices/lab_pin.sym} 95 205 0 0 {name=l1 lab=vdd}
N 95 285 95 305 {lab=0}
C {devices/lab_pin.sym} 95 305 0 0 {name=l2 lab=0}
C {devices/vcvs.sym} 325 255 0 0 {name=Epos value="'(vcm+vdiff/2)/vsup'"}
C {devices/lab_pin.sym} 285 235 0 0 {name=l3 lab=vdd}
C {devices/lab_pin.sym} 285 275 0 0 {name=l4 lab=0}
N 325 225 325 205 {lab=ep}
C {devices/lab_pin.sym} 325 205 0 0 {name=l5 lab=ep}
N 325 285 325 305 {lab=0}
C {devices/lab_pin.sym} 325 305 0 0 {name=l6 lab=0}
C {devices/vcvs.sym} 570 255 0 0 {name=Eneg value="'(vcm-vdiff/2)/vsup'"}
C {devices/lab_pin.sym} 530 235 0 0 {name=l7 lab=vdd}
C {devices/lab_pin.sym} 530 275 0 0 {name=l8 lab=0}
N 570 225 570 205 {lab=en}
C {devices/lab_pin.sym} 570 205 0 0 {name=l9 lab=en}
N 570 285 570 305 {lab=0}
C {devices/lab_pin.sym} 570 305 0 0 {name=l10 lab=0}
C {devices/res.sym} 325 420 0 0 {name=Rvinp value=1.5k}
N 325 390 325 370 {lab=ep}
C {devices/lab_pin.sym} 325 370 0 0 {name=l11 lab=ep}
N 325 450 325 490 {lab=vinp}
C {devices/lab_pin.sym} 325 470 0 0 {name=l12 lab=vinp}
C {devices/capa.sym} 325 520 0 0 {name=Cvinp value=5p}
N 325 550 325 570 {lab=0}
C {devices/lab_pin.sym} 325 570 0 0 {name=l13 lab=0}
C {devices/res.sym} 570 420 0 0 {name=Rvinn value=1.5k}
N 570 390 570 370 {lab=en}
C {devices/lab_pin.sym} 570 370 0 0 {name=l14 lab=en}
N 570 450 570 490 {lab=vinn}
C {devices/lab_pin.sym} 570 470 0 0 {name=l15 lab=vinn}
C {devices/capa.sym} 570 520 0 0 {name=Cvinn value=5p}
N 570 550 570 570 {lab=0}
C {devices/lab_pin.sym} 570 570 0 0 {name=l16 lab=0}
T {Supply-tracking bias select} 30 623 0 0 0.39 0.39 {}
C {devices/vcvs.sym} 125 740 0 0 {name=Ebit0 value="'bit0'"}
C {devices/lab_pin.sym} 85 720 0 0 {name=l17 lab=vdd}
C {devices/lab_pin.sym} 85 760 0 0 {name=l18 lab=0}
N 125 710 125 690 {lab=sel0}
C {devices/lab_pin.sym} 125 690 0 0 {name=l19 lab=sel0}
N 125 770 125 790 {lab=0}
C {devices/lab_pin.sym} 125 790 0 0 {name=l20 lab=0}
C {devices/vcvs.sym} 370 740 0 0 {name=Ebit1 value="'bit1'"}
C {devices/lab_pin.sym} 330 720 0 0 {name=l21 lab=vdd}
C {devices/lab_pin.sym} 330 760 0 0 {name=l22 lab=0}
N 370 710 370 690 {lab=sel1}
C {devices/lab_pin.sym} 370 690 0 0 {name=l23 lab=sel1}
N 370 770 370 790 {lab=0}
C {devices/lab_pin.sym} 370 790 0 0 {name=l24 lab=0}
T {Input and bias parameters} 30 862 0 0 0.39 0.39 {}
C {devices/code_shown.sym} 30 926 0 0 {name=STIM only_toplevel=true value=".param vsup=1.80 vcm=0.630 vdiff=0.100
.param bit0=0 bit1=0"}
T {Analog macro} 795 130 0 0 0.46 0.46 {}
C {adc_analog.sym} 930 245 0 0 {name=Xdut}
N 810 245 774 245 {lab=vinp}
C {devices/lab_pin.sym} 774 245 0 0 {name=l25 lab=vinp}
N 810 275 774 275 {lab=vinn}
C {devices/lab_pin.sym} 774 275 0 0 {name=l26 lab=vinn}
N 810 305 774 305 {lab=sel0}
C {devices/lab_pin.sym} 774 305 0 0 {name=l27 lab=sel0}
N 810 335 774 335 {lab=sel1}
C {devices/lab_pin.sym} 774 335 0 0 {name=l28 lab=sel1}
N 810 365 774 365 {lab=vdd}
C {devices/lab_pin.sym} 774 365 0 0 {name=l29 lab=vdd}
N 810 395 774 395 {lab=0}
C {devices/lab_pin.sym} 774 395 0 0 {name=l30 lab=0}
N 810 425 774 425 {lab=p0}
C {devices/lab_pin.sym} 774 425 0 0 {name=l31 lab=p0}
N 810 455 774 455 {lab=pt[1]}
C {devices/lab_pin.sym} 774 455 0 0 {name=l32 lab=pt[1]}
N 810 485 774 485 {lab=pt[2]}
C {devices/lab_pin.sym} 774 485 0 0 {name=l33 lab=pt[2]}
N 810 515 774 515 {lab=pt[3]}
C {devices/lab_pin.sym} 774 515 0 0 {name=l34 lab=pt[3]}
N 810 545 774 545 {lab=pt[4]}
C {devices/lab_pin.sym} 774 545 0 0 {name=l35 lab=pt[4]}
N 810 575 774 575 {lab=pt[5]}
C {devices/lab_pin.sym} 774 575 0 0 {name=l36 lab=pt[5]}
N 810 605 774 605 {lab=pt[6]}
C {devices/lab_pin.sym} 774 605 0 0 {name=l37 lab=pt[6]}
N 810 635 774 635 {lab=pt[7]}
C {devices/lab_pin.sym} 774 635 0 0 {name=l38 lab=pt[7]}
N 810 665 774 665 {lab=pt[8]}
C {devices/lab_pin.sym} 774 665 0 0 {name=l39 lab=pt[8]}
N 810 695 774 695 {lab=pt[9]}
C {devices/lab_pin.sym} 774 695 0 0 {name=l40 lab=pt[9]}
N 810 725 774 725 {lab=pt[10]}
C {devices/lab_pin.sym} 774 725 0 0 {name=l41 lab=pt[10]}
N 810 755 774 755 {lab=pt[11]}
C {devices/lab_pin.sym} 774 755 0 0 {name=l42 lab=pt[11]}
N 1050 245 1086 245 {lab=pt[12]}
C {devices/lab_pin.sym} 1086 245 0 1 {name=l43 lab=pt[12]}
N 1050 275 1086 275 {lab=pt[13]}
C {devices/lab_pin.sym} 1086 275 0 1 {name=l44 lab=pt[13]}
N 1050 305 1086 305 {lab=pt[14]}
C {devices/lab_pin.sym} 1086 305 0 1 {name=l45 lab=pt[14]}
N 1050 335 1086 335 {lab=n0}
C {devices/lab_pin.sym} 1086 335 0 1 {name=l46 lab=n0}
N 1050 365 1086 365 {lab=nt[1]}
C {devices/lab_pin.sym} 1086 365 0 1 {name=l47 lab=nt[1]}
N 1050 395 1086 395 {lab=nt[2]}
C {devices/lab_pin.sym} 1086 395 0 1 {name=l48 lab=nt[2]}
N 1050 425 1086 425 {lab=nt[3]}
C {devices/lab_pin.sym} 1086 425 0 1 {name=l49 lab=nt[3]}
N 1050 455 1086 455 {lab=nt[4]}
C {devices/lab_pin.sym} 1086 455 0 1 {name=l50 lab=nt[4]}
N 1050 485 1086 485 {lab=nt[5]}
C {devices/lab_pin.sym} 1086 485 0 1 {name=l51 lab=nt[5]}
N 1050 515 1086 515 {lab=nt[6]}
C {devices/lab_pin.sym} 1086 515 0 1 {name=l52 lab=nt[6]}
N 1050 545 1086 545 {lab=nt[7]}
C {devices/lab_pin.sym} 1086 545 0 1 {name=l53 lab=nt[7]}
N 1050 575 1086 575 {lab=nt[8]}
C {devices/lab_pin.sym} 1086 575 0 1 {name=l54 lab=nt[8]}
N 1050 605 1086 605 {lab=nt[9]}
C {devices/lab_pin.sym} 1086 605 0 1 {name=l55 lab=nt[9]}
N 1050 635 1086 635 {lab=nt[10]}
C {devices/lab_pin.sym} 1086 635 0 1 {name=l56 lab=nt[10]}
N 1050 665 1086 665 {lab=nt[11]}
C {devices/lab_pin.sym} 1086 665 0 1 {name=l57 lab=nt[11]}
N 1050 695 1086 695 {lab=nt[12]}
C {devices/lab_pin.sym} 1086 695 0 1 {name=l58 lab=nt[12]}
N 1050 725 1086 725 {lab=nt[13]}
C {devices/lab_pin.sym} 1086 725 0 1 {name=l59 lab=nt[13]}
N 1050 755 1086 755 {lab=nt[14]}
C {devices/lab_pin.sym} 1086 755 0 1 {name=l60 lab=nt[14]}
T {Receiver loads   /   5 fF per tap} 670 860 0 0 0.39 0.39 {}
C {devices/capa.sym} 700 965 0 0 {name=CP0 value=5f}
N 700 935 700 915 {lab=p0}
C {devices/lab_pin.sym} 700 915 0 0 {name=l61 lab=p0}
N 700 995 700 1015 {lab=0}
C {devices/lab_pin.sym} 700 1015 0 0 {name=l62 lab=0}
C {devices/capa.sym} 845 965 0 0 {name=CN0 value=5f}
N 845 935 845 915 {lab=n0}
C {devices/lab_pin.sym} 845 915 0 0 {name=l63 lab=n0}
N 845 995 845 1015 {lab=0}
C {devices/lab_pin.sym} 845 1015 0 0 {name=l64 lab=0}
C {devices/capa.sym} 990 965 0 0 {name=CP[1:14] value=5f}
N 990 935 990 915 {lab=pt[1:14]}
C {devices/lab_pin.sym} 990 915 0 0 {name=l65 lab=pt[1:14]}
N 990 995 990 1015 {lab=0}
C {devices/lab_pin.sym} 990 1015 0 0 {name=l66 lab=0}
C {devices/capa.sym} 1150 965 0 0 {name=CN[1:14] value=5f}
N 1150 935 1150 915 {lab=nt[1:14]}
C {devices/lab_pin.sym} 1150 915 0 0 {name=l67 lab=nt[1:14]}
N 1150 995 1150 1015 {lab=0}
C {devices/lab_pin.sym} 1150 1015 0 0 {name=l68 lab=0}
T {Startup   /   supply and bias [V]} 1270 132 0 0 0.42 0.42 {}
B 2 1270 195 1950 440 {flags=graph,unlocked
x1=0 x2=8e-06 y1=0 y2=1.95
divx=5 divy=4 subdivx=2 subdivy=1
unitx=u
node="v(vdd)
v(xdut.xf.vb)
v(xdut.rp)
v(xdut.rn)"
color="4 7 8 6"
dataset=-1}
T {CVSL outputs   /   P and N tap 0 [V]} 1270 488 0 0 0.42 0.42 {}
B 2 1270 550 1950 795 {flags=graph,unlocked
x1=5e-06 x2=6e-06 y1=-0.15 y2=1.95
divx=5 divy=4 subdivx=2 subdivy=1
unitx=u
node="v(p0)
v(n0)"
color="8 6"
dataset=-1}
C {devices/launcher.sym} 1310 875 0 0 {name=load_traces descr="Load transient waveforms" tclcommand="ccro_load_traces"}
C {devices/launcher.sym} 1700 875 0 0 {name=show_log descr="Open measurements" tclcommand="textwindow [file join $netlist_dir tb_ccro.log] ro"}
T {Netlist, then Simulate. After completion, Ctrl-click the arrow.} 1270 940 0 0 0.32 0.32 {}
T {Open the measurement log for fP, fN, fP - fN and supply current.} 1270 980 0 0 0.3 0.3 {}
C {sky130_fd_pr/corner.sym} 35 1110 0 0 {name=CORNER only_toplevel=true corner=tt}
C {devices/code.sym} 320 1110 0 0 {name=TRANSIENT only_toplevel=true value=".option scale=1u method=gear reltol=0.0005
.temp 27
.csparam stop_s='8u+22u*bit0*(1-bit1)'
.control
set num_threads=1
save v(vdd) v(vinp) v(vinn) v(xdut.xf.vb) v(xdut.rp) v(xdut.rn) v(p0) v(n0) i(vdd)
set tstop = $&stop_s
tran 2n $tstop 0 2n
if time[length(time)-1] < 0.999999*$tstop
  echo Incomplete transient
  quit 2
end
meas tran period2p TRIG v(p0) VAL=0.9 TD=5u RISE=1 TARG v(p0) VAL=0.9 TD=5u RISE=3
meas tran period2n TRIG v(n0) VAL=0.9 TD=5u RISE=1 TARG v(n0) VAL=0.9 TD=5u RISE=3
meas tran supply_a AVG i(vdd) FROM=5u TO=$tstop
let fp_mhz = 2e-6/period2p
let fn_mhz = 2e-6/period2n
let delta_mhz = fp_mhz-fn_mhz
let idd_ua = -1e6*supply_a
print fp_mhz fn_mhz delta_mhz idd_ua
write tb_ccro.raw time v(vdd) v(vinp) v(vinn) v(xdut.xf.vb) v(xdut.rp) v(xdut.rn) v(p0) v(n0) i(vdd)
quit
.endc"}
T {Simulation settings} 295 1062 0 0 0.3 0.3 {}
