// fz15_d: gen_fused15.py
module fz15_d(
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
    wire [63:0] r1_5 = rotl(x1, 5);
    wire [63:0] r1_15 = rotl(x1, 15);
    wire [63:0] r1_25 = rotl(x1, 25);
    wire [63:0] r1_41 = rotl(x1, 41);
    wire [63:0] x2 = (x1 ^ (r1_5 & r1_15) ^ r1_25 ^ r1_41);
    wire [63:0] r2_11 = rotl(x2, 11);
    wire [63:0] r2_23 = rotl(x2, 23);
    wire [63:0] r2_37 = rotl(x2, 37);
    wire [63:0] r2_53 = rotl(x2, 53);
    wire [63:0] x3 = (x2 ^ (r2_11 & r2_23) ^ r2_37 ^ r2_53);
    wire [63:0] k13 = rotl(k, 13);
    assign out = x3 ^ k13;
endmodule
