// t6_xorh5_16: xorh5 hetero schedule (fisher triage z=3.46 n_reject=0)
module t6_xorh5_16(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[50:0],x0[63:51]};
    wire [63:0] x1_a = {x0[9:0],x0[63:10]};
    wire [63:0] x1_b = {x0[40:0],x0[63:41]};
    wire [63:0] x1_d = {x0[38:0],x0[63:39]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[10:0],x1[63:11]};
    wire [63:0] x2_a = {x1[16:0],x1[63:17]};
    wire [63:0] x2_b = {x1[54:0],x1[63:55]};
    wire [63:0] x2_d = {x1[19:0],x1[63:20]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[3:0],x2[63:4]};
    wire [63:0] x3_a = {x2[0:0],x2[63:1]};
    wire [63:0] x3_b = {x2[10:0],x2[63:11]};
    wire [63:0] x3_d = {x2[51:0],x2[63:52]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[59:0],x3[63:60]};
    wire [63:0] x4_a = {x3[48:0],x3[63:49]};
    wire [63:0] x4_b = {x3[21:0],x3[63:22]};
    wire [63:0] x4_d = {x3[2:0],x3[63:3]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5 = x4 ^ {x4[48:0],x4[63:49]} ^ {x4[42:0],x4[63:43]} ^ {x4[58:0],x4[63:59]} ^ {x4[39:0],x4[63:40]};
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
