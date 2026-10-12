// fz_muxx_5: 5-stage: x ^= MUX(x,ra,rb)^MUX(rc,rd,re) (gen_fused8.py)
module fz_muxx_5(
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
    wire [63:0] m0a = (x0&s0a)|(~x0&s0b);
    wire [63:0] m0b = (s0c&s0d)|(~s0c&s0e);
    wire [63:0] x1 = x0 ^ m0a ^ m0b;
    wire [63:0] s1a = {x1[56:0],x1[63:57]};
    wire [63:0] s1b = {x1[46:0],x1[63:47]};
    wire [63:0] s1c = {x1[34:0],x1[63:35]};
    wire [63:0] s1d = {x1[26:0],x1[63:27]};
    wire [63:0] s1e = {x1[16:0],x1[63:17]};
    wire [63:0] s1f = {x1[4:0],x1[63:5]};
    wire [63:0] m1a = (x1&s1a)|(~x1&s1b);
    wire [63:0] m1b = (s1c&s1d)|(~s1c&s1e);
    wire [63:0] x2 = x1 ^ m1a ^ m1b;
    wire [63:0] s2a = {x2[58:0],x2[63:59]};
    wire [63:0] s2b = {x2[50:0],x2[63:51]};
    wire [63:0] s2c = {x2[36:0],x2[63:37]};
    wire [63:0] s2d = {x2[22:0],x2[63:23]};
    wire [63:0] s2e = {x2[14:0],x2[63:15]};
    wire [63:0] s2f = {x2[2:0],x2[63:3]};
    wire [63:0] m2a = (x2&s2a)|(~x2&s2b);
    wire [63:0] m2b = (s2c&s2d)|(~s2c&s2e);
    wire [63:0] x3 = x2 ^ m2a ^ m2b;
    wire [63:0] s3a = {x3[54:0],x3[63:55]};
    wire [63:0] s3b = {x3[44:0],x3[63:45]};
    wire [63:0] s3c = {x3[30:0],x3[63:31]};
    wire [63:0] s3d = {x3[24:0],x3[63:25]};
    wire [63:0] s3e = {x3[12:0],x3[63:13]};
    wire [63:0] s3f = {x3[6:0],x3[63:7]};
    wire [63:0] m3a = (x3&s3a)|(~x3&s3b);
    wire [63:0] m3b = (s3c&s3d)|(~s3c&s3e);
    wire [63:0] x4 = x3 ^ m3a ^ m3b;
    wire [63:0] s4a = {x4[52:0],x4[63:53]};
    wire [63:0] s4b = {x4[40:0],x4[63:41]};
    wire [63:0] s4c = {x4[28:0],x4[63:29]};
    wire [63:0] s4d = {x4[18:0],x4[63:19]};
    wire [63:0] s4e = {x4[8:0],x4[63:9]};
    wire [63:0] s4f = {x4[0:0],x4[63:1]};
    wire [63:0] m4a = (x4&s4a)|(~x4&s4b);
    wire [63:0] m4b = (s4c&s4d)|(~s4c&s4e);
    wire [63:0] x5 = x4 ^ m4a ^ m4b;
    wire [63:0] kr = {k[50:0],k[63:51]};
    assign o = x5 ^ kr;
endmodule
