v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Differential VCO ADC} 0 0 0 0 0.62 0.62 {}
T {Sheet terminals} 0 60 0 0 0.32 0.32 {layer=13}
C {devices/iopin.sym} 0 110 0 0 {name=io0 lab=vinp sim_pinnumber=1}
C {devices/iopin.sym} 150 110 0 0 {name=io1 lab=vinn sim_pinnumber=2}
C {devices/iopin.sym} 300 110 0 0 {name=io2 lab=b0 sim_pinnumber=3}
C {devices/iopin.sym} 450 110 0 0 {name=io3 lab=b1 sim_pinnumber=4}
C {devices/iopin.sym} 600 110 0 0 {name=io4 lab=v sim_pinnumber=5}
C {devices/iopin.sym} 750 110 0 0 {name=io5 lab=g sim_pinnumber=6}
C {devices/iopin.sym} 900 110 0 0 {name=io6 lab=p0 sim_pinnumber=7}
C {devices/iopin.sym} 1050 110 0 0 {name=io7 lab=p1 sim_pinnumber=8}
C {devices/iopin.sym} 0 145 0 0 {name=io8 lab=p2 sim_pinnumber=9}
C {devices/iopin.sym} 150 145 0 0 {name=io9 lab=p3 sim_pinnumber=10}
C {devices/iopin.sym} 300 145 0 0 {name=io10 lab=p4 sim_pinnumber=11}
C {devices/iopin.sym} 450 145 0 0 {name=io11 lab=p5 sim_pinnumber=12}
C {devices/iopin.sym} 600 145 0 0 {name=io12 lab=p6 sim_pinnumber=13}
C {devices/iopin.sym} 750 145 0 0 {name=io13 lab=p7 sim_pinnumber=14}
C {devices/iopin.sym} 900 145 0 0 {name=io14 lab=p8 sim_pinnumber=15}
C {devices/iopin.sym} 1050 145 0 0 {name=io15 lab=p9 sim_pinnumber=16}
C {devices/iopin.sym} 0 180 0 0 {name=io16 lab=p10 sim_pinnumber=17}
C {devices/iopin.sym} 150 180 0 0 {name=io17 lab=p11 sim_pinnumber=18}
C {devices/iopin.sym} 300 180 0 0 {name=io18 lab=p12 sim_pinnumber=19}
C {devices/iopin.sym} 450 180 0 0 {name=io19 lab=p13 sim_pinnumber=20}
C {devices/iopin.sym} 600 180 0 0 {name=io20 lab=p14 sim_pinnumber=21}
C {devices/iopin.sym} 750 180 0 0 {name=io21 lab=n0 sim_pinnumber=22}
C {devices/iopin.sym} 900 180 0 0 {name=io22 lab=n1 sim_pinnumber=23}
C {devices/iopin.sym} 1050 180 0 0 {name=io23 lab=n2 sim_pinnumber=24}
C {devices/iopin.sym} 0 215 0 0 {name=io24 lab=n3 sim_pinnumber=25}
C {devices/iopin.sym} 150 215 0 0 {name=io25 lab=n4 sim_pinnumber=26}
C {devices/iopin.sym} 300 215 0 0 {name=io26 lab=n5 sim_pinnumber=27}
C {devices/iopin.sym} 450 215 0 0 {name=io27 lab=n6 sim_pinnumber=28}
C {devices/iopin.sym} 600 215 0 0 {name=io28 lab=n7 sim_pinnumber=29}
C {devices/iopin.sym} 750 215 0 0 {name=io29 lab=n8 sim_pinnumber=30}
C {devices/iopin.sym} 900 215 0 0 {name=io30 lab=n9 sim_pinnumber=31}
C {devices/iopin.sym} 1050 215 0 0 {name=io31 lab=n10 sim_pinnumber=32}
C {devices/iopin.sym} 0 250 0 0 {name=io32 lab=n11 sim_pinnumber=33}
C {devices/iopin.sym} 150 250 0 0 {name=io33 lab=n12 sim_pinnumber=34}
C {devices/iopin.sym} 300 250 0 0 {name=io34 lab=n13 sim_pinnumber=35}
C {devices/iopin.sym} 450 250 0 0 {name=io35 lab=n14 sim_pinnumber=36}
C {front.sym} 180 415 0 0 {name=Xf}
N 25 415 60 415 {lab=vinp}
C {devices/lab_pin.sym} 25 415 0 0 {name=net0 lab=vinp}
N 25 445 60 445 {lab=vinn}
C {devices/lab_pin.sym} 25 445 0 0 {name=net1 lab=vinn}
N 25 475 60 475 {lab=b0}
C {devices/lab_pin.sym} 25 475 0 0 {name=net2 lab=b0}
N 25 505 60 505 {lab=b1}
C {devices/lab_pin.sym} 25 505 0 0 {name=net3 lab=b1}
N 300 415 335 415 {lab=rp}
C {devices/lab_pin.sym} 335 415 0 1 {name=net4 lab=rp}
N 300 445 335 445 {lab=rn}
C {devices/lab_pin.sym} 335 445 0 1 {name=net5 lab=rn}
N 300 475 335 475 {lab=v}
C {devices/lab_pin.sym} 335 475 0 1 {name=net6 lab=v}
N 300 505 335 505 {lab=g}
C {devices/lab_pin.sym} 335 505 0 1 {name=net7 lab=g}
C {dual.sym} 675 415 0 0 {name=Xd}
N 520 415 555 415 {lab=rp}
C {devices/lab_pin.sym} 520 415 0 0 {name=net8 lab=rp}
N 520 445 555 445 {lab=rn}
C {devices/lab_pin.sym} 520 445 0 0 {name=net9 lab=rn}
N 520 475 555 475 {lab=v}
C {devices/lab_pin.sym} 520 475 0 0 {name=net10 lab=v}
N 520 505 555 505 {lab=g}
C {devices/lab_pin.sym} 520 505 0 0 {name=net11 lab=g}
N 520 535 555 535 {lab=p0}
C {devices/lab_pin.sym} 520 535 0 0 {name=net12 lab=p0}
N 520 565 555 565 {lab=p1}
C {devices/lab_pin.sym} 520 565 0 0 {name=net13 lab=p1}
N 520 595 555 595 {lab=p2}
C {devices/lab_pin.sym} 520 595 0 0 {name=net14 lab=p2}
N 520 625 555 625 {lab=p3}
C {devices/lab_pin.sym} 520 625 0 0 {name=net15 lab=p3}
N 520 655 555 655 {lab=p4}
C {devices/lab_pin.sym} 520 655 0 0 {name=net16 lab=p4}
N 520 685 555 685 {lab=p5}
C {devices/lab_pin.sym} 520 685 0 0 {name=net17 lab=p5}
N 520 715 555 715 {lab=p6}
C {devices/lab_pin.sym} 520 715 0 0 {name=net18 lab=p6}
N 520 745 555 745 {lab=p7}
C {devices/lab_pin.sym} 520 745 0 0 {name=net19 lab=p7}
N 520 775 555 775 {lab=p8}
C {devices/lab_pin.sym} 520 775 0 0 {name=net20 lab=p8}
N 520 805 555 805 {lab=p9}
C {devices/lab_pin.sym} 520 805 0 0 {name=net21 lab=p9}
N 520 835 555 835 {lab=p10}
C {devices/lab_pin.sym} 520 835 0 0 {name=net22 lab=p10}
N 520 865 555 865 {lab=p11}
C {devices/lab_pin.sym} 520 865 0 0 {name=net23 lab=p11}
N 520 895 555 895 {lab=p12}
C {devices/lab_pin.sym} 520 895 0 0 {name=net24 lab=p12}
N 795 415 830 415 {lab=p13}
C {devices/lab_pin.sym} 830 415 0 1 {name=net25 lab=p13}
N 795 445 830 445 {lab=p14}
C {devices/lab_pin.sym} 830 445 0 1 {name=net26 lab=p14}
N 795 475 830 475 {lab=n0}
C {devices/lab_pin.sym} 830 475 0 1 {name=net27 lab=n0}
N 795 505 830 505 {lab=n1}
C {devices/lab_pin.sym} 830 505 0 1 {name=net28 lab=n1}
N 795 535 830 535 {lab=n2}
C {devices/lab_pin.sym} 830 535 0 1 {name=net29 lab=n2}
N 795 565 830 565 {lab=n3}
C {devices/lab_pin.sym} 830 565 0 1 {name=net30 lab=n3}
N 795 595 830 595 {lab=n4}
C {devices/lab_pin.sym} 830 595 0 1 {name=net31 lab=n4}
N 795 625 830 625 {lab=n5}
C {devices/lab_pin.sym} 830 625 0 1 {name=net32 lab=n5}
N 795 655 830 655 {lab=n6}
C {devices/lab_pin.sym} 830 655 0 1 {name=net33 lab=n6}
N 795 685 830 685 {lab=n7}
C {devices/lab_pin.sym} 830 685 0 1 {name=net34 lab=n7}
N 795 715 830 715 {lab=n8}
C {devices/lab_pin.sym} 830 715 0 1 {name=net35 lab=n8}
N 795 745 830 745 {lab=n9}
C {devices/lab_pin.sym} 830 745 0 1 {name=net36 lab=n9}
N 795 775 830 775 {lab=n10}
C {devices/lab_pin.sym} 830 775 0 1 {name=net37 lab=n10}
N 795 805 830 805 {lab=n11}
C {devices/lab_pin.sym} 830 805 0 1 {name=net38 lab=n11}
N 795 835 830 835 {lab=n12}
C {devices/lab_pin.sym} 830 835 0 1 {name=net39 lab=n12}
N 795 865 830 865 {lab=n13}
C {devices/lab_pin.sym} 830 865 0 1 {name=net40 lab=n13}
N 795 895 830 895 {lab=n14}
C {devices/lab_pin.sym} 830 895 0 1 {name=net41 lab=n14}
