v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Bias reference and static enable decoder} 0 0 0 0 0.62 0.62 {}
T {Sheet terminals} 0 60 0 0 0.32 0.32 {layer=13}
C {devices/iopin.sym} 0 110 0 0 {name=io0 lab=b0 sim_pinnumber=1}
C {devices/iopin.sym} 150 110 0 0 {name=io1 lab=b1 sim_pinnumber=2}
C {devices/iopin.sym} 300 110 0 0 {name=io2 lab=vb sim_pinnumber=3}
C {devices/iopin.sym} 450 110 0 0 {name=io3 lab=g4 sim_pinnumber=4}
C {devices/iopin.sym} 600 110 0 0 {name=io4 lab=g15 sim_pinnumber=5}
C {devices/iopin.sym} 750 110 0 0 {name=io5 lab=g20 sim_pinnumber=6}
C {devices/iopin.sym} 900 110 0 0 {name=io6 lab=v sim_pinnumber=7}
C {devices/iopin.sym} 1050 110 0 0 {name=io7 lab=g sim_pinnumber=8}
N 200 305 200 370 {lab=nb0}
N 200 370 200 435 {lab=nb0}
N 200 370 260 370 {lab=nb0}
C {devices/lab_pin.sym} 260 370 0 1 {name=drain0 lab=nb0}
N 105 275 160 275 {lab=b0}
N 105 465 160 465 {lab=b0}
N 105 275 105 370 {lab=b0}
N 105 370 105 465 {lab=b0}
C {devices/lab_pin.sym} 105 370 0 0 {name=gate0 lab=b0}
N 620 305 620 370 {lab=nb1}
N 620 370 620 435 {lab=nb1}
N 620 370 680 370 {lab=nb1}
C {devices/lab_pin.sym} 680 370 0 1 {name=drain1 lab=nb1}
N 525 275 580 275 {lab=b1}
N 525 465 580 465 {lab=b1}
N 525 275 525 370 {lab=b1}
N 525 370 525 465 {lab=b1}
C {devices/lab_pin.sym} 525 370 0 0 {name=gate1 lab=b1}
N 1040 305 1040 370 {lab=en4}
N 1040 370 1040 435 {lab=en4}
N 1040 370 1100 370 {lab=en4}
C {devices/lab_pin.sym} 1100 370 0 1 {name=drain2 lab=en4}
N 945 275 1000 275 {lab=off4}
N 945 465 1000 465 {lab=off4}
N 945 275 945 370 {lab=off4}
N 945 370 945 465 {lab=off4}
C {devices/lab_pin.sym} 945 370 0 0 {name=gate2 lab=off4}
N 1460 305 1460 370 {lab=en15}
N 1460 370 1460 435 {lab=en15}
N 1460 370 1520 370 {lab=en15}
C {devices/lab_pin.sym} 1520 370 0 1 {name=drain3 lab=en15}
N 1365 275 1420 275 {lab=off15}
N 1365 465 1420 465 {lab=off15}
N 1365 275 1365 370 {lab=off15}
N 1365 370 1365 465 {lab=off15}
C {devices/lab_pin.sym} 1365 370 0 0 {name=gate3 lab=off15}
N 200 785 200 850 {lab=off20}
N 200 850 200 915 {lab=off20}
N 200 850 260 850 {lab=off20}
C {devices/lab_pin.sym} 260 850 0 1 {name=drain4 lab=off20}
N 105 755 160 755 {lab=en20}
N 105 945 160 945 {lab=en20}
N 105 755 105 850 {lab=en20}
N 105 850 105 945 {lab=en20}
C {devices/lab_pin.sym} 105 850 0 0 {name=gate4 lab=en20}
C {beta_ref.sym} 180 1235 0 0 {name=Xreference}
N 25 1235 60 1235 {lab=vb}
C {devices/lab_pin.sym} 25 1235 0 0 {name=net0 lab=vb}
N 25 1265 60 1265 {lab=v}
C {devices/lab_pin.sym} 25 1265 0 0 {name=net1 lab=v}
N 300 1235 335 1235 {lab=g}
C {devices/lab_pin.sym} 335 1235 0 1 {name=net2 lab=g}
C {sky130_fd_pr/pfet_01v8.sym} 180 275 0 0 {name=Mi0p W=.84 L=.15}
N 200 210 200 245 {lab=v}
N 175 210 200 210 {lab=v}
C {devices/lab_pin.sym} 175 210 0 0 {name=net3 lab=v}
N 200 275 210 275 {lab=v}
N 210 275 210 318 {lab=v}
N 210 318 270 318 {lab=v}
C {devices/lab_pin.sym} 270 318 0 1 {name=net4 lab=v}
C {sky130_fd_pr/nfet_01v8.sym} 180 465 0 0 {name=Mi0n W=.42 L=.15}
N 200 495 200 530 {lab=g}
N 175 530 200 530 {lab=g}
C {devices/lab_pin.sym} 175 530 0 0 {name=net5 lab=g}
N 200 465 210 465 {lab=g}
N 210 465 210 508 {lab=g}
N 210 508 270 508 {lab=g}
C {devices/lab_pin.sym} 270 508 0 1 {name=net6 lab=g}
C {sky130_fd_pr/pfet_01v8.sym} 600 275 0 0 {name=Mi1p W=.84 L=.15}
N 620 210 620 245 {lab=v}
N 595 210 620 210 {lab=v}
C {devices/lab_pin.sym} 595 210 0 0 {name=net7 lab=v}
N 620 275 630 275 {lab=v}
N 630 275 630 318 {lab=v}
N 630 318 690 318 {lab=v}
C {devices/lab_pin.sym} 690 318 0 1 {name=net8 lab=v}
C {sky130_fd_pr/nfet_01v8.sym} 600 465 0 0 {name=Mi1n W=.42 L=.15}
N 620 495 620 530 {lab=g}
N 595 530 620 530 {lab=g}
C {devices/lab_pin.sym} 595 530 0 0 {name=net9 lab=g}
N 620 465 630 465 {lab=g}
N 630 465 630 508 {lab=g}
N 630 508 690 508 {lab=g}
C {devices/lab_pin.sym} 690 508 0 1 {name=net10 lab=g}
C {nor2.sym} 600 1235 0 0 {name=Xonlylow}
N 445 1235 480 1235 {lab=nb0}
C {devices/lab_pin.sym} 445 1235 0 0 {name=net11 lab=nb0}
N 445 1265 480 1265 {lab=b1}
C {devices/lab_pin.sym} 445 1265 0 0 {name=net12 lab=b1}
N 445 1295 480 1295 {lab=off4}
C {devices/lab_pin.sym} 445 1295 0 0 {name=net13 lab=off4}
N 720 1235 755 1235 {lab=v}
C {devices/lab_pin.sym} 755 1235 0 1 {name=net14 lab=v}
N 720 1265 755 1265 {lab=g}
C {devices/lab_pin.sym} 755 1265 0 1 {name=net15 lab=g}
C {sky130_fd_pr/pfet_01v8.sym} 1020 275 0 0 {name=Mi4p W=.84 L=.15}
N 1040 210 1040 245 {lab=v}
N 1015 210 1040 210 {lab=v}
C {devices/lab_pin.sym} 1015 210 0 0 {name=net16 lab=v}
N 1040 275 1050 275 {lab=v}
N 1050 275 1050 318 {lab=v}
N 1050 318 1110 318 {lab=v}
C {devices/lab_pin.sym} 1110 318 0 1 {name=net17 lab=v}
C {sky130_fd_pr/nfet_01v8.sym} 1020 465 0 0 {name=Mi4n W=.42 L=.15}
N 1040 495 1040 530 {lab=g}
N 1015 530 1040 530 {lab=g}
C {devices/lab_pin.sym} 1015 530 0 0 {name=net18 lab=g}
N 1040 465 1050 465 {lab=g}
N 1050 465 1050 508 {lab=g}
N 1050 508 1110 508 {lab=g}
C {devices/lab_pin.sym} 1110 508 0 1 {name=net19 lab=g}
C {nor2.sym} 1020 1235 0 0 {name=Xboth}
N 865 1235 900 1235 {lab=nb0}
C {devices/lab_pin.sym} 865 1235 0 0 {name=net20 lab=nb0}
N 865 1265 900 1265 {lab=nb1}
C {devices/lab_pin.sym} 865 1265 0 0 {name=net21 lab=nb1}
N 865 1295 900 1295 {lab=en20}
C {devices/lab_pin.sym} 865 1295 0 0 {name=net22 lab=en20}
N 1140 1235 1175 1235 {lab=v}
C {devices/lab_pin.sym} 1175 1235 0 1 {name=net23 lab=v}
N 1140 1265 1175 1265 {lab=g}
C {devices/lab_pin.sym} 1175 1265 0 1 {name=net24 lab=g}
C {nor2.sym} 1440 1235 0 0 {name=Xzero}
N 1285 1235 1320 1235 {lab=b0}
C {devices/lab_pin.sym} 1285 1235 0 0 {name=net25 lab=b0}
N 1285 1265 1320 1265 {lab=b1}
C {devices/lab_pin.sym} 1285 1265 0 0 {name=net26 lab=b1}
N 1285 1295 1320 1295 {lab=zero}
C {devices/lab_pin.sym} 1285 1295 0 0 {name=net27 lab=zero}
N 1560 1235 1595 1235 {lab=v}
C {devices/lab_pin.sym} 1595 1235 0 1 {name=net28 lab=v}
N 1560 1265 1595 1265 {lab=g}
C {devices/lab_pin.sym} 1595 1265 0 1 {name=net29 lab=g}
C {nor2.sym} 180 1515 0 0 {name=Xdiff}
N 25 1515 60 1515 {lab=zero}
C {devices/lab_pin.sym} 25 1515 0 0 {name=net30 lab=zero}
N 25 1545 60 1545 {lab=en20}
C {devices/lab_pin.sym} 25 1545 0 0 {name=net31 lab=en20}
N 25 1575 60 1575 {lab=off15}
C {devices/lab_pin.sym} 25 1575 0 0 {name=net32 lab=off15}
N 300 1515 335 1515 {lab=v}
C {devices/lab_pin.sym} 335 1515 0 1 {name=net33 lab=v}
N 300 1545 335 1545 {lab=g}
C {devices/lab_pin.sym} 335 1545 0 1 {name=net34 lab=g}
C {sky130_fd_pr/pfet_01v8.sym} 1440 275 0 0 {name=Mi15p W=.84 L=.15}
N 1460 210 1460 245 {lab=v}
N 1435 210 1460 210 {lab=v}
C {devices/lab_pin.sym} 1435 210 0 0 {name=net35 lab=v}
N 1460 275 1470 275 {lab=v}
N 1470 275 1470 318 {lab=v}
N 1470 318 1530 318 {lab=v}
C {devices/lab_pin.sym} 1530 318 0 1 {name=net36 lab=v}
C {sky130_fd_pr/nfet_01v8.sym} 1440 465 0 0 {name=Mi15n W=.42 L=.15}
N 1460 495 1460 530 {lab=g}
N 1435 530 1460 530 {lab=g}
C {devices/lab_pin.sym} 1435 530 0 0 {name=net37 lab=g}
N 1460 465 1470 465 {lab=g}
N 1470 465 1470 508 {lab=g}
N 1470 508 1530 508 {lab=g}
C {devices/lab_pin.sym} 1530 508 0 1 {name=net38 lab=g}
C {sky130_fd_pr/pfet_01v8.sym} 180 755 0 0 {name=Mi20p W=.84 L=.15}
N 200 690 200 725 {lab=v}
N 175 690 200 690 {lab=v}
C {devices/lab_pin.sym} 175 690 0 0 {name=net39 lab=v}
N 200 755 210 755 {lab=v}
N 210 755 210 798 {lab=v}
N 210 798 270 798 {lab=v}
C {devices/lab_pin.sym} 270 798 0 1 {name=net40 lab=v}
C {sky130_fd_pr/nfet_01v8.sym} 180 945 0 0 {name=Mi20n W=.42 L=.15}
N 200 975 200 1010 {lab=g}
N 175 1010 200 1010 {lab=g}
C {devices/lab_pin.sym} 175 1010 0 0 {name=net41 lab=g}
N 200 945 210 945 {lab=g}
N 210 945 210 988 {lab=g}
N 210 988 270 988 {lab=g}
C {devices/lab_pin.sym} 270 988 0 1 {name=net42 lab=g}
C {tailgate.sym} 600 1515 0 0 {name=Xsw4}
N 445 1515 480 1515 {lab=en4}
C {devices/lab_pin.sym} 445 1515 0 0 {name=net43 lab=en4}
N 445 1545 480 1545 {lab=off4}
C {devices/lab_pin.sym} 445 1545 0 0 {name=net44 lab=off4}
N 445 1575 480 1575 {lab=vb}
C {devices/lab_pin.sym} 445 1575 0 0 {name=net45 lab=vb}
N 720 1515 755 1515 {lab=g4}
C {devices/lab_pin.sym} 755 1515 0 1 {name=net46 lab=g4}
N 720 1545 755 1545 {lab=v}
C {devices/lab_pin.sym} 755 1545 0 1 {name=net47 lab=v}
N 720 1575 755 1575 {lab=g}
C {devices/lab_pin.sym} 755 1575 0 1 {name=net48 lab=g}
C {tailgate.sym} 1020 1515 0 0 {name=Xsw15}
N 865 1515 900 1515 {lab=en15}
C {devices/lab_pin.sym} 865 1515 0 0 {name=net49 lab=en15}
N 865 1545 900 1545 {lab=off15}
C {devices/lab_pin.sym} 865 1545 0 0 {name=net50 lab=off15}
N 865 1575 900 1575 {lab=vb}
C {devices/lab_pin.sym} 865 1575 0 0 {name=net51 lab=vb}
N 1140 1515 1175 1515 {lab=g15}
C {devices/lab_pin.sym} 1175 1515 0 1 {name=net52 lab=g15}
N 1140 1545 1175 1545 {lab=v}
C {devices/lab_pin.sym} 1175 1545 0 1 {name=net53 lab=v}
N 1140 1575 1175 1575 {lab=g}
C {devices/lab_pin.sym} 1175 1575 0 1 {name=net54 lab=g}
C {tailgate.sym} 1440 1515 0 0 {name=Xsw20}
N 1285 1515 1320 1515 {lab=en20}
C {devices/lab_pin.sym} 1285 1515 0 0 {name=net55 lab=en20}
N 1285 1545 1320 1545 {lab=off20}
C {devices/lab_pin.sym} 1285 1545 0 0 {name=net56 lab=off20}
N 1285 1575 1320 1575 {lab=vb}
C {devices/lab_pin.sym} 1285 1575 0 0 {name=net57 lab=vb}
N 1560 1515 1595 1515 {lab=g20}
C {devices/lab_pin.sym} 1595 1515 0 1 {name=net58 lab=g20}
N 1560 1545 1595 1545 {lab=v}
C {devices/lab_pin.sym} 1595 1545 0 1 {name=net59 lab=v}
N 1560 1575 1595 1575 {lab=g}
C {devices/lab_pin.sym} 1595 1575 0 1 {name=net60 lab=g}
