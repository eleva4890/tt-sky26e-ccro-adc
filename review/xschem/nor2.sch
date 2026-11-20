v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Static CMOS NOR} 0 0 0 0 0.62 0.62 {}
T {Sheet terminals} 0 60 0 0 0.32 0.32 {layer=13}
C {devices/iopin.sym} 0 110 0 0 {name=io0 lab=a sim_pinnumber=1}
C {devices/iopin.sym} 150 110 0 0 {name=io1 lab=b sim_pinnumber=2}
C {devices/iopin.sym} 300 110 0 0 {name=io2 lab=y sim_pinnumber=3}
C {devices/iopin.sym} 450 110 0 0 {name=io3 lab=v sim_pinnumber=4}
C {devices/iopin.sym} 600 110 0 0 {name=io4 lab=g sim_pinnumber=5}
C {sky130_fd_pr/pfet_01v8.sym} 180 275 0 0 {name=Mp0 W=.84 L=.15}
N 200 305 200 340 {lab=mid}
N 175 340 200 340 {lab=mid}
C {devices/lab_pin.sym} 175 340 0 0 {name=net0 lab=mid}
N 125 275 160 275 {lab=a}
C {devices/lab_pin.sym} 125 275 0 0 {name=net1 lab=a}
N 200 210 200 245 {lab=v}
N 175 210 200 210 {lab=v}
C {devices/lab_pin.sym} 175 210 0 0 {name=net2 lab=v}
N 200 275 210 275 {lab=v}
N 210 275 210 318 {lab=v}
N 210 318 270 318 {lab=v}
C {devices/lab_pin.sym} 270 318 0 1 {name=net3 lab=v}
C {sky130_fd_pr/pfet_01v8.sym} 675 275 0 0 {name=Mp1 W=.84 L=.15}
N 695 305 695 340 {lab=y}
N 670 340 695 340 {lab=y}
C {devices/lab_pin.sym} 670 340 0 0 {name=net4 lab=y}
N 620 275 655 275 {lab=b}
C {devices/lab_pin.sym} 620 275 0 0 {name=net5 lab=b}
N 695 210 695 245 {lab=mid}
N 670 210 695 210 {lab=mid}
C {devices/lab_pin.sym} 670 210 0 0 {name=net6 lab=mid}
N 695 275 705 275 {lab=v}
N 705 275 705 318 {lab=v}
N 705 318 765 318 {lab=v}
C {devices/lab_pin.sym} 765 318 0 1 {name=net7 lab=v}
C {sky130_fd_pr/nfet_01v8.sym} 1170 275 0 0 {name=Mn0 W=.42 L=.15}
N 1190 210 1190 245 {lab=y}
N 1165 210 1190 210 {lab=y}
C {devices/lab_pin.sym} 1165 210 0 0 {name=net8 lab=y}
N 1115 275 1150 275 {lab=a}
C {devices/lab_pin.sym} 1115 275 0 0 {name=net9 lab=a}
N 1190 305 1190 340 {lab=g}
N 1165 340 1190 340 {lab=g}
C {devices/lab_pin.sym} 1165 340 0 0 {name=net10 lab=g}
N 1190 275 1200 275 {lab=g}
N 1200 275 1200 318 {lab=g}
N 1200 318 1260 318 {lab=g}
C {devices/lab_pin.sym} 1260 318 0 1 {name=net11 lab=g}
C {sky130_fd_pr/nfet_01v8.sym} 180 515 0 0 {name=Mn1 W=.42 L=.15}
N 200 450 200 485 {lab=y}
N 175 450 200 450 {lab=y}
C {devices/lab_pin.sym} 175 450 0 0 {name=net12 lab=y}
N 125 515 160 515 {lab=b}
C {devices/lab_pin.sym} 125 515 0 0 {name=net13 lab=b}
N 200 545 200 580 {lab=g}
N 175 580 200 580 {lab=g}
C {devices/lab_pin.sym} 175 580 0 0 {name=net14 lab=g}
N 200 515 210 515 {lab=g}
N 210 515 210 558 {lab=g}
N 210 558 270 558 {lab=g}
C {devices/lab_pin.sym} 270 558 0 1 {name=net15 lab=g}
