gds readonly false
gds rescale false
gds read $::env(ASSEMBLY_GDS)
load tt_um_eleva_ccro_adc
select top cell
expand
flatten tile_mask
load tile_mask
select top cell
box values 0 0 161um 225.76um
erase labels
source $::env(TILE_PORTS)
extract all
ext2spice lvs
ext2spice merge none
ext2spice subcircuit top on
ext2spice -o tile_mask.spice
feedback clear
antennacheck
feedback save antenna_feedback.txt
puts "ANTENNA_FEEDBACK [feedback count]"
quit -noprompt
