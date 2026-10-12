// fz_chif_5: 5-stage fused chi: x ^= chi(x,ra,rb)^chi(rc,rd,re)^chi(rf,rg,rh) (gen_fused9.py)
module fz_chif_5(
    input [63:0] v,
    input [63:0] k,
    output [63:0] o
);
    wire [63:0] x0 = v ^ k;
    wire [63:0] s0a = {x0[60:0],x0[63:61]};
    wire [63:0] s0b = {x0[52:0],x0[63:53]};
    wire [63:0] s0c = {x0[40:0],x0[63:41]};
    wire [63:0] s0d = {x0[32:0],x0[63:33]};
    wire [63:0] s0e = {x0[20:0],x0[63:21]};
    wire [63:0] s0f = {x0[10:0],x0[63:11]};
    wire [63:0] t0a = x0 ^ ((~s0a)&s0b);
    wire [63:0] t0b = s0c ^ ((~s0d)&s0e);
    wire [63:0] t0c = s0f ^ ((~s0a)&s0c);
    wire [63:0] x1 = x0 ^ t0a ^ t0b ^ t0c;
    wire [63:0] s1a = {x1[56:0],x1[63:57]};
    wire [63:0] s1b = {x1[46:0],x1[63:47]};
    wire [63:0] s1c = {x1[34:0],x1[63:35]};
    wire [63:0] s1d = {x1[26:0],x1[63:27]};
    wire [63:0] s1e = {x1[16:0],x1[63:17]};
    wire [63:0] s1f = {x1[4:0],x1[63:5]};
    wire [63:0] t1a = x1 ^ ((~s1a)&s1b);
    wire [63:0] t1b = s1c ^ ((~s1d)&s1e);
    wire [63:0] t1c = s1f ^ ((~s1a)&s1c);
    wire [63:0] x2 = x1 ^ t1a ^ t1b ^ t1c;
    wire [63:0] s2a = {x2[58:0],x2[63:59]};
    wire [63:0] s2b = {x2[50:0],x2[63:51]};
    wire [63:0] s2c = {x2[36:0],x2[63:37]};
    wire [63:0] s2d = {x2[22:0],x2[63:23]};
    wire [63:0] s2e = {x2[14:0],x2[63:15]};
    wire [63:0] s2f = {x2[2:0],x2[63:3]};
    wire [63:0] t2a = x2 ^ ((~s2a)&s2b);
    wire [63:0] t2b = s2c ^ ((~s2d)&s2e);
    wire [63:0] t2c = s2f ^ ((~s2a)&s2c);
    wire [63:0] x3 = x2 ^ t2a ^ t2b ^ t2c;
    wire [63:0] s3a = {x3[54:0],x3[63:55]};
    wire [63:0] s3b = {x3[44:0],x3[63:45]};
    wire [63:0] s3c = {x3[30:0],x3[63:31]};
    wire [63:0] s3d = {x3[24:0],x3[63:25]};
    wire [63:0] s3e = {x3[12:0],x3[63:13]};
    wire [63:0] s3f = {x3[6:0],x3[63:7]};
    wire [63:0] t3a = x3 ^ ((~s3a)&s3b);
    wire [63:0] t3b = s3c ^ ((~s3d)&s3e);
    wire [63:0] t3c = s3f ^ ((~s3a)&s3c);
    wire [63:0] x4 = x3 ^ t3a ^ t3b ^ t3c;
    wire [63:0] s4a = {x4[52:0],x4[63:53]};
    wire [63:0] s4b = {x4[40:0],x4[63:41]};
    wire [63:0] s4c = {x4[28:0],x4[63:29]};
    wire [63:0] s4d = {x4[18:0],x4[63:19]};
    wire [63:0] s4e = {x4[8:0],x4[63:9]};
    wire [63:0] s4f = {x4[0:0],x4[63:1]};
    wire [63:0] t4a = x4 ^ ((~s4a)&s4b);
    wire [63:0] t4b = s4c ^ ((~s4d)&s4e);
    wire [63:0] t4c = s4f ^ ((~s4a)&s4c);
    wire [63:0] x5 = x4 ^ t4a ^ t4b ^ t4c;
    wire [63:0] kr = {k[50:0],k[63:51]};
    assign o = x5 ^ kr;
endmodule
