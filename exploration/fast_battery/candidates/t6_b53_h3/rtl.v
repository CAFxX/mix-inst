// t6_b53_h3: batch-53 hetMA5 schedule (triage z=9.18, andpos=4)
module t6_b53_h3(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[10:0],x0[63:11]};
    wire [63:0] x1_a = {x0[52:0],x0[63:53]};
    wire [63:0] x1_b = {x0[51:0],x0[63:52]};
    wire [63:0] x1_d = {x0[42:0],x0[63:43]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[31:0],x1[63:32]};
    wire [63:0] x2_a = {x1[34:0],x1[63:35]};
    wire [63:0] x2_b = {x1[15:0],x1[63:16]};
    wire [63:0] x2_d = {x1[19:0],x1[63:20]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[62:0],x2[63:63]};
    wire [63:0] x3_a = {x2[13:0],x2[63:14]};
    wire [63:0] x3_b = {x2[28:0],x2[63:29]};
    wire [63:0] x3_d = {x2[24:0],x2[63:25]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[26:0],x3[63:27]};
    wire [63:0] x4_a = {x3[0:0],x3[63:1]};
    wire [63:0] x4_b = {x3[47:0],x3[63:48]};
    wire [63:0] x4_d = {x3[46:0],x3[63:47]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_p = {x4[17:0],x4[63:18]};
    wire [63:0] x5_q = {x4[18:0],x4[63:19]};
    wire [63:0] x5_r = {x4[8:0],x4[63:9]};
    wire [63:0] x5 = x4 ^ (x5_p & x5_q) ^ x5_r;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
