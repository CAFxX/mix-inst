// fz18_b: gen_fused18.py (split tree)
module fz18_b(
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
    wire [63:0] and0 = r0_13 & r0_27;
    wire [63:0] t0a = x0 ^ r0_37;
    wire [63:0] t0b = and0 ^ r0_55;
    wire [63:0] x1 = t0a ^ t0b;
    wire [63:0] r1_9 = rotl(x1, 9);
    wire [63:0] r1_21 = rotl(x1, 21);
    wire [63:0] r1_31 = rotl(x1, 31);
    wire [63:0] r1_49 = rotl(x1, 49);
    wire [63:0] and1 = r1_9 & r1_21;
    wire [63:0] t1a = x1 ^ r1_31;
    wire [63:0] t1b = and1 ^ r1_49;
    wire [63:0] x2 = t1a ^ t1b;
    wire [63:0] r2_5 = rotl(x2, 5);
    wire [63:0] r2_15 = rotl(x2, 15);
    wire [63:0] r2_25 = rotl(x2, 25);
    wire [63:0] r2_41 = rotl(x2, 41);
    wire [63:0] and2 = r2_5 & r2_15;
    wire [63:0] t2a = x2 ^ r2_25;
    wire [63:0] t2b = and2 ^ r2_41;
    wire [63:0] x3 = t2a ^ t2b;
    wire [63:0] r3_3 = rotl(x3, 3);
    wire [63:0] r3_11 = rotl(x3, 11);
    wire [63:0] r3_19 = rotl(x3, 19);
    wire [63:0] r3_37 = rotl(x3, 37);
    wire [63:0] and3 = r3_3 & r3_11;
    wire [63:0] t3a = x3 ^ r3_19;
    wire [63:0] t3b = and3 ^ r3_37;
    wire [63:0] x4 = t3a ^ t3b;
    wire [63:0] r4_1 = rotl(x4, 1);
    wire [63:0] r4_7 = rotl(x4, 7);
    wire [63:0] r4_13 = rotl(x4, 13);
    wire [63:0] r4_29 = rotl(x4, 29);
    wire [63:0] and4 = r4_1 & r4_7;
    wire [63:0] t4a = x4 ^ r4_13;
    wire [63:0] t4b = and4 ^ r4_29;
    wire [63:0] x5 = t4a ^ t4b;
    wire [63:0] k13 = rotl(key, 13);
    assign out = x5 ^ k13;
endmodule
