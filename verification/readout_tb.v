`timescale 1ns/1ps
module readout_tb;
    reg clk=0,rst_n,osr_sel,err_clr;
    reg [1:0] dbg_mode;
    reg [14:0] tap_p,tap_n;
    wire [7:0] debug;
    wire wrap_err,sdo,cs_n,sclk;
    adc_readout dut(.*);
    reg [3:0] pins;
    reg [7:0] raw;
    integer file,scan,tick=0,edges=0,plus_fs=0,minus_fs=0,frames=0;
    reg last_sclk=0,last_cs=1;
    reg [15:0] recv;
    reg [1023:0] path;
    initial begin
        if (!$value$plusargs("DATA=%s",path)) $fatal;
        file=$fopen(path,"r");
        while (!$feof(file)) begin
            scan=$fscanf(file,"%h %h %h %h %h %h %h %h\n",rst_n,osr_sel,err_clr,dbg_mode,tap_p,tap_n,pins,raw);
            if (scan!=8) $fatal;
            #8 clk=1; #5;
            if ({wrap_err,sclk,cs_n,sdo}!==pins || debug!==raw)
                $fatal(1,"tick=%d spi=%h expected=%h debug=%h expected=%h",tick,{wrap_err,sclk,cs_n,sdo},pins,debug,raw);
            if (last_cs && !cs_n) edges=0;
            if (!cs_n && !last_sclk && sclk) begin recv={recv[14:0],sdo}; edges=edges+1; end
            if (cs_n && !last_cs && rst_n) begin
                if (edges!=16) $fatal;
                frames=frames+1;
                if (recv==16'h7800) plus_fs=plus_fs+1;
                if (recv==16'h8800) minus_fs=minus_fs+1;
            end
            last_cs=cs_n; last_sclk=sclk;
            #3 clk=0; #4; tick=tick+1;
        end
        if (plus_fs<5 || minus_fs<5) $fatal;
        $display("PASS: %0d checked clocks, %0d complete frames, +30720 x%0d, -30720 x%0d",tick,frames,plus_fs,minus_fs);
        $finish;
    end
endmodule
