`timescale 1ns/1ps
module mixed_tb;
    reg clk=0,rst_n,osr_sel=0,err_clr=0;
    reg [1:0] dbg_mode=0;
    reg [14:0] tap_p,tap_n;
    wire [7:0] debug;
    wire wrap_err,sdo,cs_n,sclk;
    adc_readout dut(.*);
    integer file,fields,cycles=0,frames=0,bits=0,width=0,prev_start=-1,signcheck;
    reg [1023:0] path;
    reg last_cs=1,last_clk=0;
    reg signed [15:0] word_reg;
    initial begin
        if (!$value$plusargs("DATA=%s",path) || !$value$plusargs("SIGN=%d",signcheck)) $fatal;
        if (signcheck!==1 && signcheck!==-1) $fatal;
        file=$fopen(path,"r");
        while (!$feof(file)) begin
            fields=$fscanf(file,"%d %h %h\n",rst_n,tap_p,tap_n);
            if (fields!=3) $fatal;
            #15.625 clk=1; #8;
            if (^{sdo,cs_n,sclk,wrap_err,debug}===1'bx) $fatal(1,"X at %d",cycles);
            if (wrap_err!==0 || debug!==0) $fatal(1,"Wrap/debug at %d",cycles);
            if (cs_n && (sdo || sclk)) $fatal;
            if (last_cs && !cs_n) begin
                if (prev_start>=0 && cycles-prev_start!=128) $fatal;
                prev_start=cycles; bits=0; width=0;
            end
            if (!cs_n) width=width+1;
            if (!cs_n && !last_clk && sclk) begin
                word_reg={word_reg[14:0],sdo}; bits=bits+1;
            end
            if (cs_n && !last_cs) begin
                if (bits!=16 || width!=64) $fatal;
                frames=frames+1;
                $display("frame %0d signed code %0d",frames,$signed(word_reg));
                if ((signcheck>0 && word_reg<=0) || (signcheck<0 && word_reg>=0)) $fatal(1,"polarity error");
            end
            last_cs=cs_n; last_clk=sclk;
            #7.625 clk=0; cycles=cycles+1;
        end
        if (frames<3) $fatal(1,"insufficient frames %d",frames);
        $display("PASS: %0d sample clocks, %0d frames, sign %0d",cycles,frames,signcheck);
        $finish;
    end
endmodule
