`timescale 1ns/1ps
module ideal_latency_tb;
    reg clk=0, rst_n=1, osr_sel, err_clr=0;
    reg [1:0] dbg_mode=0;
    reg [14:0] tap_p=0,tap_n=0;
    wire [7:0] debug;
    wire wrap_err,sdo,cs_n,sclk;
    adc_readout dut(.*);
    integer r,tick=0,phase,first_tick,settled,minimum=99999,maximum=0;
    reg prev_cs=1,prev_clk=0;
    reg signed [15:0] frame;
    integer bits;
    task advance;
        begin
            #24 clk=1; #5;
            if (prev_cs && !cs_n) begin frame=0; bits=0; end
            if (!cs_n && sclk && !prev_clk) begin frame={frame[14:0],sdo}; bits=bits+1; end
            if (!prev_cs && cs_n) begin
                if (bits!=16) $fatal;
                if (first_tick>=0 && frame==16384 && settled<0) settled=tick-first_tick;
            end
            prev_cs=cs_n; prev_clk=sclk;
            #20 clk=0; #1; tick=tick+1;
        end
    endtask
    initial begin
        if (!$value$plusargs("RATE=%d",r)) $fatal;
        osr_sel=(r==256);
        first_tick=-1;
        #1 rst_n=0;
        repeat (5) advance;
        rst_n=1;
        repeat (4*r) advance;
        for (phase=0;phase<r;phase=phase+1) begin
            first_tick=tick; settled=-1;
            repeat (4*r) begin tap_p=tap_p^15'hff; advance; end
            if (settled<0 || wrap_err!==1'b0) $fatal;
            if (settled<minimum) minimum=settled;
            if (settled>maximum) maximum=settled;
            $display("PHASE %0d %0d %0d",r,phase,settled);
            first_tick=-1;
            repeat (4*r+1) advance;
        end
        $display("RANGE %0d %0d %0d",r,minimum,maximum);
        $finish;
    end
endmodule
