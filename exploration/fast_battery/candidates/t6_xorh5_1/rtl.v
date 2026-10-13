// t6_xorh5_1: xorh5 hetero schedule (fisher triage z=2.56 n_reject=0)
module t6_xorh5_1(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1 = x0 ^ {x0[7:0],x0[63:8]} ^ {x0[26:0],x0[63:27]} ^ {x0[43:0],x0[63:44]} ^ {x0[50:0],x0[63:51]};
    wire [63:0] x2_s = {x1[34:0],x1[63:35]};
    wire [63:0] x2_a = {x1[28:0],x1[63:29]};
    wire [63:0] x2_b = {x1[35:0],x1[63:36]};
    wire [63:0] x2_d = {x1[51:0],x1[63:52]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[3:0],x2[63:4]};
    wire [63:0] x3_a = {x2[27:0],x2[63:28]};
    wire [63:0] x3_b = {x2[14:0],x2[63:15]};
    wire [63:0] x3_d = {x2[42:0],x2[63:43]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[6:0],x3[63:7]};
    wire [63:0] x4_a = {x3[18:0],x3[63:19]};
    wire [63:0] x4_b = {x3[61:0],x3[63:62]};
    wire [63:0] x4_d = {x3[57:0],x3[63:58]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[22:0],x4[63:23]};
    wire [63:0] x5_a = {x4[24:0],x4[63:25]};
    wire [63:0] x5_b = {x4[37:0],x4[63:38]};
    wire [63:0] x5_d = {x4[41:0],x4[63:42]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
