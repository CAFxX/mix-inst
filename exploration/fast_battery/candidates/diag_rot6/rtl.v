// diag_rot6: diagnostic: 6-stage rotation-only
module diag_rot6(
    input [63:0] val,
    input [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] s0a = {x0[54:0], x0[63:55]};
    wire [63:0] s0b = {x0[36:0], x0[63:37]};
    wire [63:0] x1 = x0 ^ s0a ^ s0b;
    wire [63:0] s1a = {x1[48:0], x1[63:49]};
    wire [63:0] s1b = {x1[30:0], x1[63:31]};
    wire [63:0] x2 = x1 ^ s1a ^ s1b;
    wire [63:0] s2a = {x2[42:0], x2[63:43]};
    wire [63:0] s2b = {x2[24:0], x2[63:25]};
    wire [63:0] x3 = x2 ^ s2a ^ s2b;
    wire [63:0] s3a = {x3[36:0], x3[63:37]};
    wire [63:0] s3b = {x3[18:0], x3[63:19]};
    wire [63:0] x4 = x3 ^ s3a ^ s3b;
    wire [63:0] s4a = {x4[30:0], x4[63:31]};
    wire [63:0] s4b = {x4[12:0], x4[63:13]};
    wire [63:0] x5 = x4 ^ s4a ^ s4b;
    wire [63:0] s5a = {x5[24:0], x5[63:25]};
    wire [63:0] s5b = {x5[6:0], x5[63:7]};
    wire [63:0] x6 = x5 ^ s5a ^ s5b;
    wire [63:0] kr = {key[50:0], key[63:51]};
    assign out = x6 ^ kr;
endmodule
