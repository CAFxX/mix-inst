// t6_b54_h5: batch-54 hetMA5p1 schedule (triage z=7.77, andpos=1)
module t6_b54_h5(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[36:0],x0[63:37]};
    wire [63:0] x1_a = {x0[47:0],x0[63:48]};
    wire [63:0] x1_b = {x0[33:0],x0[63:34]};
    wire [63:0] x1_d = {x0[32:0],x0[63:33]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_p = {x1[51:0],x1[63:52]};
    wire [63:0] x2_q = {x1[9:0],x1[63:10]};
    wire [63:0] x2_r = {x1[60:0],x1[63:61]};
    wire [63:0] x2 = x1 ^ (x2_p & x2_q) ^ x2_r;
    wire [63:0] x3_s = {x2[1:0],x2[63:2]};
    wire [63:0] x3_a = {x2[11:0],x2[63:12]};
    wire [63:0] x3_b = {x2[10:0],x2[63:11]};
    wire [63:0] x3_d = {x2[18:0],x2[63:19]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[53:0],x3[63:54]};
    wire [63:0] x4_a = {x3[36:0],x3[63:37]};
    wire [63:0] x4_b = {x3[47:0],x3[63:48]};
    wire [63:0] x4_d = {x3[49:0],x3[63:50]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[43:0],x4[63:44]};
    wire [63:0] x5_a = {x4[24:0],x4[63:25]};
    wire [63:0] x5_b = {x4[27:0],x4[63:28]};
    wire [63:0] x5_d = {x4[31:0],x4[63:32]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
