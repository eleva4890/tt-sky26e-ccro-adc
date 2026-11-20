set libdir /pdk/libs.ref/sky130_fd_sc_hd/lib
foreach {rc pvt} {min ff_n40C_1v95 nom tt_025C_1v80 max ss_100C_1v60} {
    if {$rc ne $::env(ADC_STA_RC)} {continue}
    define_corners $rc
    read_liberty -corner $rc $libdir/sky130_fd_sc_hd__${pvt}.lib
    read_verilog /design/layout/readout/adc_readout.nl.v
    link_design adc_readout
    read_spef -corner $rc /spef/adc_readout.$rc.spef
    read_sdc /design/layout/timing.sdc
    source /design/results/tile_loads.tcl
    set_propagated_clock [all_clocks]
    puts "CORNER $rc $pvt"
    report_checks -path_delay min_max -group_count 1 -fields {cap slew}
    puts "SETUP $rc"
    report_worst_slack -max
    puts "HOLD $rc"
    report_worst_slack -min
    # Each corner runs in a fresh OpenSTA process.
    exit
}
