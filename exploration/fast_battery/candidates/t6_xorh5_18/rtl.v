// t6_xorh5_18: xorh5 hetero schedule (fisher triage z=3.62 n_reject=0)
module t6_xorh5_18(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1 = x0 ^ {x0[40:0],x0[63:41]} ^ {x0[16:0],x0[63:17]} ^ {x0[60:0],x0[63:61]} ^ {x0[12:0],x0[63:13]};
    wire [63:0] x2_s = {x1[13:0],x1[63:14]};
    wire [63:0] x2_a = {x1[25:0],x1[63:26]};
    wire [63:0] x2_b = {x1[17:0],x1[63:18]};
    wire [63:0] x2_d = x1;
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[50:0],x2[63:51]};
    wire [63:0] x3_a = {x2[37:0],x2[63:38]};
    wire [63:0] x3_b = {x2[1:0],x2[63:2]};
    wire [63:0] x3_d = {x2[59:0],x2[63:60]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[50:0],x3[63:51]};
    wire [63:0] x4_a = {x3[13:0],x3[63:14]};
    wire [63:0] x4_b = {x3[38:0],x3[63:39]};
    wire [63:0] x4_d = {x3[52:0],x3[63:53]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[10:0],x4[63:11]};
    wire [63:0] x5_a = {x4[18:0],x4[63:19]};
    wire [63:0] x5_b = {x4[6:0],x4[63:7]};
    wire [63:0] x5_d = {x4[54:0],x4[63:55]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
