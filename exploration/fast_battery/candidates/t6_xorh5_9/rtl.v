// t6_xorh5_9: xorh5 hetero schedule (fisher triage z=2.95 n_reject=0)
module t6_xorh5_9(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[10:0],x0[63:11]};
    wire [63:0] x1_a = {x0[2:0],x0[63:3]};
    wire [63:0] x1_b = {x0[4:0],x0[63:5]};
    wire [63:0] x1_d = {x0[9:0],x0[63:10]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[62:0],x1[63:63]};
    wire [63:0] x2_a = {x1[49:0],x1[63:50]};
    wire [63:0] x2_b = {x1[7:0],x1[63:8]};
    wire [63:0] x2_d = {x1[19:0],x1[63:20]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[27:0],x2[63:28]};
    wire [63:0] x3_a = {x2[24:0],x2[63:25]};
    wire [63:0] x3_b = {x2[37:0],x2[63:38]};
    wire [63:0] x3_d = {x2[9:0],x2[63:10]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[18:0],x3[63:19]};
    wire [63:0] x4_a = {x3[15:0],x3[63:16]};
    wire [63:0] x4_b = {x3[8:0],x3[63:9]};
    wire [63:0] x4_d = {x3[5:0],x3[63:6]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5 = x4 ^ {x4[17:0],x4[63:18]} ^ {x4[60:0],x4[63:61]} ^ {x4[43:0],x4[63:44]} ^ {x4[50:0],x4[63:51]};
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
