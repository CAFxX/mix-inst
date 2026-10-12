// fz14_tchi3a: gen_fused14.py
module fz14_tchi3a(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] out
);
    function [63:0] rotl;
        input [63:0] x;
        input integer r;
        begin
            r = r % 64;
            rotl = r ? ((x << r) | (x >> (64 - r))) : x;
        end
    endfunction
    wire [63:0] x0 = v ^ k;
    wire [63:0] r0_1 = rotl(x0, 1);
    wire [63:0] r0_5 = rotl(x0, 5);
    wire [63:0] r0_7 = rotl(x0, 7);
    wire [63:0] r0_13 = rotl(x0, 13);
    wire [63:0] r0_19 = rotl(x0, 19);
    wire [63:0] r0_29 = rotl(x0, 29);
    wire [63:0] r0_37 = rotl(x0, 37);
    wire [63:0] x1 = (x0 ^ (r0_1 & r0_7) ^ (r0_13 & r0_19) ^ (r0_29 & r0_37) ^ r0_5);
    wire [63:0] r1_7 = rotl(x1, 7);
    wire [63:0] r1_13 = rotl(x1, 13);
    wire [63:0] r1_15 = rotl(x1, 15);
    wire [63:0] r1_25 = rotl(x1, 25);
    wire [63:0] r1_35 = rotl(x1, 35);
    wire [63:0] r1_45 = rotl(x1, 45);
    wire [63:0] r1_55 = rotl(x1, 55);
    wire [63:0] x2 = (x1 ^ (r1_7 & r1_15) ^ (r1_25 & r1_35) ^ (r1_45 & r1_55) ^ r1_13);
    wire [63:0] r2_13 = rotl(x2, 13);
    wire [63:0] r2_21 = rotl(x2, 21);
    wire [63:0] r2_23 = rotl(x2, 23);
    wire [63:0] r2_33 = rotl(x2, 33);
    wire [63:0] r2_43 = rotl(x2, 43);
    wire [63:0] r2_53 = rotl(x2, 53);
    wire [63:0] r2_61 = rotl(x2, 61);
    wire [63:0] x3 = (x2 ^ (r2_13 & r2_23) ^ (r2_33 & r2_43) ^ (r2_53 & r2_61) ^ r2_21);
    wire [63:0] k13 = rotl(k, 13);
    assign out = x3 ^ k13;
endmodule
