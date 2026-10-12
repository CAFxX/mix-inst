// fz16_e: gen_fused16.py
module fz16_e(
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
    wire [63:0] r0_13 = rotl(x0, 13);
    wire [63:0] r0_27 = rotl(x0, 27);
    wire [63:0] r0_37 = rotl(x0, 37);
    wire [63:0] r0_55 = rotl(x0, 55);
    wire [63:0] x1 = (x0 ^ (r0_13 & r0_27) ^ r0_37 ^ r0_55);
    wire [63:0] r1_9 = rotl(x1, 9);
    wire [63:0] r1_21 = rotl(x1, 21);
    wire [63:0] r1_31 = rotl(x1, 31);
    wire [63:0] r1_49 = rotl(x1, 49);
    wire [63:0] x2 = (x1 ^ (r1_9 & r1_21) ^ r1_31 ^ r1_49);
    wire [63:0] r2_5 = rotl(x2, 5);
    wire [63:0] r2_15 = rotl(x2, 15);
    wire [63:0] r2_25 = rotl(x2, 25);
    wire [63:0] r2_41 = rotl(x2, 41);
    wire [63:0] x3 = (x2 ^ (r2_5 & r2_15) ^ r2_25 ^ r2_41);
    wire [63:0] r3_3 = rotl(x3, 3);
    wire [63:0] r3_11 = rotl(x3, 11);
    wire [63:0] r3_19 = rotl(x3, 19);
    wire [63:0] r3_37 = rotl(x3, 37);
    wire [63:0] x4 = (x3 ^ (r3_3 & r3_11) ^ r3_19 ^ r3_37);
    wire [63:0] r4_1 = rotl(x4, 1);
    wire [63:0] r4_7 = rotl(x4, 7);
    wire [63:0] r4_13 = rotl(x4, 13);
    wire [63:0] r4_29 = rotl(x4, 29);
    wire [63:0] x5 = (x4 ^ (r4_1 & r4_7) ^ r4_13 ^ r4_29);
    wire [63:0] k13 = rotl(key, 13);
    assign out = x5 ^ k13;
endmodule
