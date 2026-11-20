v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Split-tail input and ring reservoirs} 0 0 0 0 0.62 0.62 {}
T {Sheet terminals} 0 60 0 0 0.32 0.32 {layer=13}
C {devices/iopin.sym} 0 110 0 0 {name=io0 lab=vinp sim_pinnumber=1}
C {devices/iopin.sym} 150 110 0 0 {name=io1 lab=vinn sim_pinnumber=2}
C {devices/iopin.sym} 300 110 0 0 {name=io2 lab=b0 sim_pinnumber=3}
C {devices/iopin.sym} 450 110 0 0 {name=io3 lab=b1 sim_pinnumber=4}
C {devices/iopin.sym} 600 110 0 0 {name=io4 lab=rp sim_pinnumber=5}
C {devices/iopin.sym} 750 110 0 0 {name=io5 lab=rn sim_pinnumber=6}
C {devices/iopin.sym} 900 110 0 0 {name=io6 lab=v sim_pinnumber=7}
C {devices/iopin.sym} 1050 110 0 0 {name=io7 lab=g sim_pinnumber=8}
C {bias.sym} 180 275 0 0 {name=Xbias}
N 25 275 60 275 {lab=b0}
C {devices/lab_pin.sym} 25 275 0 0 {name=net0 lab=b0}
N 25 305 60 305 {lab=b1}
C {devices/lab_pin.sym} 25 305 0 0 {name=net1 lab=b1}
N 25 335 60 335 {lab=vb}
C {devices/lab_pin.sym} 25 335 0 0 {name=net2 lab=vb}
N 25 365 60 365 {lab=g4}
C {devices/lab_pin.sym} 25 365 0 0 {name=net3 lab=g4}
N 300 275 335 275 {lab=g15}
C {devices/lab_pin.sym} 335 275 0 1 {name=net4 lab=g15}
N 300 305 335 305 {lab=g20}
C {devices/lab_pin.sym} 335 305 0 1 {name=net5 lab=g20}
N 300 335 335 335 {lab=v}
C {devices/lab_pin.sym} 335 335 0 1 {name=net6 lab=v}
N 300 365 335 365 {lab=g}
C {devices/lab_pin.sym} 335 365 0 1 {name=net7 lab=g}
C {tail.sym} 675 275 0 0 {name=Xtailp}
N 520 275 555 275 {lab=sp}
C {devices/lab_pin.sym} 520 275 0 0 {name=net8 lab=sp}
N 520 305 555 305 {lab=vb}
C {devices/lab_pin.sym} 520 305 0 0 {name=net9 lab=vb}
N 520 335 555 335 {lab=g4}
C {devices/lab_pin.sym} 520 335 0 0 {name=net10 lab=g4}
N 795 275 830 275 {lab=g15}
C {devices/lab_pin.sym} 830 275 0 1 {name=net11 lab=g15}
N 795 305 830 305 {lab=g20}
C {devices/lab_pin.sym} 830 305 0 1 {name=net12 lab=g20}
N 795 335 830 335 {lab=v}
C {devices/lab_pin.sym} 830 335 0 1 {name=net13 lab=v}
C {tail.sym} 1170 275 0 0 {name=Xtailn}
N 1015 275 1050 275 {lab=sn}
C {devices/lab_pin.sym} 1015 275 0 0 {name=net14 lab=sn}
N 1015 305 1050 305 {lab=vb}
C {devices/lab_pin.sym} 1015 305 0 0 {name=net15 lab=vb}
N 1015 335 1050 335 {lab=g4}
C {devices/lab_pin.sym} 1015 335 0 0 {name=net16 lab=g4}
N 1290 275 1325 275 {lab=g15}
C {devices/lab_pin.sym} 1325 275 0 1 {name=net17 lab=g15}
N 1290 305 1325 305 {lab=g20}
C {devices/lab_pin.sym} 1325 305 0 1 {name=net18 lab=g20}
N 1290 335 1325 335 {lab=v}
C {devices/lab_pin.sym} 1325 335 0 1 {name=net19 lab=v}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 180 545 0 0 {name=Minp0 W=6 L=1}
N 200 575 200 610 {lab=rp}
N 175 610 200 610 {lab=rp}
C {devices/lab_pin.sym} 175 610 0 0 {name=net20 lab=rp}
N 125 545 160 545 {lab=vinn}
C {devices/lab_pin.sym} 125 545 0 0 {name=net21 lab=vinn}
N 200 480 200 515 {lab=sp}
N 175 480 200 480 {lab=sp}
C {devices/lab_pin.sym} 175 480 0 0 {name=net22 lab=sp}
N 200 545 210 545 {lab=sp}
N 210 545 210 588 {lab=sp}
N 210 588 270 588 {lab=sp}
C {devices/lab_pin.sym} 270 588 0 1 {name=net23 lab=sp}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 675 545 0 0 {name=Minp1 W=6 L=1}
N 695 575 695 610 {lab=rp}
N 670 610 695 610 {lab=rp}
C {devices/lab_pin.sym} 670 610 0 0 {name=net24 lab=rp}
N 620 545 655 545 {lab=vinn}
C {devices/lab_pin.sym} 620 545 0 0 {name=net25 lab=vinn}
N 695 480 695 515 {lab=sp}
N 670 480 695 480 {lab=sp}
C {devices/lab_pin.sym} 670 480 0 0 {name=net26 lab=sp}
N 695 545 705 545 {lab=sp}
N 705 545 705 588 {lab=sp}
N 705 588 765 588 {lab=sp}
C {devices/lab_pin.sym} 765 588 0 1 {name=net27 lab=sp}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 1170 545 0 0 {name=Minp2 W=6 L=1}
N 1190 575 1190 610 {lab=rp}
N 1165 610 1190 610 {lab=rp}
C {devices/lab_pin.sym} 1165 610 0 0 {name=net28 lab=rp}
N 1115 545 1150 545 {lab=vinn}
C {devices/lab_pin.sym} 1115 545 0 0 {name=net29 lab=vinn}
N 1190 480 1190 515 {lab=sp}
N 1165 480 1190 480 {lab=sp}
C {devices/lab_pin.sym} 1165 480 0 0 {name=net30 lab=sp}
N 1190 545 1200 545 {lab=sp}
N 1200 545 1200 588 {lab=sp}
N 1200 588 1260 588 {lab=sp}
C {devices/lab_pin.sym} 1260 588 0 1 {name=net31 lab=sp}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 180 785 0 0 {name=Minp3 W=6 L=1}
N 200 815 200 850 {lab=rp}
N 175 850 200 850 {lab=rp}
C {devices/lab_pin.sym} 175 850 0 0 {name=net32 lab=rp}
N 125 785 160 785 {lab=vinn}
C {devices/lab_pin.sym} 125 785 0 0 {name=net33 lab=vinn}
N 200 720 200 755 {lab=sp}
N 175 720 200 720 {lab=sp}
C {devices/lab_pin.sym} 175 720 0 0 {name=net34 lab=sp}
N 200 785 210 785 {lab=sp}
N 210 785 210 828 {lab=sp}
N 210 828 270 828 {lab=sp}
C {devices/lab_pin.sym} 270 828 0 1 {name=net35 lab=sp}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 675 785 0 0 {name=Minn0 W=6 L=1}
N 695 815 695 850 {lab=rn}
N 670 850 695 850 {lab=rn}
C {devices/lab_pin.sym} 670 850 0 0 {name=net36 lab=rn}
N 620 785 655 785 {lab=vinp}
C {devices/lab_pin.sym} 620 785 0 0 {name=net37 lab=vinp}
N 695 720 695 755 {lab=sn}
N 670 720 695 720 {lab=sn}
C {devices/lab_pin.sym} 670 720 0 0 {name=net38 lab=sn}
N 695 785 705 785 {lab=sn}
N 705 785 705 828 {lab=sn}
N 705 828 765 828 {lab=sn}
C {devices/lab_pin.sym} 765 828 0 1 {name=net39 lab=sn}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 1170 785 0 0 {name=Minn1 W=6 L=1}
N 1190 815 1190 850 {lab=rn}
N 1165 850 1190 850 {lab=rn}
C {devices/lab_pin.sym} 1165 850 0 0 {name=net40 lab=rn}
N 1115 785 1150 785 {lab=vinp}
C {devices/lab_pin.sym} 1115 785 0 0 {name=net41 lab=vinp}
N 1190 720 1190 755 {lab=sn}
N 1165 720 1190 720 {lab=sn}
C {devices/lab_pin.sym} 1165 720 0 0 {name=net42 lab=sn}
N 1190 785 1200 785 {lab=sn}
N 1200 785 1200 828 {lab=sn}
N 1200 828 1260 828 {lab=sn}
C {devices/lab_pin.sym} 1260 828 0 1 {name=net43 lab=sn}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 180 1025 0 0 {name=Minn2 W=6 L=1}
N 200 1055 200 1090 {lab=rn}
N 175 1090 200 1090 {lab=rn}
C {devices/lab_pin.sym} 175 1090 0 0 {name=net44 lab=rn}
N 125 1025 160 1025 {lab=vinp}
C {devices/lab_pin.sym} 125 1025 0 0 {name=net45 lab=vinp}
N 200 960 200 995 {lab=sn}
N 175 960 200 960 {lab=sn}
C {devices/lab_pin.sym} 175 960 0 0 {name=net46 lab=sn}
N 200 1025 210 1025 {lab=sn}
N 210 1025 210 1068 {lab=sn}
N 210 1068 270 1068 {lab=sn}
C {devices/lab_pin.sym} 270 1068 0 1 {name=net47 lab=sn}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 675 1025 0 0 {name=Minn3 W=6 L=1}
N 695 1055 695 1090 {lab=rn}
N 670 1090 695 1090 {lab=rn}
C {devices/lab_pin.sym} 670 1090 0 0 {name=net48 lab=rn}
N 620 1025 655 1025 {lab=vinp}
C {devices/lab_pin.sym} 620 1025 0 0 {name=net49 lab=vinp}
N 695 960 695 995 {lab=sn}
N 670 960 695 960 {lab=sn}
C {devices/lab_pin.sym} 670 960 0 0 {name=net50 lab=sn}
N 695 1025 705 1025 {lab=sn}
N 705 1025 705 1068 {lab=sn}
N 705 1068 765 1068 {lab=sn}
C {devices/lab_pin.sym} 765 1068 0 1 {name=net51 lab=sn}
C {sky130_fd_pr/res_high_po_0p69.sym} 1170 1025 0 0 {name=Rr0 L=80}
N 1170 1055 1170 1090 {lab=sp}
N 1145 1090 1170 1090 {lab=sp}
C {devices/lab_pin.sym} 1145 1090 0 0 {name=net52 lab=sp}
N 1170 960 1170 995 {lab=mid}
N 1145 960 1170 960 {lab=mid}
C {devices/lab_pin.sym} 1145 960 0 0 {name=net53 lab=mid}
N 1115 1025 1150 1025 {lab=g}
C {devices/lab_pin.sym} 1115 1025 0 0 {name=net54 lab=g}
C {sky130_fd_pr/res_high_po_0p69.sym} 180 1265 0 0 {name=Rr1 L=80}
N 180 1295 180 1330 {lab=mid}
N 155 1330 180 1330 {lab=mid}
C {devices/lab_pin.sym} 155 1330 0 0 {name=net55 lab=mid}
N 180 1200 180 1235 {lab=sn}
N 155 1200 180 1200 {lab=sn}
C {devices/lab_pin.sym} 155 1200 0 0 {name=net56 lab=sn}
N 125 1265 160 1265 {lab=g}
C {devices/lab_pin.sym} 125 1265 0 0 {name=net57 lab=g}
C {sky130_fd_pr/cap_mim_m3_1.sym} 675 1265 0 0 {name=CcapP W=21.8 L=21.8}
N 675 1200 675 1235 {lab=rp}
N 650 1200 675 1200 {lab=rp}
C {devices/lab_pin.sym} 650 1200 0 0 {name=net58 lab=rp}
N 675 1295 675 1330 {lab=g}
N 650 1330 675 1330 {lab=g}
C {devices/lab_pin.sym} 650 1330 0 0 {name=net59 lab=g}
C {sky130_fd_pr/cap_mim_m3_1.sym} 1170 1265 0 0 {name=CcapN W=21.8 L=21.8}
N 1170 1200 1170 1235 {lab=rn}
N 1145 1200 1170 1200 {lab=rn}
C {devices/lab_pin.sym} 1145 1200 0 0 {name=net60 lab=rn}
N 1170 1295 1170 1330 {lab=g}
N 1145 1330 1170 1330 {lab=g}
C {devices/lab_pin.sym} 1145 1330 0 0 {name=net61 lab=g}
