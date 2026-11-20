v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Transmission gate and off clamp} 0 0 0 0 0.62 0.62 {}
T {Sheet terminals} 0 60 0 0 0.32 0.32 {layer=13}
C {devices/iopin.sym} 0 110 0 0 {name=io0 lab=en sim_pinnumber=1}
C {devices/iopin.sym} 150 110 0 0 {name=io1 lab=enb sim_pinnumber=2}
C {devices/iopin.sym} 300 110 0 0 {name=io2 lab=vb sim_pinnumber=3}
C {devices/iopin.sym} 450 110 0 0 {name=io3 lab=out sim_pinnumber=4}
C {devices/iopin.sym} 600 110 0 0 {name=io4 lab=v sim_pinnumber=5}
C {devices/iopin.sym} 750 110 0 0 {name=io5 lab=g sim_pinnumber=6}
C {sky130_fd_pr/pfet_01v8.sym} 180 275 0 0 {name=Monp W=.84 L=.15}
N 200 305 200 340 {lab=out}
N 175 340 200 340 {lab=out}
C {devices/lab_pin.sym} 175 340 0 0 {name=net0 lab=out}
N 125 275 160 275 {lab=enb}
C {devices/lab_pin.sym} 125 275 0 0 {name=net1 lab=enb}
N 200 210 200 245 {lab=vb}
N 175 210 200 210 {lab=vb}
C {devices/lab_pin.sym} 175 210 0 0 {name=net2 lab=vb}
N 200 275 210 275 {lab=v}
N 210 275 210 318 {lab=v}
N 210 318 270 318 {lab=v}
C {devices/lab_pin.sym} 270 318 0 1 {name=net3 lab=v}
C {sky130_fd_pr/nfet_01v8.sym} 675 275 0 0 {name=Monn W=.42 L=.15}
N 695 210 695 245 {lab=out}
N 670 210 695 210 {lab=out}
C {devices/lab_pin.sym} 670 210 0 0 {name=net4 lab=out}
N 620 275 655 275 {lab=en}
C {devices/lab_pin.sym} 620 275 0 0 {name=net5 lab=en}
N 695 305 695 340 {lab=vb}
N 670 340 695 340 {lab=vb}
C {devices/lab_pin.sym} 670 340 0 0 {name=net6 lab=vb}
N 695 275 705 275 {lab=g}
N 705 275 705 318 {lab=g}
N 705 318 765 318 {lab=g}
C {devices/lab_pin.sym} 765 318 0 1 {name=net7 lab=g}
C {sky130_fd_pr/pfet_01v8.sym} 1170 275 0 0 {name=Moff W=.84 L=.15}
N 1190 305 1190 340 {lab=out}
N 1165 340 1190 340 {lab=out}
C {devices/lab_pin.sym} 1165 340 0 0 {name=net8 lab=out}
N 1115 275 1150 275 {lab=en}
C {devices/lab_pin.sym} 1115 275 0 0 {name=net9 lab=en}
N 1190 210 1190 245 {lab=v}
N 1165 210 1190 210 {lab=v}
C {devices/lab_pin.sym} 1165 210 0 0 {name=net10 lab=v}
N 1190 275 1200 275 {lab=v}
N 1200 275 1200 318 {lab=v}
N 1200 318 1260 318 {lab=v}
C {devices/lab_pin.sym} 1260 318 0 1 {name=net11 lab=v}
