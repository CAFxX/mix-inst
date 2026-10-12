// hyb9_maj3_6: 6-stage MAJ3 cascade: x ^= maj(ra,rb,rc)^rd
module hyb9_maj3_6(
    input [63:0] val,
    input [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] s0a = {x0[62:0], x0[63:63]};
    wire [63:0] s0b = {x0[61:0], x0[63:62]};
    wire [63:0] s0c = {x0[50:0], x0[63:51]};
    wire [63:0] s0d = {x0[22:0], x0[63:23]};
    wire [63:0] m0 = (s0a & s0b) | (s0b & s0c) | (s0a & s0c);
    wire [63:0] t0 = x0 ^ m0 ^ s0d;
    wire [63:0] s1a = {t0[56:0], t0[63:57]};
    wire [63:0] s1b = {t0[44:0], t0[63:45]};
    wire [63:0] s1c = {t0[58:0], t0[63:59]};
    wire [63:0] s1d = {t0[26:0], t0[63:27]};
    wire [63:0] m1 = (s1a & s1b) | (s1b & s1c) | (s1a & s1c);
    wire [63:0] t1 = t0 ^ m1 ^ s1d;
    wire [63:0] s2a = {t1[60:0], t1[63:61]};
    wire [63:0] s2b = {t1[52:0], t1[63:53]};
    wire [63:0] s2c = {t1[34:0], t1[63:35]};
    wire [63:0] s2d = {t1[16:0], t1[63:17]};
    wire [63:0] m2 = (s2a & s2b) | (s2b & s2c) | (s2a & s2c);
    wire [63:0] t2 = t1 ^ m2 ^ s2d;
    wire [63:0] s3a = {t2[46:0], t2[63:47]};
    wire [63:0] s3b = {t2[32:0], t2[63:33]};
    wire [63:0] s3c = {t2[56:0], t2[63:57]};
    wire [63:0] s3d = {t2[20:0], t2[63:21]};
    wire [63:0] m3 = (s3a & s3b) | (s3b & s3c) | (s3a & s3c);
    wire [63:0] t3 = t2 ^ m3 ^ s3d;
    wire [63:0] s4a = {t3[52:0], t3[63:53]};
    wire [63:0] s4b = {t3[40:0], t3[63:41]};
    wire [63:0] s4c = {t3[26:0], t3[63:27]};
    wire [63:0] s4d = {t3[58:0], t3[63:59]};
    wire [63:0] m4 = (s4a & s4b) | (s4b & s4c) | (s4a & s4c);
    wire [63:0] t4 = t3 ^ m4 ^ s4d;
    wire [63:0] s5a = {t4[44:0], t4[63:45]};
    wire [63:0] s5b = {t4[22:0], t4[63:23]};
    wire [63:0] s5c = {t4[40:0], t4[63:41]};
    wire [63:0] s5d = {t4[50:0], t4[63:51]};
    wire [63:0] m5 = (s5a & s5b) | (s5b & s5c) | (s5a & s5c);
    wire [63:0] t5 = t4 ^ m5 ^ s5d;
    wire [63:0] kr = {key[50:0], key[63:51]};
    assign out = t5 ^ kr;
endmodule
