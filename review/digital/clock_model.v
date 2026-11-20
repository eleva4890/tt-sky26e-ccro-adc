module sky130_fd_sc_hd__dlclkp_1 (
    GCLK,
    GATE,
    CLK
);

    // Module ports
    output GCLK;
    input  GATE;
    input  CLK ;

    // Local signals
    reg m0  ;
    wire clkn;

    //                            Name     Output  Other arguments
    not                           not0    (clkn  , CLK            );
    always @* if (clkn) m0 = GATE;
    and                           and0    (GCLK  , m0, CLK        );

endmodule
