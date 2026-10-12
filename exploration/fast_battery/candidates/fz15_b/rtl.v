// fz15_b: gen_fused15.py
module fz15_b(
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
    wire [63:0] r0_9 = rotl(x0, 9);
    wire [63:0] r0_17 = rotl(x0, 17);
    wire [63:0] r0_33 = rotl(x0, 33);
    wire [63:0] x1 = (x0 ^ (r0_2 & r0_9) ^ r0_17 ^ r0_33);
    wire [63:0] r1_5 = rotl(x1, 5);
    wire [63:0] r1_13 = rotl(x1, 13);
    wire [63:0] r1_21 = rotl(x1, 21);
    wire [63:0] r1_39 = rotl(x1, 39);
    wire [63:0] x2 = (x1 ^ (r1_5 & r1_13) ^ r1_21 ^ r1_39);
    wire [63:0] r2_9 = rotl(x2, 9);
    wire [63:0] r2_19 = rotl(x2, 19);
    wire [63:0] r2_27 = rotl(x2, 27);
    wire [63:0] r2_45 = rotl(x2, 45);
    wire [63:0] x3 = (x2 ^ (r2_9 & r2_19) ^ r2_27 ^ r2_45);
    wire [63:0] r3_13 = rotl(x3, 13);
    wire [63:0] r3_27 = rotl(x3, 27);
    wire [63:0] r3_35 = rotl(x3, 35);
    wire [63:0] r3_53 = rotl(x3, 53);
    wire [63:0] x4 = (x3 ^ (r3_13 & r3_27) ^ r3_35 ^ r3_53);
    wire [63:0] k13 = rotl(k, 13);
    assign out = x4 ^ k13;
endmodule
