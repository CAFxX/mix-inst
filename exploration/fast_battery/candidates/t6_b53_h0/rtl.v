// t6_b53_h0: batch-53 hetMA5 schedule (triage z=2.95, andpos=1)
module t6_b53_h0(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[35:0],x0[63:36]};
    wire [63:0] x1_a = {x0[34:0],x0[63:35]};
    wire [63:0] x1_b = {x0[47:0],x0[63:48]};
    wire [63:0] x1_d = {x0[26:0],x0[63:27]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_p = {x1[47:0],x1[63:48]};
    wire [63:0] x2_q = {x1[53:0],x1[63:54]};
    wire [63:0] x2_r = {x1[58:0],x1[63:59]};
    wire [63:0] x2 = x1 ^ (x2_p & x2_q) ^ x2_r;
    wire [63:0] x3_s = {x2[49:0],x2[63:50]};
    wire [63:0] x3_a = {x2[46:0],x2[63:47]};
    wire [63:0] x3_b = {x2[23:0],x2[63:24]};
    wire [63:0] x3_d = {x2[2:0],x2[63:3]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[52:0],x3[63:53]};
    wire [63:0] x4_a = {x3[13:0],x3[63:14]};
    wire [63:0] x4_b = {x3[28:0],x3[63:29]};
    wire [63:0] x4_d = {x3[43:0],x3[63:44]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[40:0],x4[63:41]};
    wire [63:0] x5_a = {x4[53:0],x4[63:54]};
    wire [63:0] x5_b = {x4[32:0],x4[63:33]};
    wire [63:0] x5_d = {x4[39:0],x4[63:40]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
