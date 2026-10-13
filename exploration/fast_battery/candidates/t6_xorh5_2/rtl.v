// t6_xorh5_2: xorh5 hetero schedule (fisher triage z=2.57 n_reject=0)
module t6_xorh5_2(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[24:0],x0[63:25]};
    wire [63:0] x1_a = {x0[3:0],x0[63:4]};
    wire [63:0] x1_b = {x0[9:0],x0[63:10]};
    wire [63:0] x1_d = {x0[54:0],x0[63:55]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[55:0],x1[63:56]};
    wire [63:0] x2_a = {x1[1:0],x1[63:2]};
    wire [63:0] x2_b = {x1[15:0],x1[63:16]};
    wire [63:0] x2_d = {x1[25:0],x1[63:26]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[34:0],x2[63:35]};
    wire [63:0] x3_a = {x2[44:0],x2[63:45]};
    wire [63:0] x3_b = {x2[30:0],x2[63:31]};
    wire [63:0] x3_d = {x2[34:0],x2[63:35]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[16:0],x3[63:17]};
    wire [63:0] x4_a = {x3[31:0],x3[63:32]};
    wire [63:0] x4_b = {x3[39:0],x3[63:40]};
    wire [63:0] x4_d = {x3[33:0],x3[63:34]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5 = x4 ^ {x4[4:0],x4[63:5]} ^ {x4[7:0],x4[63:8]} ^ {x4[27:0],x4[63:28]} ^ {x4[22:0],x4[63:23]};
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
