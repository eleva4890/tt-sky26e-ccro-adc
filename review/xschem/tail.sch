v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Selectable current-source banks} 0 0 0 0 0.62 0.62 {}
T {Sheet terminals} 0 60 0 0 0.32 0.32 {layer=13}
C {devices/iopin.sym} 0 110 0 0 {name=io0 lab=s sim_pinnumber=1}
C {devices/iopin.sym} 150 110 0 0 {name=io1 lab=vb sim_pinnumber=2}
C {devices/iopin.sym} 300 110 0 0 {name=io2 lab=g4 sim_pinnumber=3}
C {devices/iopin.sym} 450 110 0 0 {name=io3 lab=g15 sim_pinnumber=4}
C {devices/iopin.sym} 600 110 0 0 {name=io4 lab=g20 sim_pinnumber=5}
C {devices/iopin.sym} 750 110 0 0 {name=io5 lab=v sim_pinnumber=6}
C {sky130_fd_pr/pfet_01v8.sym} 180 275 0 0 {name=Mone W=1 L=2}
N 200 305 200 340 {lab=s}
N 175 340 200 340 {lab=s}
C {devices/lab_pin.sym} 175 340 0 0 {name=net0 lab=s}
N 125 275 160 275 {lab=vb}
C {devices/lab_pin.sym} 125 275 0 0 {name=net1 lab=vb}
N 200 210 200 245 {lab=v}
N 175 210 200 210 {lab=v}
C {devices/lab_pin.sym} 175 210 0 0 {name=net2 lab=v}
N 200 275 210 275 {lab=v}
N 210 275 210 318 {lab=v}
N 210 318 270 318 {lab=v}
C {devices/lab_pin.sym} 270 318 0 1 {name=net3 lab=v}
C {units4.sym} 675 275 0 0 {name=Xunits4}
N 520 275 555 275 {lab=s}
C {devices/lab_pin.sym} 520 275 0 0 {name=net4 lab=s}
N 520 305 555 305 {lab=g4}
C {devices/lab_pin.sym} 520 305 0 0 {name=net5 lab=g4}
N 795 275 830 275 {lab=v}
C {devices/lab_pin.sym} 830 275 0 1 {name=net6 lab=v}
C {units15.sym} 1170 275 0 0 {name=Xunits15}
N 1015 275 1050 275 {lab=s}
C {devices/lab_pin.sym} 1015 275 0 0 {name=net7 lab=s}
N 1015 305 1050 305 {lab=g15}
C {devices/lab_pin.sym} 1015 305 0 0 {name=net8 lab=g15}
N 1290 275 1325 275 {lab=v}
C {devices/lab_pin.sym} 1325 275 0 1 {name=net9 lab=v}
C {units20.sym} 180 515 0 0 {name=Xunits20}
N 25 515 60 515 {lab=s}
C {devices/lab_pin.sym} 25 515 0 0 {name=net10 lab=s}
N 25 545 60 545 {lab=g20}
C {devices/lab_pin.sym} 25 545 0 0 {name=net11 lab=g20}
N 300 515 335 515 {lab=v}
C {devices/lab_pin.sym} 335 515 0 1 {name=net12 lab=v}
