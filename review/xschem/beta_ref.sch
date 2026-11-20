v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Beta multiplier and start-up branch} 0 0 0 0 0.62 0.62 {}
T {Sheet terminals} 0 60 0 0 0.32 0.32 {layer=13}
C {devices/iopin.sym} 0 110 0 0 {name=io0 lab=vb sim_pinnumber=1}
C {devices/iopin.sym} 150 110 0 0 {name=io1 lab=v sim_pinnumber=2}
C {devices/iopin.sym} 300 110 0 0 {name=io2 lab=g sim_pinnumber=3}
N 200 305 200 370 {lab=vb}
N 200 370 200 435 {lab=vb}
N 200 370 260 370 {lab=vb}
C {devices/lab_pin.sym} 260 370 0 1 {name=drain0 lab=vb}
N 620 305 620 370 {lab=vn}
N 620 370 620 435 {lab=vn}
N 620 370 680 370 {lab=vn}
C {devices/lab_pin.sym} 680 370 0 1 {name=drain1 lab=vn}
N 1040 305 1040 370 {lab=kick}
N 1040 370 1040 435 {lab=kick}
N 1040 370 1100 370 {lab=kick}
C {devices/lab_pin.sym} 1100 370 0 1 {name=drain2 lab=kick}
C {sky130_fd_pr/pfet_01v8.sym} 180 275 0 0 {name=Mp0 W=2 L=2}
N 125 275 160 275 {lab=vb}
C {devices/lab_pin.sym} 125 275 0 0 {name=net0 lab=vb}
N 200 210 200 245 {lab=v}
N 175 210 200 210 {lab=v}
C {devices/lab_pin.sym} 175 210 0 0 {name=net1 lab=v}
N 200 275 210 275 {lab=v}
N 210 275 210 318 {lab=v}
N 210 318 270 318 {lab=v}
C {devices/lab_pin.sym} 270 318 0 1 {name=net2 lab=v}
C {sky130_fd_pr/nfet_01v8.sym} 600 465 0 0 {name=Mn0 W=2 L=2}
N 545 465 580 465 {lab=vn}
C {devices/lab_pin.sym} 545 465 0 0 {name=net3 lab=vn}
N 620 495 620 530 {lab=g}
N 595 530 620 530 {lab=g}
C {devices/lab_pin.sym} 595 530 0 0 {name=net4 lab=g}
N 620 465 630 465 {lab=g}
N 630 465 630 508 {lab=g}
N 630 508 690 508 {lab=g}
C {devices/lab_pin.sym} 690 508 0 1 {name=net5 lab=g}
C {sky130_fd_pr/pfet_01v8.sym} 600 275 0 0 {name=Mp1 W=2 L=2}
N 545 275 580 275 {lab=vb}
C {devices/lab_pin.sym} 545 275 0 0 {name=net6 lab=vb}
N 620 210 620 245 {lab=v}
N 595 210 620 210 {lab=v}
C {devices/lab_pin.sym} 595 210 0 0 {name=net7 lab=v}
N 620 275 630 275 {lab=v}
N 630 275 630 318 {lab=v}
N 630 318 690 318 {lab=v}
C {devices/lab_pin.sym} 690 318 0 1 {name=net8 lab=v}
C {sky130_fd_pr/nfet_01v8.sym} 180 465 0 0 {name=Mn1 W=8 L=2}
N 125 465 160 465 {lab=vn}
C {devices/lab_pin.sym} 125 465 0 0 {name=net9 lab=vn}
N 200 495 200 530 {lab=rs}
N 175 530 200 530 {lab=rs}
C {devices/lab_pin.sym} 175 530 0 0 {name=net10 lab=rs}
N 200 465 210 465 {lab=g}
N 210 465 210 508 {lab=g}
N 210 508 270 508 {lab=g}
C {devices/lab_pin.sym} 270 508 0 1 {name=net11 lab=g}
C {sky130_fd_pr/res_high_po_0p69.sym} 180 755 0 0 {name=Rref0 L=97.1}
N 180 785 180 820 {lab=rs}
N 155 820 180 820 {lab=rs}
C {devices/lab_pin.sym} 155 820 0 0 {name=net12 lab=rs}
N 180 690 180 725 {lab=refmid}
N 155 690 180 690 {lab=refmid}
C {devices/lab_pin.sym} 155 690 0 0 {name=net13 lab=refmid}
N 125 755 160 755 {lab=g}
C {devices/lab_pin.sym} 125 755 0 0 {name=net14 lab=g}
C {sky130_fd_pr/res_high_po_0p69.sym} 600 755 0 0 {name=Rref1 L=97.1}
N 600 785 600 820 {lab=refmid}
N 575 820 600 820 {lab=refmid}
C {devices/lab_pin.sym} 575 820 0 0 {name=net15 lab=refmid}
N 600 690 600 725 {lab=g}
N 575 690 600 690 {lab=g}
C {devices/lab_pin.sym} 575 690 0 0 {name=net16 lab=g}
N 545 755 580 755 {lab=g}
C {devices/lab_pin.sym} 545 755 0 0 {name=net17 lab=g}
C {sky130_fd_pr/pfet_01v8.sym} 1020 275 0 0 {name=Mweak W=.42 L=12}
N 965 275 1000 275 {lab=g}
C {devices/lab_pin.sym} 965 275 0 0 {name=net18 lab=g}
N 1040 210 1040 245 {lab=v}
N 1015 210 1040 210 {lab=v}
C {devices/lab_pin.sym} 1015 210 0 0 {name=net19 lab=v}
N 1040 275 1050 275 {lab=v}
N 1050 275 1050 318 {lab=v}
N 1050 318 1110 318 {lab=v}
C {devices/lab_pin.sym} 1110 318 0 1 {name=net20 lab=v}
C {sky130_fd_pr/nfet_01v8_lvt.sym} 1020 465 0 0 {name=Msense W=5 L=.15}
N 965 465 1000 465 {lab=vn}
C {devices/lab_pin.sym} 965 465 0 0 {name=net21 lab=vn}
N 1040 495 1040 530 {lab=g}
N 1015 530 1040 530 {lab=g}
C {devices/lab_pin.sym} 1015 530 0 0 {name=net22 lab=g}
N 1040 465 1050 465 {lab=g}
N 1050 465 1050 508 {lab=g}
N 1050 508 1110 508 {lab=g}
C {devices/lab_pin.sym} 1110 508 0 1 {name=net23 lab=g}
C {sky130_fd_pr/nfet_01v8.sym} 1020 755 0 0 {name=Mkick W=.5 L=1}
N 1040 690 1040 725 {lab=vb}
N 1015 690 1040 690 {lab=vb}
C {devices/lab_pin.sym} 1015 690 0 0 {name=net24 lab=vb}
N 965 755 1000 755 {lab=kick}
C {devices/lab_pin.sym} 965 755 0 0 {name=net25 lab=kick}
N 1040 785 1040 820 {lab=g}
N 1015 820 1040 820 {lab=g}
C {devices/lab_pin.sym} 1015 820 0 0 {name=net26 lab=g}
N 1040 755 1050 755 {lab=g}
N 1050 755 1050 798 {lab=g}
N 1050 798 1110 798 {lab=g}
C {devices/lab_pin.sym} 1110 798 0 1 {name=net27 lab=g}
