// t6_xorh5_17: xorh5 hetero schedule (fisher triage z=3.55 n_reject=0)
module t6_xorh5_17(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[25:0],x0[63:26]};
    wire [63:0] x1_a = {x0[60:0],x0[63:61]};
    wire [63:0] x1_b = {x0[47:0],x0[63:48]};
    wire [63:0] x1_d = {x0[39:0],x0[63:40]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2 = x1 ^ {x1[25:0],x1[63:26]} ^ {x1[35:0],x1[63:36]} ^ {x1[45:0],x1[63:46]} ^ {x1[6:0],x1[63:7]};
    wire [63:0] x3_s = {x2[38:0],x2[63:39]};
    wire [63:0] x3_a = {x2[6:0],x2[63:7]};
    wire [63:0] x3_b = {x2[26:0],x2[63:27]};
    wire [63:0] x3_d = {x2[38:0],x2[63:39]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[51:0],x3[63:52]};
    wire [63:0] x4_a = {x3[33:0],x3[63:34]};
    wire [63:0] x4_b = {x3[13:0],x3[63:14]};
    wire [63:0] x4_d = {x3[30:0],x3[63:31]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[9:0],x4[63:10]};
    wire [63:0] x5_a = {x4[27:0],x4[63:28]};
    wire [63:0] x5_b = {x4[16:0],x4[63:17]};
    wire [63:0] x5_d = {x4[56:0],x4[63:57]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
