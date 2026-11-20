v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Main inverters, cross-couplers and MIM loads} 0 0 0 0 0.62 0.62 {}
T {Sheet terminals} 0 60 0 0 0.32 0.32 {layer=13}
C {devices/iopin.sym} 0 110 0 0 {name=io0 lab=a sim_pinnumber=1}
C {devices/iopin.sym} 150 110 0 0 {name=io1 lab=b sim_pinnumber=2}
C {devices/iopin.sym} 300 110 0 0 {name=io2 lab=y sim_pinnumber=3}
C {devices/iopin.sym} 450 110 0 0 {name=io3 lab=z sim_pinnumber=4}
C {devices/iopin.sym} 600 110 0 0 {name=io4 lab=rail sim_pinnumber=5}
C {devices/iopin.sym} 750 110 0 0 {name=io5 lab=g sim_pinnumber=6}
C {devices/iopin.sym} 900 110 0 0 {name=io6 lab=well sim_pinnumber=7}
N 200 305 200 370 {lab=y}
N 200 370 200 435 {lab=y}
N 200 370 260 370 {lab=y}
C {devices/lab_pin.sym} 260 370 0 1 {name=drain0 lab=y}
N 105 275 160 275 {lab=a}
N 105 465 160 465 {lab=a}
N 105 275 105 370 {lab=a}
N 105 370 105 465 {lab=a}
C {devices/lab_pin.sym} 105 370 0 0 {name=gate0 lab=a}
N 620 305 620 370 {lab=z}
N 620 370 620 435 {lab=z}
N 620 370 680 370 {lab=z}
C {devices/lab_pin.sym} 680 370 0 1 {name=drain1 lab=z}
N 525 275 580 275 {lab=b}
N 525 465 580 465 {lab=b}
N 525 275 525 370 {lab=b}
N 525 370 525 465 {lab=b}
C {devices/lab_pin.sym} 525 370 0 0 {name=gate1 lab=b}
N 1040 305 1040 370 {lab=z}
N 1040 370 1040 435 {lab=z}
N 1040 370 1100 370 {lab=z}
C {devices/lab_pin.sym} 1100 370 0 1 {name=drain2 lab=z}
N 945 275 1000 275 {lab=y}
N 945 465 1000 465 {lab=y}
N 945 275 945 370 {lab=y}
N 945 370 945 465 {lab=y}
C {devices/lab_pin.sym} 945 370 0 0 {name=gate2 lab=y}
N 1460 305 1460 370 {lab=y}
N 1460 370 1460 435 {lab=y}
N 1460 370 1520 370 {lab=y}
C {devices/lab_pin.sym} 1520 370 0 1 {name=drain3 lab=y}
N 1365 275 1420 275 {lab=z}
N 1365 465 1420 465 {lab=z}
N 1365 275 1365 370 {lab=z}
N 1365 370 1365 465 {lab=z}
C {devices/lab_pin.sym} 1365 370 0 0 {name=gate3 lab=z}
C {sky130_fd_pr/cap_mim_m3_1.sym} 180 755 0 0 {name=Cca W=4.5 L=4.5}
N 180 690 180 725 {lab=g}
N 155 690 180 690 {lab=g}
C {devices/lab_pin.sym} 155 690 0 0 {name=net0 lab=g}
N 180 785 180 820 {lab=y}
N 155 820 180 820 {lab=y}
C {devices/lab_pin.sym} 155 820 0 0 {name=net1 lab=y}
C {sky130_fd_pr/cap_mim_m3_1.sym} 600 755 0 0 {name=Ccb W=4.5 L=4.5}
N 600 690 600 725 {lab=g}
N 575 690 600 690 {lab=g}
C {devices/lab_pin.sym} 575 690 0 0 {name=net2 lab=g}
N 600 785 600 820 {lab=z}
N 575 820 600 820 {lab=z}
C {devices/lab_pin.sym} 575 820 0 0 {name=net3 lab=z}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 180 275 0 0 {name=MmainA_Xp W=8.4 L=.55}
N 200 210 200 245 {lab=rail}
N 175 210 200 210 {lab=rail}
C {devices/lab_pin.sym} 175 210 0 0 {name=net4 lab=rail}
N 200 275 210 275 {lab=well}
N 210 275 210 318 {lab=well}
N 210 318 270 318 {lab=well}
C {devices/lab_pin.sym} 270 318 0 1 {name=net5 lab=well}
C {sky130_fd_pr/nfet_01v8.sym} 180 465 0 0 {name=MmainA_Xn W=4.2 L=.55}
N 200 495 200 530 {lab=g}
N 175 530 200 530 {lab=g}
C {devices/lab_pin.sym} 175 530 0 0 {name=net6 lab=g}
N 200 465 210 465 {lab=g}
N 210 465 210 508 {lab=g}
N 210 508 270 508 {lab=g}
C {devices/lab_pin.sym} 270 508 0 1 {name=net7 lab=g}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 600 275 0 0 {name=MmainB_Xp W=8.4 L=.55}
N 620 210 620 245 {lab=rail}
N 595 210 620 210 {lab=rail}
C {devices/lab_pin.sym} 595 210 0 0 {name=net8 lab=rail}
N 620 275 630 275 {lab=well}
N 630 275 630 318 {lab=well}
N 630 318 690 318 {lab=well}
C {devices/lab_pin.sym} 690 318 0 1 {name=net9 lab=well}
C {sky130_fd_pr/nfet_01v8.sym} 600 465 0 0 {name=MmainB_Xn W=4.2 L=.55}
N 620 495 620 530 {lab=g}
N 595 530 620 530 {lab=g}
C {devices/lab_pin.sym} 595 530 0 0 {name=net10 lab=g}
N 620 465 630 465 {lab=g}
N 630 465 630 508 {lab=g}
N 630 508 690 508 {lab=g}
C {devices/lab_pin.sym} 690 508 0 1 {name=net11 lab=g}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 1020 275 0 0 {name=McrossA_Xp W=1.68 L=.55}
N 1040 210 1040 245 {lab=rail}
N 1015 210 1040 210 {lab=rail}
C {devices/lab_pin.sym} 1015 210 0 0 {name=net12 lab=rail}
N 1040 275 1050 275 {lab=well}
N 1050 275 1050 318 {lab=well}
N 1050 318 1110 318 {lab=well}
C {devices/lab_pin.sym} 1110 318 0 1 {name=net13 lab=well}
C {sky130_fd_pr/nfet_01v8.sym} 1020 465 0 0 {name=McrossA_Xn W=.84 L=.55}
N 1040 495 1040 530 {lab=g}
N 1015 530 1040 530 {lab=g}
C {devices/lab_pin.sym} 1015 530 0 0 {name=net14 lab=g}
N 1040 465 1050 465 {lab=g}
N 1050 465 1050 508 {lab=g}
N 1050 508 1110 508 {lab=g}
C {devices/lab_pin.sym} 1110 508 0 1 {name=net15 lab=g}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 1440 275 0 0 {name=McrossB_Xp W=1.68 L=.55}
N 1460 210 1460 245 {lab=rail}
N 1435 210 1460 210 {lab=rail}
C {devices/lab_pin.sym} 1435 210 0 0 {name=net16 lab=rail}
N 1460 275 1470 275 {lab=well}
N 1470 275 1470 318 {lab=well}
N 1470 318 1530 318 {lab=well}
C {devices/lab_pin.sym} 1530 318 0 1 {name=net17 lab=well}
C {sky130_fd_pr/nfet_01v8.sym} 1440 465 0 0 {name=McrossB_Xn W=.84 L=.55}
N 1460 495 1460 530 {lab=g}
N 1435 530 1460 530 {lab=g}
C {devices/lab_pin.sym} 1435 530 0 0 {name=net18 lab=g}
N 1460 465 1470 465 {lab=g}
N 1470 465 1470 508 {lab=g}
N 1470 508 1530 508 {lab=g}
C {devices/lab_pin.sym} 1530 508 0 1 {name=net19 lab=g}
