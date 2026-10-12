// fz14_dchi4b: gen_fused14.py
module fz14_dchi4b(
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
    wire [63:0] r0_2 = rotl(x0, 2);
    wire [63:0] r0_7 = rotl(x0, 7);
    wire [63:0] r0_9 = rotl(x0, 9);
    wire [63:0] r0_17 = rotl(x0, 17);
    wire [63:0] r0_35 = rotl(x0, 35);
    wire [63:0] x1 = (x0 ^ (r0_2 & r0_9) ^ (r0_17 & r0_35) ^ r0_7);
    wire [63:0] r1_7 = rotl(x1, 7);
    wire [63:0] r1_13 = rotl(x1, 13);
    wire [63:0] r1_15 = rotl(x1, 15);
    wire [63:0] r1_27 = rotl(x1, 27);
    wire [63:0] r1_45 = rotl(x1, 45);
    wire [63:0] x2 = (x1 ^ (r1_7 & r1_15) ^ (r1_27 & r1_45) ^ r1_13);
    wire [63:0] r2_13 = rotl(x2, 13);
    wire [63:0] r2_19 = rotl(x2, 19);
    wire [63:0] r2_25 = rotl(x2, 25);
    wire [63:0] r2_37 = rotl(x2, 37);
    wire [63:0] r2_55 = rotl(x2, 55);
    wire [63:0] x3 = (x2 ^ (r2_13 & r2_25) ^ (r2_37 & r2_55) ^ r2_19);
    wire [63:0] r3_19 = rotl(x3, 19);
    wire [63:0] r3_27 = rotl(x3, 27);
    wire [63:0] r3_33 = rotl(x3, 33);
    wire [63:0] r3_47 = rotl(x3, 47);
    wire [63:0] r3_61 = rotl(x3, 61);
    wire [63:0] x4 = (x3 ^ (r3_19 & r3_33) ^ (r3_47 & r3_61) ^ r3_27);
    wire [63:0] k13 = rotl(k, 13);
    assign out = x4 ^ k13;
endmodule
