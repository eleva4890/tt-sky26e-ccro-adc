`timescale 1ns/1ps
module t6_tb;
    reg clk=0, rst_n=1, osr_sel=0, err_clr=0;
    reg [1:0] dbg_mode=0;
    reg [14:0] tap_p=0,tap_n=0, noisy_p=0,noisy_n=0;
    wire [7:0] debug_a,debug_b;
    wire [3:0] a,b;
    adc_readout ca (.clk(clk),.rst_n(rst_n),.osr_sel(osr_sel),.err_clr(err_clr),.dbg_mode(dbg_mode),
      .tap_p(tap_p),.tap_n(tap_n),.wrap_err(a[3]),.sclk(a[2]),.cs_n(a[1]),.sdo(a[0]),.debug(debug_a));
    adc_readout cb (.clk(clk),.rst_n(rst_n),.osr_sel(osr_sel),.err_clr(err_clr),.dbg_mode(dbg_mode),
      .tap_p(noisy_p),.tap_n(noisy_n),.wrap_err(b[3]),.sclk(b[2]),.cs_n(b[1]),.sdo(b[0]),.debug(debug_b));
    integer source,observation,tick=0,n,next_reset;
    reg [1023:0] src_path,out_path;
    initial begin
        if (!$value$plusargs("SRC=%s",src_path) || !$value$plusargs("OUT=%s",out_path)) $fatal;
        source=$fopen(src_path,"r");
        observation=$fopen(out_path,"w");
        while (!$feof(source)) begin
            n=$fscanf(source,"%h %h %h %h %h %h %h\n",next_reset,osr_sel,dbg_mode,tap_p,tap_n,noisy_p,noisy_n);
            if (n!=7) $fatal;
            if (!next_reset) rst_n=0;
            #24.999;
            if (next_reset) rst_n=1;
            #0.001 clk=1;
            #5;
`ifndef NETLIST
            $fdisplay(observation,"%d %h %h %h %h %h %h",tick,a,b,ca.acc1,cb.acc1,ca.acc2,cb.acc2);
`else
            $fdisplay(observation,"%d %h %h",tick,a,b);
`endif
            #20 clk=0;
            tick=tick+1;
        end
        $fclose(observation);
        $finish;
    end
endmodule
