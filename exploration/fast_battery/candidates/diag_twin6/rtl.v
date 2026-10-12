// diag_twin6: diagnostic: 6-stage twin-AND x^=(ra&rb)^(rc&rd)
module diag_twin6(
    input [63:0] val,
    input [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] s0a = {x0[62:0], x0[63:63]};
    wire [63:0] s0b = {x0[61:0], x0[63:62]};
    wire [63:0] s0c = {x0[56:0], x0[63:57]};
    wire [63:0] s0d = {x0[44:0], x0[63:45]};
    wire [63:0] x1 = x0 ^ (s0a & s0b) ^ (s0c & s0d);
    wire [63:0] s1a = {x1[56:0], x1[63:57]};
    wire [63:0] s1b = {x1[44:0], x1[63:45]};
    wire [63:0] s1c = {x1[60:0], x1[63:61]};
    wire [63:0] s1d = {x1[52:0], x1[63:53]};
    wire [63:0] x2 = x1 ^ (s1a & s1b) ^ (s1c & s1d);
    wire [63:0] s2a = {x2[60:0], x2[63:61]};
    wire [63:0] s2b = {x2[52:0], x2[63:53]};
    wire [63:0] s2c = {x2[46:0], x2[63:47]};
    wire [63:0] s2d = {x2[32:0], x2[63:33]};
    wire [63:0] x3 = x2 ^ (s2a & s2b) ^ (s2c & s2d);
    wire [63:0] s3a = {x3[46:0], x3[63:47]};
    wire [63:0] s3b = {x3[32:0], x3[63:33]};
    wire [63:0] s3c = {x3[52:0], x3[63:53]};
    wire [63:0] s3d = {x3[40:0], x3[63:41]};
    wire [63:0] x4 = x3 ^ (s3a & s3b) ^ (s3c & s3d);
    wire [63:0] s4a = {x4[52:0], x4[63:53]};
    wire [63:0] s4b = {x4[40:0], x4[63:41]};
    wire [63:0] s4c = {x4[44:0], x4[63:45]};
    wire [63:0] s4d = {x4[22:0], x4[63:23]};
    wire [63:0] x5 = x4 ^ (s4a & s4b) ^ (s4c & s4d);
    wire [63:0] s5a = {x5[44:0], x5[63:45]};
    wire [63:0] s5b = {x5[22:0], x5[63:23]};
    wire [63:0] s5c = {x5[62:0], x5[63:63]};
    wire [63:0] s5d = {x5[61:0], x5[63:62]};
    wire [63:0] x6 = x5 ^ (s5a & s5b) ^ (s5c & s5d);
    wire [63:0] kr = {key[50:0], key[63:51]};
    assign out = x6 ^ kr;
endmodule
