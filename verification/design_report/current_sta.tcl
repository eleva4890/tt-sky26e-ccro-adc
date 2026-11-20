set corner $::env(PWR_CORNER)
set rc $::env(PWR_RC)
read_liberty /pdk/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__${corner}.lib
read_verilog /design/layout/readout/adc_readout.nl.v
link_design adc_readout
read_spef /design/layout/readout/spef/adc_readout.$rc.spef
if {$::env(PWR_MODE)==0} {
    create_clock -name sample -period 50
} else {
    create_clock -name sample -period 50 [get_ports clk]
}
set_input_transition 0.3 [all_inputs]
source /design/results/tile_loads.tcl
set_propagated_clock [all_clocks]
read_power_activities -scope current_tb/dut -vcd /work/activity.vcd
report_power -digits 6
exit
