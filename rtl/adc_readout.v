// Fifteen phases per polarity, continuous-time VCO ADC back end.
`default_nettype none
module adc_fa(input wire a,b,ci, output wire sum,co);
`ifdef SKY130_GATES
    sky130_fd_sc_hd__fa_1 fa(.A(a),.B(b),.CIN(ci),.SUM(sum),.COUT(co));
`else
    assign {co,sum}={1'b0,a}+b+ci;
`endif
endmodule

module pop15(input wire [14:0] x, output wire [3:0] count);
    wire [4:0] ones;
    wire [6:0] twos;
    wire [2:0] fours;
    genvar j;
    generate for (j=0; j<5; j=j+1) begin: column
        adc_fa fa(x[3*j],x[3*j+1],x[3*j+2],ones[j],twos[j]);
    end endgenerate
    wire o, t0, t1;
    adc_fa f0(ones[0],ones[1],ones[2],o,twos[5]);
    adc_fa f1(ones[3],ones[4],o,count[0],twos[6]);
    adc_fa f2(twos[0],twos[1],twos[2],t0,fours[0]);
    adc_fa f3(twos[3],twos[4],twos[5],t1,fours[1]);
    adc_fa f4(t0,t1,twos[6],count[1],fours[2]);
    adc_fa f5(fours[0],fours[1],fours[2],count[2],count[3]);
endmodule

module adc_add21(input wire [20:0] a,b, output wire [20:0] sum);
    wire [21:0] carry;
    assign carry[0]=0;
    genvar j;
    generate for (j=0; j<21; j=j+1) begin: bit_add
        adc_fa fa(a[j],b[j],carry[j],sum[j],carry[j+1]);
    end endgenerate
endmodule

// Low-phase latch followed by AND, mapped to an integrated clock gate in synthesis.
module adc_gate(input wire clk, en, output wire gclk);
`ifdef SKY130_GATES
    sky130_fd_sc_hd__dlclkp_1 cg (.CLK(clk), .GATE(en), .GCLK(gclk));
`else
    reg latched;
    always @* if (!clk) latched = en;
    assign gclk=clk & latched;
`endif
endmodule

module adc_div64(input wire tap, enable, rst_n, output wire divided);
    wire gated;
    adc_gate cg(tap,enable,gated);
    reg [5:0] count;
    always @(posedge gated or negedge rst_n)
        if (!rst_n) count<=0;
        else count<=count+1'b1;
    assign divided=count[5];
endmodule

module adc_readout(
    input wire clk, rst_n, input wire [14:0] tap_p, tap_n,
    input wire osr_sel, err_clr, input wire [1:0] dbg_mode,
    output wire [7:0] debug, output reg wrap_err, sdo, cs_n, sclk
);
    (* async_reg="true" *) reg [1:0] reset_sync, clear_sync, rate_sync;
    always @(posedge clk or negedge rst_n)
        if (!rst_n) reset_sync<=0;
        else reset_sync<={reset_sync[0],1'b1};
    wire run_n=reset_sync[1];
    always @(posedge clk or negedge run_n)
        if (!run_n) begin clear_sync<=0; rate_sync<=0; end
        else begin clear_sync<={clear_sync[0],err_clr}; rate_sync<={rate_sync[0],osr_sel}; end

    (* async_reg="true" *) reg [29:0] meta, sync;
    reg [29:0] prev;
    always @(posedge clk) begin
        meta<={tap_p,tap_n};
        sync<=meta;
        prev<=sync;
    end
    wire [29:0] toggled=sync^prev;
    wire [3:0] dp,dn;
    pop15 pp(toggled[29:15],dp);
    pop15 pn(toggled[14:0],dn);
    reg [3:0] valid;
    always @(posedge clk or negedge run_n)
        if (!run_n) valid<=0;
        else valid<={valid[2:0],1'b1};
    wire signed [4:0] delta=valid[3] ? $signed({1'b0,dp})-$signed({1'b0,dn}) : 5'sd0;
    always @(posedge clk or negedge run_n)
        if (!run_n) wrap_err<=0;
        else if (clear_sync[1]) wrap_err<=0;
        else if (valid[3] && ((&dp[3:1]) || (&dn[3:1]))) wrap_err<=1;

    wire divp,divn;
    adc_div64 vp(tap_p[0],dbg_mode==2,rst_n,divp);
    adc_div64 vn(tap_n[0],dbg_mode==2,rst_n,divn);
    assign debug=dbg_mode==1 && valid[3] ? {dp,dn} :
                 dbg_mode==2 ? {6'b0,divn,divp} : 0;

    reg rate, sampled;
    reg [7:0] phase;
    // Adopt a new OSR between complete frames and restart the two CIC histories.
    wire frame_slot=(phase[7:5]==1 || phase[7:5]==2);
    wire restart=(rate!=rate_sync[1]) && (!sampled || phase==97);
    wire terminal=(&phase[6:0]) && (!rate || phase[7]);
    reg signed [20:0] acc1,acc2;
    // The negative edge gives half a sample period for reset release.
    reg cic_n;
    always @(negedge clk or negedge run_n)
        if (!run_n) cic_n<=0;
        else cic_n<=!restart;
    wire [20:0] sum1,sum2;
    adc_add21 add1(acc1,{{16{delta[4]}},delta},sum1);
    adc_add21 add2(acc2,acc1,sum2);
    always @(posedge clk or negedge cic_n)
        if (!cic_n) begin acc1<=0; acc2<=0; end
        else begin acc1<=sum1; acc2<=sum2; end
    always @(posedge clk or negedge run_n)
        if (!run_n) begin
            phase<=0; rate<=0; sampled<=0;
        end else if (restart) begin
            phase<=0; rate<=rate_sync[1]; sampled<=0;
        end else begin
            phase<=terminal ? 0 : phase+1'b1;
            if (terminal) sampled<=1;
        end

    // At phase 1, acc2 includes acc1 for the last sample of the previous block.
    wire capture=sampled && phase==1;
    wire serial=sampled && phase>=2 && phase<=22;
    wire shift_clk, work_clk;
    adc_gate g_delay(clk,serial,shift_clk);
    adc_gate g_work(clk,serial || capture,work_clk);
    wire [20:0] work;
    reg [20:0] delay1, delay2;
    reg borrow1, borrow2;
    reg history_valid;
    always @(posedge clk or negedge run_n)
        if (!run_n) history_valid<=0;
        else if (restart) history_valid<=0;
        else if (sampled && phase==22) history_valid<=1;
    wire a=work[0], b=delay1[0] & history_valid, z=delay2[0] & history_valid;
    wire first=a^b^borrow1;
    wire second=first^z^borrow2;
    wire [20:0] shift_word={second,work[20:1]};
`ifdef SKY130_GATES
    // The scan mux doubles as the parallel-load selector of the serial comb.
    genvar k;
    generate for (k=0; k<21; k=k+1) begin: bit_store
        sky130_fd_sc_hd__sdfxtp_1 ff(.CLK(work_clk),.D(shift_word[k]),
                                      .SCD(acc2[k]),.SCE(capture),.Q(work[k]));
    end endgenerate
`else
    reg [20:0] storage;
    always @(posedge work_clk) storage<=capture ? acc2 : shift_word;
    assign work=storage;
`endif
    // history_valid masks the old delay bits for one full 21-bit pass.
    always @(posedge shift_clk) begin
        delay1<={a,delay1[20:1]};
        delay2<={first,delay2[20:1]};
    end
    always @(posedge clk or negedge run_n)
        if (!run_n) begin borrow1<=0; borrow2<=0; end
        else if (capture) begin borrow1<=0; borrow2<=0; end
        else if (serial) begin
            borrow1<=(~a & b) | (~(a^b) & borrow1);
            borrow2<=(~first & z) | (~(first^z) & borrow2);
        end

    wire [15:0] code=rate ? work[20:5] : work[18:3];
    wire [3:0] bit_index={phase[5],~phase[4:2]};
    always @(posedge clk or negedge run_n)
        if (!run_n) begin sdo<=0; cs_n<=1; sclk<=0; end
        else if (sampled && frame_slot) begin
            cs_n<=0; sclk<=phase[1];
            if (phase[1:0]==0) sdo<=code[bit_index];
        end else begin sdo<=0; cs_n<=1; sclk<=0; end
endmodule
`default_nettype wire
