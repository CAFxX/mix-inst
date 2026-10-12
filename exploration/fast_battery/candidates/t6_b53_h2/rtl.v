// t6_b53_h2: batch-53 hetMA5 schedule (triage z=6.45, andpos=0)
module t6_b53_h2(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_p = {x0[32:0],x0[63:33]};
    wire [63:0] x1_q = {x0[34:0],x0[63:35]};
    wire [63:0] x1_r = {x0[3:0],x0[63:4]};
    wire [63:0] x1 = x0 ^ (x1_p & x1_q) ^ x1_r;
    wire [63:0] x2_s = {x1[45:0],x1[63:46]};
    wire [63:0] x2_a = {x1[52:0],x1[63:53]};
    wire [63:0] x2_b = {x1[28:0],x1[63:29]};
    wire [63:0] x2_d = {x1[8:0],x1[63:9]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[32:0],x2[63:33]};
    wire [63:0] x3_a = {x2[31:0],x2[63:32]};
    wire [63:0] x3_b = {x2[1:0],x2[63:2]};
    wire [63:0] x3_d = {x2[21:0],x2[63:22]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[45:0],x3[63:46]};
    wire [63:0] x4_a = {x3[37:0],x3[63:38]};
    wire [63:0] x4_b = {x3[22:0],x3[63:23]};
    wire [63:0] x4_d = {x3[38:0],x3[63:39]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[46:0],x4[63:47]};
    wire [63:0] x5_a = {x4[25:0],x4[63:26]};
    wire [63:0] x5_b = {x4[7:0],x4[63:8]};
    wire [63:0] x5_d = {x4[41:0],x4[63:42]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
