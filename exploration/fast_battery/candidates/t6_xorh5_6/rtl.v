// t6_xorh5_6: xorh5 hetero schedule (fisher triage z=2.87 n_reject=0)
module t6_xorh5_6(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[55:0],x0[63:56]};
    wire [63:0] x1_a = {x0[58:0],x0[63:59]};
    wire [63:0] x1_b = {x0[53:0],x0[63:54]};
    wire [63:0] x1_d = {x0[17:0],x0[63:18]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[58:0],x1[63:59]};
    wire [63:0] x2_a = {x1[33:0],x1[63:34]};
    wire [63:0] x2_b = {x1[55:0],x1[63:56]};
    wire [63:0] x2_d = {x1[31:0],x1[63:32]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[57:0],x2[63:58]};
    wire [63:0] x3_a = {x2[44:0],x2[63:45]};
    wire [63:0] x3_b = {x2[59:0],x2[63:60]};
    wire [63:0] x3_d = {x2[3:0],x2[63:4]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[16:0],x3[63:17]};
    wire [63:0] x4_a = {x3[40:0],x3[63:41]};
    wire [63:0] x4_b = {x3[19:0],x3[63:20]};
    wire [63:0] x4_d = {x3[15:0],x3[63:16]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5 = x4 ^ {x4[41:0],x4[63:42]} ^ {x4[21:0],x4[63:22]} ^ {x4[22:0],x4[63:23]} ^ {x4[36:0],x4[63:37]};
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
