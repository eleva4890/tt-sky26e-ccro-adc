`timescale 1ns/1ps
module divider_tb;
    reg clk=0,rst_n=1,osr_sel=0,err_clr=0;
    reg [1:0] dbg_mode=0;
    reg [14:0] tap_p=0,tap_n=0;
    wire [7:0] debug;
    wire wrap_err,cs_n,sclk,sdo;
    adc_readout dut(.*);
    always #10 clk=~clk;
    integer i,p=0,n=0;
    task test_bus;
        begin
            if (debug !== (dbg_mode==2 ? {6'b0,n[5],p[5]} : 8'b0))
                $fatal(1,"Debug divider mismatch got %h p=%d n=%d",debug,p,n);
        end
    endtask
    initial begin
        #3 rst_n=0; #30 rst_n=1;
        // Idle intervals contain many full raw VCO periods. Re-enabling while
        // tap is high must wait for the next low phase before counting.
        for (i=0;i<428;i=i+1) begin
            #3 tap_p[0]=1; if (dbg_mode==2) p=p+1;
            #3;
            if (i==5 || i==109 || i==275) dbg_mode=2;
            if (i==84 || i==203 || i==390) dbg_mode=3;
            #3; test_bus;
            tap_p[0]=0; #4;
            if (i%3==0) begin
                tap_n[0]=1; if (dbg_mode==2) n=n+1;
                #4; test_bus; tap_n[0]=0;
            end
            #4; test_bus;
        end
        $display("PASS: /64 phase retention, independent P/N edges, QUIET gating, high-phase mode changes");
        $finish;
    end
endmodule
