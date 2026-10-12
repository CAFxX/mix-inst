// t6_b54_h2: batch-54 hetMA5p1 schedule (triage z=4.58, andpos=1)
module t6_b54_h2(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[39:0],x0[63:40]};
    wire [63:0] x1_a = {x0[23:0],x0[63:24]};
    wire [63:0] x1_b = {x0[42:0],x0[63:43]};
    wire [63:0] x1_d = {x0[61:0],x0[63:62]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_p = {x1[29:0],x1[63:30]};
    wire [63:0] x2_q = {x1[17:0],x1[63:18]};
    wire [63:0] x2_r = {x1[34:0],x1[63:35]};
    wire [63:0] x2 = x1 ^ (x2_p & x2_q) ^ x2_r;
    wire [63:0] x3_s = {x2[32:0],x2[63:33]};
    wire [63:0] x3_a = {x2[6:0],x2[63:7]};
    wire [63:0] x3_b = {x2[46:0],x2[63:47]};
    wire [63:0] x3_d = {x2[52:0],x2[63:53]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[35:0],x3[63:36]};
    wire [63:0] x4_a = {x3[42:0],x3[63:43]};
    wire [63:0] x4_b = {x3[49:0],x3[63:50]};
    wire [63:0] x4_d = {x3[18:0],x3[63:19]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[56:0],x4[63:57]};
    wire [63:0] x5_a = {x4[36:0],x4[63:37]};
    wire [63:0] x5_b = {x4[0:0],x4[63:1]};
    wire [63:0] x5_d = {x4[15:0],x4[63:16]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
