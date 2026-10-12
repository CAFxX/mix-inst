// hyb20_dm4a: batch-20 fused maj+chi [dm4]: dm(47,26,63,62,7,8) -> dm(63,47,4,59,25,45) -> dm(45,43,18,11,49,62) -> dm(47,11,53,34,10,23) (hill-climbed proxy z=6.6, est=18.80u)
module hyb20_dm4a(
    input [63:0] val,
    input [63:0] key,
    output [63:0] out
);
    wire [63:0] x0 = val ^ key;
    wire [63:0] s0a = {x0[16:0], x0[63:17]};
    wire [63:0] s0b = {x0[37:0], x0[63:38]};
    wire [63:0] s0c = {x0[0:0], x0[63:1]};
    wire [63:0] s0d = {x0[1:0], x0[63:2]};
    wire [63:0] s0e = {x0[56:0], x0[63:57]};
    wire [63:0] s0f = {x0[55:0], x0[63:56]};
    wire [63:0] m10 = (x0 & s0a) | (x0 & s0b) | (s0a & s0b);
    wire [63:0] m20 = (x0 & s0d) | (x0 & s0e) | (s0d & s0e);
    wire [63:0] t0 = x0 ^ m10 ^ s0c ^ m20 ^ s0f;
    wire [63:0] s1a = {t0[0:0], t0[63:1]};
    wire [63:0] s1b = {t0[16:0], t0[63:17]};
    wire [63:0] s1c = {t0[59:0], t0[63:60]};
    wire [63:0] s1d = {t0[4:0], t0[63:5]};
    wire [63:0] s1e = {t0[38:0], t0[63:39]};
    wire [63:0] s1f = {t0[18:0], t0[63:19]};
    wire [63:0] m11 = (t0 & s1a) | (t0 & s1b) | (s1a & s1b);
    wire [63:0] m21 = (t0 & s1d) | (t0 & s1e) | (s1d & s1e);
    wire [63:0] t1 = t0 ^ m11 ^ s1c ^ m21 ^ s1f;
    wire [63:0] s2a = {t1[18:0], t1[63:19]};
    wire [63:0] s2b = {t1[20:0], t1[63:21]};
    wire [63:0] s2c = {t1[45:0], t1[63:46]};
    wire [63:0] s2d = {t1[52:0], t1[63:53]};
    wire [63:0] s2e = {t1[14:0], t1[63:15]};
    wire [63:0] s2f = {t1[1:0], t1[63:2]};
    wire [63:0] m12 = (t1 & s2a) | (t1 & s2b) | (s2a & s2b);
    wire [63:0] m22 = (t1 & s2d) | (t1 & s2e) | (s2d & s2e);
    wire [63:0] t2 = t1 ^ m12 ^ s2c ^ m22 ^ s2f;
    wire [63:0] s3a = {t2[16:0], t2[63:17]};
    wire [63:0] s3b = {t2[52:0], t2[63:53]};
    wire [63:0] s3c = {t2[10:0], t2[63:11]};
    wire [63:0] s3d = {t2[29:0], t2[63:30]};
    wire [63:0] s3e = {t2[53:0], t2[63:54]};
    wire [63:0] s3f = {t2[40:0], t2[63:41]};
    wire [63:0] m13 = (t2 & s3a) | (t2 & s3b) | (s3a & s3b);
    wire [63:0] m23 = (t2 & s3d) | (t2 & s3e) | (s3d & s3e);
    wire [63:0] t3 = t2 ^ m13 ^ s3c ^ m23 ^ s3f;
    assign out = t3;
endmodule
