// t6_b57_0: batch-57 muxD5f schedule (fisher triage z=2.36 n_reject=0)
module t6_b57_0(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[50:0],x0[63:51]};
    wire [63:0] x1_a = {x0[48:0],x0[63:49]};
    wire [63:0] x1_b = {x0[51:0],x0[63:52]};
    wire [63:0] x1_d = {x0[20:0],x0[63:21]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[31:0],x1[63:32]};
    wire [63:0] x2_a = {x1[8:0],x1[63:9]};
    wire [63:0] x2_b = {x1[34:0],x1[63:35]};
    wire [63:0] x2_d = {x1[52:0],x1[63:53]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[46:0],x2[63:47]};
    wire [63:0] x3_a = {x2[5:0],x2[63:6]};
    wire [63:0] x3_b = {x2[36:0],x2[63:37]};
    wire [63:0] x3_d = {x2[37:0],x2[63:38]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[21:0],x3[63:22]};
    wire [63:0] x4_a = {x3[36:0],x3[63:37]};
    wire [63:0] x4_b = {x3[6:0],x3[63:7]};
    wire [63:0] x4_d = {x3[55:0],x3[63:56]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[19:0],x4[63:20]};
    wire [63:0] x5_a = {x4[4:0],x4[63:5]};
    wire [63:0] x5_b = {x4[60:0],x4[63:61]};
    wire [63:0] x5_d = {x4[56:0],x4[63:57]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
