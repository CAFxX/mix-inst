// fz14_dchi4a: gen_fused14.py
module fz14_dchi4a(
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
    wire [63:0] r0_29 = rotl(x0, 29);
    wire [63:0] x1 = (x0 ^ (r0_1 & r0_7) ^ (r0_13 & r0_29) ^ r0_5);
    wire [63:0] r1_5 = rotl(x1, 5);
    wire [63:0] r1_11 = rotl(x1, 11);
    wire [63:0] r1_13 = rotl(x1, 13);
    wire [63:0] r1_23 = rotl(x1, 23);
    wire [63:0] r1_41 = rotl(x1, 41);
    wire [63:0] x2 = (x1 ^ (r1_5 & r1_13) ^ (r1_23 & r1_41) ^ r1_11);
    wire [63:0] r2_11 = rotl(x2, 11);
    wire [63:0] r2_17 = rotl(x2, 17);
    wire [63:0] r2_23 = rotl(x2, 23);
    wire [63:0] r2_33 = rotl(x2, 33);
    wire [63:0] r2_51 = rotl(x2, 51);
    wire [63:0] x3 = (x2 ^ (r2_11 & r2_23) ^ (r2_33 & r2_51) ^ r2_17);
    wire [63:0] r3_17 = rotl(x3, 17);
    wire [63:0] r3_23 = rotl(x3, 23);
    wire [63:0] r3_31 = rotl(x3, 31);
    wire [63:0] r3_43 = rotl(x3, 43);
    wire [63:0] r3_59 = rotl(x3, 59);
    wire [63:0] x4 = (x3 ^ (r3_17 & r3_31) ^ (r3_43 & r3_59) ^ r3_23);
    wire [63:0] k13 = rotl(k, 13);
    assign out = x4 ^ k13;
endmodule
