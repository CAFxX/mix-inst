// t6_b54_h7: batch-54 hetMA5p1 schedule (triage z=9.88, andpos=1)
module t6_b54_h7(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[35:0],x0[63:36]};
    wire [63:0] x1_a = {x0[29:0],x0[63:30]};
    wire [63:0] x1_b = {x0[40:0],x0[63:41]};
    wire [63:0] x1_d = {x0[57:0],x0[63:58]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_p = {x1[49:0],x1[63:50]};
    wire [63:0] x2_q = {x1[33:0],x1[63:34]};
    wire [63:0] x2_r = {x1[55:0],x1[63:56]};
    wire [63:0] x2 = x1 ^ (x2_p & x2_q) ^ x2_r;
    wire [63:0] x3_s = {x2[42:0],x2[63:43]};
    wire [63:0] x3_a = {x2[17:0],x2[63:18]};
    wire [63:0] x3_b = {x2[26:0],x2[63:27]};
    wire [63:0] x3_d = {x2[29:0],x2[63:30]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[3:0],x3[63:4]};
    wire [63:0] x4_a = {x3[48:0],x3[63:49]};
    wire [63:0] x4_b = {x3[32:0],x3[63:33]};
    wire [63:0] x4_d = {x3[29:0],x3[63:30]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[46:0],x4[63:47]};
    wire [63:0] x5_a = {x4[8:0],x4[63:9]};
    wire [63:0] x5_b = {x4[59:0],x4[63:60]};
    wire [63:0] x5_d = {x4[35:0],x4[63:36]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
