// fz15_a: gen_fused15.py
module fz15_a(
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
    wire [63:0] r0_7 = rotl(x0, 7);
    wire [63:0] r0_13 = rotl(x0, 13);
    wire [63:0] r0_29 = rotl(x0, 29);
    wire [63:0] x1 = (x0 ^ (r0_1 & r0_7) ^ r0_13 ^ r0_29);
    wire [63:0] r1_3 = rotl(x1, 3);
    wire [63:0] r1_11 = rotl(x1, 11);
    wire [63:0] r1_19 = rotl(x1, 19);
    wire [63:0] r1_37 = rotl(x1, 37);
    wire [63:0] x2 = (x1 ^ (r1_3 & r1_11) ^ r1_19 ^ r1_37);
    wire [63:0] r2_7 = rotl(x2, 7);
    wire [63:0] r2_17 = rotl(x2, 17);
    wire [63:0] r2_23 = rotl(x2, 23);
    wire [63:0] r2_43 = rotl(x2, 43);
    wire [63:0] x3 = (x2 ^ (r2_7 & r2_17) ^ r2_23 ^ r2_43);
    wire [63:0] r3_11 = rotl(x3, 11);
    wire [63:0] r3_23 = rotl(x3, 23);
    wire [63:0] r3_31 = rotl(x3, 31);
    wire [63:0] r3_47 = rotl(x3, 47);
    wire [63:0] x4 = (x3 ^ (r3_11 & r3_23) ^ r3_31 ^ r3_47);
    wire [63:0] k13 = rotl(k, 13);
    assign out = x4 ^ k13;
endmodule
