gds readonly false
gds rescale false
gds read $::env(EXT_TAP_GDS)
load tt_um_eleva_ccro_adc
select top cell
expand
flatten interface
load interface
select top cell
box values 0 0 161um 225.76um
erase labels
source $::env(EXT_TAP_LABELS)
extract all
quit -noprompt
