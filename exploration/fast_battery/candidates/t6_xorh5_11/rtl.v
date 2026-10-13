// t6_xorh5_11: xorh5 hetero schedule (fisher triage z=3.00 n_reject=0)
module t6_xorh5_11(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1 = x0 ^ {x0[46:0],x0[63:47]} ^ {x0[28:0],x0[63:29]} ^ {x0[26:0],x0[63:27]} ^ {x0[34:0],x0[63:35]};
    wire [63:0] x2_s = {x1[24:0],x1[63:25]};
    wire [63:0] x2_a = {x1[0:0],x1[63:1]};
    wire [63:0] x2_b = {x1[51:0],x1[63:52]};
    wire [63:0] x2_d = {x1[2:0],x1[63:3]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[13:0],x2[63:14]};
    wire [63:0] x3_a = {x2[15:0],x2[63:16]};
    wire [63:0] x3_b = {x2[58:0],x2[63:59]};
    wire [63:0] x3_d = {x2[45:0],x2[63:46]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[30:0],x3[63:31]};
    wire [63:0] x4_a = {x3[8:0],x3[63:9]};
    wire [63:0] x4_b = {x3[62:0],x3[63:63]};
    wire [63:0] x4_d = {x3[58:0],x3[63:59]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[53:0],x4[63:54]};
    wire [63:0] x5_a = {x4[30:0],x4[63:31]};
    wire [63:0] x5_b = {x4[56:0],x4[63:57]};
    wire [63:0] x5_d = {x4[35:0],x4[63:36]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
