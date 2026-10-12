// fz16_c: gen_fused16.py
module fz16_c(
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
    wire [63:0] r0_7 = rotl(x0, 7);
    wire [63:0] r0_13 = rotl(x0, 13);
    wire [63:0] r0_29 = rotl(x0, 29);
    wire [63:0] r0_37 = rotl(x0, 37);
    wire [63:0] r0_43 = rotl(x0, 43);
    wire [63:0] x1 = (x0 ^ (r0_1 & (r0_7 ^ r0_13)) ^ r0_29 ^ r0_37 ^ r0_43);
    wire [63:0] r1_3 = rotl(x1, 3);
    wire [63:0] r1_11 = rotl(x1, 11);
    wire [63:0] r1_19 = rotl(x1, 19);
    wire [63:0] r1_31 = rotl(x1, 31);
    wire [63:0] r1_41 = rotl(x1, 41);
    wire [63:0] r1_47 = rotl(x1, 47);
    wire [63:0] x2 = (x1 ^ (r1_3 & (r1_11 ^ r1_19)) ^ r1_31 ^ r1_41 ^ r1_47);
    wire [63:0] r2_5 = rotl(x2, 5);
    wire [63:0] r2_15 = rotl(x2, 15);
    wire [63:0] r2_25 = rotl(x2, 25);
    wire [63:0] r2_37 = rotl(x2, 37);
    wire [63:0] r2_43 = rotl(x2, 43);
    wire [63:0] r2_53 = rotl(x2, 53);
    wire [63:0] x3 = (x2 ^ (r2_5 & (r2_15 ^ r2_25)) ^ r2_37 ^ r2_43 ^ r2_53);
    wire [63:0] r3_9 = rotl(x3, 9);
    wire [63:0] r3_21 = rotl(x3, 21);
    wire [63:0] r3_31 = rotl(x3, 31);
    wire [63:0] r3_41 = rotl(x3, 41);
    wire [63:0] r3_49 = rotl(x3, 49);
    wire [63:0] r3_57 = rotl(x3, 57);
    wire [63:0] x4 = (x3 ^ (r3_9 & (r3_21 ^ r3_31)) ^ r3_41 ^ r3_49 ^ r3_57);
    wire [63:0] k13 = rotl(key, 13);
    assign out = x4 ^ k13;
endmodule
