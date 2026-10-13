// t6_xorh5_3: xorh5 hetero schedule (fisher triage z=2.60 n_reject=0)
module t6_xorh5_3(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[11:0],x0[63:12]};
    wire [63:0] x1_a = {x0[8:0],x0[63:9]};
    wire [63:0] x1_b = {x0[19:0],x0[63:20]};
    wire [63:0] x1_d = {x0[28:0],x0[63:29]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[50:0],x1[63:51]};
    wire [63:0] x2_a = {x1[19:0],x1[63:20]};
    wire [63:0] x2_b = {x1[2:0],x1[63:3]};
    wire [63:0] x2_d = {x1[59:0],x1[63:60]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[5:0],x2[63:6]};
    wire [63:0] x3_a = {x2[22:0],x2[63:23]};
    wire [63:0] x3_b = {x2[46:0],x2[63:47]};
    wire [63:0] x3_d = {x2[21:0],x2[63:22]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[36:0],x3[63:37]};
    wire [63:0] x4_a = {x3[62:0],x3[63:63]};
    wire [63:0] x4_b = {x3[20:0],x3[63:21]};
    wire [63:0] x4_d = {x3[2:0],x3[63:3]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5 = x4 ^ {x4[2:0],x4[63:3]} ^ {x4[19:0],x4[63:20]} ^ {x4[28:0],x4[63:29]} ^ {x4[8:0],x4[63:9]};
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
