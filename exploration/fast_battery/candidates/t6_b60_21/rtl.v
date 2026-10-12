// t6_b60_21: batch-57 muxD5f schedule (fisher triage z=2.89 n_reject=0)
module t6_b60_21(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1_s = {x0[46:0],x0[63:47]};
    wire [63:0] x1_a = {x0[41:0],x0[63:42]};
    wire [63:0] x1_b = {x0[53:0],x0[63:54]};
    wire [63:0] x1_d = {x0[8:0],x0[63:9]};
    wire [63:0] x1_m = (x1_s & x1_a) | (~x1_s & x1_b);
    wire [63:0] x1 = x0 ^ x1_m ^ x1_d;
    wire [63:0] x2_s = {x1[29:0],x1[63:30]};
    wire [63:0] x2_a = {x1[1:0],x1[63:2]};
    wire [63:0] x2_b = {x1[9:0],x1[63:10]};
    wire [63:0] x2_d = {x1[6:0],x1[63:7]};
    wire [63:0] x2_m = (x2_s & x2_a) | (~x2_s & x2_b);
    wire [63:0] x2 = x1 ^ x2_m ^ x2_d;
    wire [63:0] x3_s = {x2[34:0],x2[63:35]};
    wire [63:0] x3_a = {x2[24:0],x2[63:25]};
    wire [63:0] x3_b = {x2[28:0],x2[63:29]};
    wire [63:0] x3_d = {x2[19:0],x2[63:20]};
    wire [63:0] x3_m = (x3_s & x3_a) | (~x3_s & x3_b);
    wire [63:0] x3 = x2 ^ x3_m ^ x3_d;
    wire [63:0] x4_s = {x3[54:0],x3[63:55]};
    wire [63:0] x4_a = {x3[59:0],x3[63:60]};
    wire [63:0] x4_b = {x3[19:0],x3[63:20]};
    wire [63:0] x4_d = {x3[27:0],x3[63:28]};
    wire [63:0] x4_m = (x4_s & x4_a) | (~x4_s & x4_b);
    wire [63:0] x4 = x3 ^ x4_m ^ x4_d;
    wire [63:0] x5_s = {x4[58:0],x4[63:59]};
    wire [63:0] x5_a = {x4[25:0],x4[63:26]};
    wire [63:0] x5_b = {x4[32:0],x4[63:33]};
    wire [63:0] x5_d = {x4[29:0],x4[63:30]};
    wire [63:0] x5_m = (x5_s & x5_a) | (~x5_s & x5_b);
    wire [63:0] x5 = x4 ^ x5_m ^ x5_d;
    wire [63:0] k13 = {key[50:0],key[63:51]};
    assign out = x5 ^ k13;
endmodule
