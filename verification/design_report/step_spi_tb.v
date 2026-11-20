`timescale 1ns/1ps
module step_spi_tb;
    reg clk=0, rst_n=1, osr_sel, err_clr=0;
    reg [1:0] dbg_mode=0;
    reg [14:0] tap_p=0, tap_n=0;
    wire [7:0] debug;
    wire wrap_err, sdo, cs_n, sclk;
    adc_readout dut(.*);
    integer source, rows, tick, file_tick, bits, start_tick, delay_ticks, rate;
    reg [2047:0] header;
    reg [14:0] p,n;
    real voltage;
    reg previous_cs=1, previous_clk=0;
    reg signed [15:0] word_data;
    initial begin
        if (!$value$plusargs("RATE=%d",rate) || !$value$plusargs("DELAY=%d",delay_ticks)) $fatal;
        osr_sel=(rate==256);
        source=$fopen("results/design_report/characterization/step_taps.csv","r");
        if (!source) $fatal;
        rows=$fgets(header,source);
        #1 rst_n=0;
        for (tick=0;tick<=2200;tick=tick+1) begin
            rows=$fscanf(source,"%d,%f,%h,%h\n",file_tick,voltage,p,n);
            if (rows!=4 || file_tick!=tick) $fatal;
            tap_p=p; tap_n=n;
            // Release after the voltage ramp and startup transients.
            rst_n=(tick>=65+delay_ticks);
            #24 clk=1;
            #5;
            if (previous_cs && !cs_n) begin bits=0; word_data=0; start_tick=tick; end
            if (!cs_n && sclk && !previous_clk) begin
                bits=bits+1;
                word_data={word_data[14:0],sdo};
            end
            if (!previous_cs && cs_n) begin
                if (bits!=16 || tick-start_tick!=64) $fatal;
                $display("WORD %0d %0d %0d %0d %0d",rate,delay_ticks,start_tick,tick,word_data);
            end
            if (tick>500 && wrap_err!==1'b0) $fatal;
            previous_cs=cs_n; previous_clk=sclk;
            #20 clk=0;
            #1;
        end
        $finish;
    end
endmodule
