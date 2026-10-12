// hyb10_xorand_6: 6-stage XOR-AND: x ^= ra ^ (rb & rc) (parallel structure)
module hyb10_xorand_6(
    input [63:0] val,
    input [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] s0a = {x0[62:0], x0[63:63]};
    wire [63:0] s0b = {x0[61:0], x0[63:62]};
    wire [63:0] s0c = {x0[50:0], x0[63:51]};
    wire [63:0] t0 = x0 ^ s0a ^ (s0b & s0c);
    wire [63:0] s1a = {t0[56:0], t0[63:57]};
    wire [63:0] s1b = {t0[44:0], t0[63:45]};
    wire [63:0] s1c = {t0[58:0], t0[63:59]};
    wire [63:0] t1 = t0 ^ s1a ^ (s1b & s1c);
    wire [63:0] s2a = {t1[60:0], t1[63:61]};
    wire [63:0] s2b = {t1[52:0], t1[63:53]};
    wire [63:0] s2c = {t1[34:0], t1[63:35]};
    wire [63:0] t2 = t1 ^ s2a ^ (s2b & s2c);
    wire [63:0] s3a = {t2[46:0], t2[63:47]};
    wire [63:0] s3b = {t2[32:0], t2[63:33]};
    wire [63:0] s3c = {t2[56:0], t2[63:57]};
    wire [63:0] t3 = t2 ^ s3a ^ (s3b & s3c);
    wire [63:0] s4a = {t3[52:0], t3[63:53]};
    wire [63:0] s4b = {t3[40:0], t3[63:41]};
    wire [63:0] s4c = {t3[26:0], t3[63:27]};
    wire [63:0] t4 = t3 ^ s4a ^ (s4b & s4c);
    wire [63:0] s5a = {t4[44:0], t4[63:45]};
    wire [63:0] s5b = {t4[22:0], t4[63:23]};
    wire [63:0] s5c = {t4[40:0], t4[63:41]};
    wire [63:0] t5 = t4 ^ s5a ^ (s5b & s5c);
    wire [63:0] kr = {key[50:0], key[63:51]};
    assign out = t5 ^ kr;
endmodule
