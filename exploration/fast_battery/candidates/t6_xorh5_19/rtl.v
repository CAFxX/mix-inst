// t6_xorh5_19: xorh5 hetero schedule (fisher triage z=3.99 n_reject=0)
module t6_xorh5_19(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[29:0],x0[63:30]};
    wire [63:0] x1_a = {x0[9:0],x0[63:10]};
    wire [63:0] x1_b = {x0[30:0],x0[63:31]};
    wire [63:0] x1_d = {x0[58:0],x0[63:59]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[40:0],x1[63:41]};
    wire [63:0] x2_a = {x1[7:0],x1[63:8]};
    wire [63:0] x2_b = {x1[28:0],x1[63:29]};
    wire [63:0] x2_d = {x1[27:0],x1[63:28]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[10:0],x2[63:11]};
    wire [63:0] x3_a = {x2[55:0],x2[63:56]};
    wire [63:0] x3_b = {x2[61:0],x2[63:62]};
    wire [63:0] x3_d = {x2[21:0],x2[63:22]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[35:0],x3[63:36]};
    wire [63:0] x4_a = {x3[23:0],x3[63:24]};
    wire [63:0] x4_b = {x3[0:0],x3[63:1]};
    wire [63:0] x4_d = {x3[43:0],x3[63:44]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5 = x4 ^ {x4[25:0],x4[63:26]} ^ {x4[49:0],x4[63:50]} ^ {x4[4:0],x4[63:5]} ^ {x4[5:0],x4[63:6]};
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
