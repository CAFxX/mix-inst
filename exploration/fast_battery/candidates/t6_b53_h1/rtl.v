// t6_b53_h1: batch-53 hetMA5 schedule (triage z=3.01, andpos=3)
module t6_b53_h1(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[15:0],x0[63:16]};
    wire [63:0] x1_a = {x0[57:0],x0[63:58]};
    wire [63:0] x1_b = {x0[14:0],x0[63:15]};
    wire [63:0] x1_d = {x0[25:0],x0[63:26]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[32:0],x1[63:33]};
    wire [63:0] x2_a = {x1[60:0],x1[63:61]};
    wire [63:0] x2_b = {x1[57:0],x1[63:58]};
    wire [63:0] x2_d = {x1[27:0],x1[63:28]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[19:0],x2[63:20]};
    wire [63:0] x3_a = {x2[30:0],x2[63:31]};
    wire [63:0] x3_b = {x2[7:0],x2[63:8]};
    wire [63:0] x3_d = {x2[31:0],x2[63:32]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_p = {x3[43:0],x3[63:44]};
    wire [63:0] x4_q = {x3[21:0],x3[63:22]};
    wire [63:0] x4_r = {x3[44:0],x3[63:45]};
    wire [63:0] x4 = x3 ^ (x4_p & x4_q) ^ x4_r;
    wire [63:0] x5_s = {x4[47:0],x4[63:48]};
    wire [63:0] x5_a = {x4[32:0],x4[63:33]};
    wire [63:0] x5_b = {x4[29:0],x4[63:30]};
    wire [63:0] x5_d = {x4[50:0],x4[63:51]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
