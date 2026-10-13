// t6_xorh5_13: xorh5 hetero schedule (fisher triage z=3.19 n_reject=0)
module t6_xorh5_13(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[61:0],x0[63:62]};
    wire [63:0] x1_a = {x0[3:0],x0[63:4]};
    wire [63:0] x1_b = {x0[25:0],x0[63:26]};
    wire [63:0] x1_d = {x0[34:0],x0[63:35]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2 = x1 ^ {x1[46:0],x1[63:47]} ^ {x1[56:0],x1[63:57]} ^ {x1[16:0],x1[63:17]} ^ {x1[15:0],x1[63:16]};
    wire [63:0] x3_s = {x2[42:0],x2[63:43]};
    wire [63:0] x3_a = {x2[46:0],x2[63:47]};
    wire [63:0] x3_b = {x2[60:0],x2[63:61]};
    wire [63:0] x3_d = {x2[51:0],x2[63:52]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[62:0],x3[63:63]};
    wire [63:0] x4_a = {x3[41:0],x3[63:42]};
    wire [63:0] x4_b = {x3[51:0],x3[63:52]};
    wire [63:0] x4_d = {x3[45:0],x3[63:46]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[31:0],x4[63:32]};
    wire [63:0] x5_a = {x4[52:0],x4[63:53]};
    wire [63:0] x5_b = {x4[40:0],x4[63:41]};
    wire [63:0] x5_d = {x4[38:0],x4[63:39]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
