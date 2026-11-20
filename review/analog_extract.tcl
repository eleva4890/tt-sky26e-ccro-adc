gds rescale false
gds read $::env(ASSEMBLY_GDS)
load eleva_adc_analog
select top cell
expand
set idx 0
set pins {vinp vinn b0 b1 v g}
foreach side {p n} {for {set i 0} {$i < 15} {incr i} {lappend pins ${side}$i}}
foreach p $pins {incr idx; findlabel $p; port $p make $idx}
extract all
ext2spice lvs
ext2spice subcircuit top on
ext2spice -o analog_mask.spice
quit -noprompt

