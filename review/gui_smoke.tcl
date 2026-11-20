foreach file [lsort [glob *.sch]] {
    xschem load [file normalize $file]
    xschem zoom_full
    set base [file rootname $file]
    xschem print svg [file join $env(SHEET_PREVIEWS) $base.svg] 1500 1000
    puts "OPEN $file [xschem get instances] objects"
}
exit

