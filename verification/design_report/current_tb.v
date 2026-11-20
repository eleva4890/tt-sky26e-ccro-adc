`timescale 1ns/1ps
module current_tb;
    reg clk=0, rst_n=1;
    reg [14:0] tap_p=0, tap_n=0;
    wire [7:0] debug;
    wire sdo, cs_n, sclk, wrap_err;
    adc_readout dut(.clk(clk), .rst_n(rst_n), .tap_p(tap_p), .tap_n(tap_n),
                    .osr_sel(1'b0), .err_clr(1'b0), .dbg_mode(2'b00), .debug(debug),
                    .sdo(sdo), .cs_n(cs_n), .sclk(sclk), .wrap_err(wrap_err));
    integer mode, ip=0, ineg=0;
    real pstep, nstep;
    initial begin
        if (!$value$plusargs("MODE=%d",mode)) $finish;
        // TT frequencies in MHz at zero and +0.20 V. Each bank has 30 edges/cycle.
        pstep=1000.0/(30*(mode==2 ? 4.4468 : 3.7691));
        nstep=1000.0/(30*(mode==2 ? 3.0679 : 3.7687));
        fork
            forever begin #(pstep); tap_p[ip]=~tap_p[ip]; ip=(ip+1)%15; end
            forever begin #(nstep); tap_n[ineg]=~tap_n[ineg]; ineg=(ineg+1)%15; end
        join
    end
    initial begin
        #1 rst_n=0;
        repeat(8) begin #25 clk=1; #25 clk=0; end
        if (mode!=0) begin rst_n=1; forever #25 clk=~clk; end
    end
    initial begin
        #30000;
        $dumpfile("activity.vcd");
        $dumpvars(2,dut);
        #128000 $finish;
    end
endmodule
