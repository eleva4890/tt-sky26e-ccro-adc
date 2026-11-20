drc style drc(full)
gds maskhints yes
gds read $::env(ANALOG_GDS)
load eleva_adc_analog
select top cell
expand
drc check
drc catchup
set bad [drc listall why]
puts "FULL_DRC_TYPES [expr {[llength $bad]/2}]"
foreach {why boxes} $bad {puts "VIOLATION $why [llength $boxes] [lindex $boxes 0]"}
set pins {vinp vinn b0 b1 v g}
foreach s {p n} {for {set i 0} {$i<15} {incr i} {lappend pins ${s}$i}}
set ix 0
foreach p $pins {incr ix; findlabel $p; port $p make $ix}
extract all
ext2spice lvs
ext2spice subcircuit top on
ext2spice -o analog.spice
ext2spice cthresh 0
ext2spice hierarchy off
ext2spice -o analog_c.spice
quit -noprompt
