// t6_b57_3: batch-57 muxD5f schedule (fisher triage z=2.83 n_reject=0)
module t6_b57_3(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[48:0],x0[63:49]};
    wire [63:0] x1_a = {x0[42:0],x0[63:43]};
    wire [63:0] x1_b = {x0[50:0],x0[63:51]};
    wire [63:0] x1_d = {x0[47:0],x0[63:48]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[5:0],x1[63:6]};
    wire [63:0] x2_a = {x1[58:0],x1[63:59]};
    wire [63:0] x2_b = {x1[30:0],x1[63:31]};
    wire [63:0] x2_d = {x1[38:0],x1[63:39]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[30:0],x2[63:31]};
    wire [63:0] x3_a = {x2[16:0],x2[63:17]};
    wire [63:0] x3_b = {x2[36:0],x2[63:37]};
    wire [63:0] x3_d = {x2[1:0],x2[63:2]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[62:0],x3[63:63]};
    wire [63:0] x4_a = {x3[22:0],x3[63:23]};
    wire [63:0] x4_b = {x3[16:0],x3[63:17]};
    wire [63:0] x4_d = {x3[41:0],x3[63:42]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[55:0],x4[63:56]};
    wire [63:0] x5_a = {x4[54:0],x4[63:55]};
    wire [63:0] x5_b = {x4[40:0],x4[63:41]};
    wire [63:0] x5_d = {x4[4:0],x4[63:5]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
