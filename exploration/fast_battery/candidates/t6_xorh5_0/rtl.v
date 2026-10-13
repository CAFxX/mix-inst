// t6_xorh5_0: xorh5 hetero schedule (fisher triage z=2.43 n_reject=0)
module t6_xorh5_0(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1 = x0 ^ {x0[34:0],x0[63:35]} ^ {x0[56:0],x0[63:57]} ^ {x0[21:0],x0[63:22]} ^ {x0[8:0],x0[63:9]};
    wire [63:0] x2_s = {x1[50:0],x1[63:51]};
    wire [63:0] x2_a = {x1[12:0],x1[63:13]};
    wire [63:0] x2_b = {x1[56:0],x1[63:57]};
    wire [63:0] x2_d = {x1[17:0],x1[63:18]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[60:0],x2[63:61]};
    wire [63:0] x3_a = {x2[42:0],x2[63:43]};
    wire [63:0] x3_b = {x2[8:0],x2[63:9]};
    wire [63:0] x3_d = {x2[7:0],x2[63:8]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[5:0],x3[63:6]};
    wire [63:0] x4_a = {x3[31:0],x3[63:32]};
    wire [63:0] x4_b = {x3[48:0],x3[63:49]};
    wire [63:0] x4_d = {x3[49:0],x3[63:50]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[7:0],x4[63:8]};
    wire [63:0] x5_a = {x4[10:0],x4[63:11]};
    wire [63:0] x5_b = {x4[27:0],x4[63:28]};
    wire [63:0] x5_d = {x4[48:0],x4[63:49]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
