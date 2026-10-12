// hyb29_mu5_002: batch-29 MU5-324local schedule (fisher triage z=2.44 n_reject=0)
module hyb29_mu5_002(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[2:0],x0[63:3]};
    wire [63:0] x1_a = {x0[13:0],x0[63:14]};
    wire [63:0] x1_b = {x0[8:0],x0[63:9]};
    wire [63:0] x1_d = {x0[61:0],x0[63:62]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[15:0],x1[63:16]};
    wire [63:0] x2_a = {x1[5:0],x1[63:6]};
    wire [63:0] x2_b = {x1[40:0],x1[63:41]};
    wire [63:0] x2_d = {x1[33:0],x1[63:34]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[19:0],x2[63:20]};
    wire [63:0] x3_a = {x2[18:0],x2[63:19]};
    wire [63:0] x3_b = {x2[56:0],x2[63:57]};
    wire [63:0] x3_d = {x2[23:0],x2[63:24]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[14:0],x3[63:15]};
    wire [63:0] x4_a = {x3[37:0],x3[63:38]};
    wire [63:0] x4_b = {x3[31:0],x3[63:32]};
    wire [63:0] x4_d = {x3[28:0],x3[63:29]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[17:0],x4[63:18]};
    wire [63:0] x5_a = {x4[12:0],x4[63:13]};
    wire [63:0] x5_b = {x4[20:0],x4[63:21]};
    wire [63:0] x5_d = {x4[19:0],x4[63:20]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
