// fz16_d: gen_fused16.py
module fz16_d(
    input  wire [63:0] val,
    input  wire [63:0] key,
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
    wire [63:0] x0 = val ^ key;
    wire [63:0] r0_1 = rotl(x0, 1);
    wire [63:0] r0_5 = rotl(x0, 5);
    wire [63:0] r0_9 = rotl(x0, 9);
    wire [63:0] r0_13 = rotl(x0, 13);
    wire [63:0] x1 = (x0 ^ (r0_1 & r0_5) ^ r0_9 ^ r0_13);
    wire [63:0] r1_2 = rotl(x1, 2);
    wire [63:0] r1_6 = rotl(x1, 6);
    wire [63:0] r1_11 = rotl(x1, 11);
    wire [63:0] r1_17 = rotl(x1, 17);
    wire [63:0] x2 = (x1 ^ (r1_2 & r1_6) ^ r1_11 ^ r1_17);
    wire [63:0] r2_3 = rotl(x2, 3);
    wire [63:0] r2_8 = rotl(x2, 8);
    wire [63:0] r2_14 = rotl(x2, 14);
    wire [63:0] r2_19 = rotl(x2, 19);
    wire [63:0] x3 = (x2 ^ (r2_3 & r2_8) ^ r2_14 ^ r2_19);
    wire [63:0] r3_5 = rotl(x3, 5);
    wire [63:0] r3_11 = rotl(x3, 11);
    wire [63:0] r3_18 = rotl(x3, 18);
    wire [63:0] r3_23 = rotl(x3, 23);
    wire [63:0] x4 = (x3 ^ (r3_5 & r3_11) ^ r3_18 ^ r3_23);
    wire [63:0] r4_7 = rotl(x4, 7);
    wire [63:0] r4_13 = rotl(x4, 13);
    wire [63:0] r4_21 = rotl(x4, 21);
    wire [63:0] r4_27 = rotl(x4, 27);
    wire [63:0] x5 = (x4 ^ (r4_7 & r4_13) ^ r4_21 ^ r4_27);
    wire [63:0] k13 = rotl(key, 13);
    assign out = x5 ^ k13;
endmodule
