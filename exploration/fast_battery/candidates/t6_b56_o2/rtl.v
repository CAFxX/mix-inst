// t6_b56_o2: batch-56 hetMOA5 schedule (fisher triage z=3.06 n_reject=0, andpos=1)
module t6_b56_o2(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[34:0],x0[63:35]};
    wire [63:0] x1_a = {x0[53:0],x0[63:54]};
    wire [63:0] x1_b = {x0[17:0],x0[63:18]};
    wire [63:0] x1_d = {x0[0:0],x0[63:1]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_p = {x1[33:0],x1[63:34]};
    wire [63:0] x2_q = {x1[44:0],x1[63:45]};
    wire [63:0] x2_r = {x1[56:0],x1[63:57]};
    wire [63:0] x2_s = {x1[19:0],x1[63:20]};
    wire [63:0] x2 = x1 ^ (((x2_p | x2_q) & x2_r) ^ x2_s);
    wire [63:0] x3_s = {x2[31:0],x2[63:32]};
    wire [63:0] x3_a = {x2[15:0],x2[63:16]};
    wire [63:0] x3_b = {x2[47:0],x2[63:48]};
    wire [63:0] x3_d = {x2[8:0],x2[63:9]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[7:0],x3[63:8]};
    wire [63:0] x4_a = {x3[51:0],x3[63:52]};
    wire [63:0] x4_b = {x3[10:0],x3[63:11]};
    wire [63:0] x4_d = {x3[53:0],x3[63:54]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[53:0],x4[63:54]};
    wire [63:0] x5_a = {x4[42:0],x4[63:43]};
    wire [63:0] x5_b = {x4[34:0],x4[63:35]};
    wire [63:0] x5_d = {x4[36:0],x4[63:37]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
