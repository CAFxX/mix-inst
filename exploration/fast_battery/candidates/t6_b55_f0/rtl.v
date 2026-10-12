// t6_b55_f0: batch-55 hetMA5p1f schedule (fisher triage z=2.90 n_reject=0, andpos=1)
module t6_b55_f0(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[20:0],x0[63:21]};
    wire [63:0] x1_a = {x0[41:0],x0[63:42]};
    wire [63:0] x1_b = {x0[19:0],x0[63:20]};
    wire [63:0] x1_d = {x0[18:0],x0[63:19]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_p = {x1[14:0],x1[63:15]};
    wire [63:0] x2_q = {x1[16:0],x1[63:17]};
    wire [63:0] x2_r = {x1[23:0],x1[63:24]};
    wire [63:0] x2 = x1 ^ (x2_p & x2_q) ^ x2_r;
    wire [63:0] x3_s = {x2[40:0],x2[63:41]};
    wire [63:0] x3_a = {x2[42:0],x2[63:43]};
    wire [63:0] x3_b = {x2[47:0],x2[63:48]};
    wire [63:0] x3_d = {x2[43:0],x2[63:44]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[59:0],x3[63:60]};
    wire [63:0] x4_a = {x3[58:0],x3[63:59]};
    wire [63:0] x4_b = {x3[51:0],x3[63:52]};
    wire [63:0] x4_d = {x3[25:0],x3[63:26]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[54:0],x4[63:55]};
    wire [63:0] x5_a = {x4[12:0],x4[63:13]};
    wire [63:0] x5_b = {x4[10:0],x4[63:11]};
    wire [63:0] x5_d = {x4[46:0],x4[63:47]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
