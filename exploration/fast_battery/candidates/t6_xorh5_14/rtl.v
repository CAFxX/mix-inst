// t6_xorh5_14: xorh5 hetero schedule (fisher triage z=3.26 n_reject=0)
module t6_xorh5_14(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1 = x0 ^ {x0[56:0],x0[63:57]} ^ {x0[3:0],x0[63:4]} ^ {x0[35:0],x0[63:36]} ^ {x0[23:0],x0[63:24]};
    wire [63:0] x2_s = {x1[15:0],x1[63:16]};
    wire [63:0] x2_a = {x1[21:0],x1[63:22]};
    wire [63:0] x2_b = {x1[24:0],x1[63:25]};
    wire [63:0] x2_d = {x1[15:0],x1[63:16]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[18:0],x2[63:19]};
    wire [63:0] x3_a = {x2[35:0],x2[63:36]};
    wire [63:0] x3_b = {x2[4:0],x2[63:5]};
    wire [63:0] x3_d = {x2[40:0],x2[63:41]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[7:0],x3[63:8]};
    wire [63:0] x4_a = {x3[61:0],x3[63:62]};
    wire [63:0] x4_b = {x3[48:0],x3[63:49]};
    wire [63:0] x4_d = {x3[50:0],x3[63:51]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[30:0],x4[63:31]};
    wire [63:0] x5_a = {x4[22:0],x4[63:23]};
    wire [63:0] x5_b = {x4[43:0],x4[63:44]};
    wire [63:0] x5_d = {x4[2:0],x4[63:3]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
