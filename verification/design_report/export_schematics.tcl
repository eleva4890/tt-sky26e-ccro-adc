# Run from review/xschem: xvfb-run -a xschem --rcfile review.rc \
#   --script ../../verification/design_report/export_schematics.tcl front.sch
set scriptdir [file dirname [file normalize [info script]]]
if {[file isdirectory [file join $scriptdir ../figures]]} {
    set out [file normalize [file join $scriptdir ../figures]]
} else {
    set out [file normalize [file join $scriptdir ../../results/design_report/figures]]
}
file mkdir $out
# Preserve native wires, polygons and text. High-contrast colors for white paper.
set svg_colors [lrepeat $cadlayers 0x283e48]
foreach {layer rgb} {0 0xffffff 1 0x00656d 3 0x20343c 4 0x243e4b 5 0x8c4740 13 0x674725} {
    lset svg_colors $layer $rgb
}
set svg_font_name Helvetica
# Equal viewport and schematic dimensions give 1 SVG unit per schematic unit.
# All four sheets use (-100,-30) as the upper-left corner.
foreach {sheet xmax ymax} {front 1530 1370 beta_ref 1280 855 stage 1700 855 cvsl 1700 570} {
    xschem load [file normalize $sheet.sch]
    xschem print svg [file join $out xschem_$sheet.svg] \
        [expr {$xmax+100}] [expr {$ymax+30}] -100 -30 $xmax $ymax
}
exit
