// t6_xorh5_12: xorh5 hetero schedule (fisher triage z=3.02 n_reject=0)
module t6_xorh5_12(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[22:0],x0[63:23]};
    wire [63:0] x1_a = {x0[14:0],x0[63:15]};
    wire [63:0] x1_b = {x0[62:0],x0[63:63]};
    wire [63:0] x1_d = {x0[31:0],x0[63:32]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2 = x1 ^ {x1[29:0],x1[63:30]} ^ {x1[26:0],x1[63:27]} ^ {x1[60:0],x1[63:61]} ^ {x1[54:0],x1[63:55]};
    wire [63:0] x3_s = {x2[10:0],x2[63:11]};
    wire [63:0] x3_a = {x2[21:0],x2[63:22]};
    wire [63:0] x3_b = x2;
    wire [63:0] x3_d = {x2[57:0],x2[63:58]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[0:0],x3[63:1]};
    wire [63:0] x4_a = {x3[7:0],x3[63:8]};
    wire [63:0] x4_b = {x3[59:0],x3[63:60]};
    wire [63:0] x4_d = {x3[43:0],x3[63:44]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[37:0],x4[63:38]};
    wire [63:0] x5_a = {x4[43:0],x4[63:44]};
    wire [63:0] x5_b = {x4[61:0],x4[63:62]};
    wire [63:0] x5_d = {x4[25:0],x4[63:26]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
