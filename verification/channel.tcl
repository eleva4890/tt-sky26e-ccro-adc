drc style drc(full)
gds maskhints yes
gds read $::env(CHANNEL_GDS)
if {[info exists ::env(ASSEMBLY_CELL)]} {load $::env(ASSEMBLY_CELL)} else {load eleva_ccro_tap_assembly}
select top cell
expand
drc check
drc catchup
set bad [drc listall why]
puts "FULL_DRC_TYPES [expr {[llength $bad]/2}]"
foreach {why boxes} $bad {puts "VIOLATION $why [llength $boxes] [lindex $boxes 0]"}
quit -noprompt
