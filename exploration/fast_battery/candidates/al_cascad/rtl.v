// al_cascad: 8-stage cascaded AND-rotation (no S-box).
// Stage: x ^= (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)
module al_cascad(
    input [63:0] v,
    input [63:0] k,
    output [63:0] o
);
    wire [63:0] x0 = v ^ k;
    // Stage 0: (1,8,2)
    wire [63:0] s0a = {x0[62:0], x0[63]};
    wire [63:0] s0b = {x0[55:0], x0[63:56]};
    wire [63:0] s0c = {x0[61:0], x0[63:62]};
    wire [63:0] x1 = x0 ^ (s0a & s0b) ^ s0c;
    // Stage 1: (3,11,5)
    wire [63:0] s1a = {x1[60:0], x1[63:61]};
    wire [63:0] s1b = {x1[52:0], x1[63:53]};
    wire [63:0] s1c = {x1[58:0], x1[63:59]};
    wire [63:0] x2 = x1 ^ (s1a & s1b) ^ s1c;
    // Stage 2: (7,19,13)
    wire [63:0] s2a = {x2[56:0], x2[63:57]};
    wire [63:0] s2b = {x2[44:0], x2[63:45]};
    wire [63:0] s2c = {x2[50:0], x2[63:51]};
    wire [63:0] x3 = x2 ^ (s2a & s2b) ^ s2c;
    // Stage 3: (2,9,4)
    wire [63:0] s3a = {x3[61:0], x3[63:62]};
    wire [63:0] s3b = {x3[54:0], x3[63:55]};
    wire [63:0] s3c = {x3[59:0], x3[63:60]};
    wire [63:0] x4 = x3 ^ (s3a & s3b) ^ s3c;
    // Stage 4: (5,17,11)
    wire [63:0] s4a = {x4[58:0], x4[63:59]};
    wire [63:0] s4b = {x4[46:0], x4[63:47]};
    wire [63:0] s4c = {x4[52:0], x4[63:53]};
    wire [63:0] x5 = x4 ^ (s4a & s4b) ^ s4c;
    // Stage 5: (13,29,7)
    wire [63:0] s5a = {x5[50:0], x5[63:51]};
    wire [63:0] s5b = {x5[34:0], x5[63:35]};
    wire [63:0] s5c = {x5[56:0], x5[63:57]};
    wire [63:0] x6 = x5 ^ (s5a & s5b) ^ s5c;
    // Stage 6: (11,23,17)
    wire [63:0] s6a = {x6[52:0], x6[63:53]};
    wire [63:0] s6b = {x6[40:0], x6[63:41]};
    wire [63:0] s6c = {x6[46:0], x6[63:47]};
    wire [63:0] x7 = x6 ^ (s6a & s6b) ^ s6c;
    // Stage 7: (19,37,23)
    wire [63:0] s7a = {x7[44:0], x7[63:45]};
    wire [63:0] s7b = {x7[26:0], x7[63:27]};
    wire [63:0] s7c = {x7[40:0], x7[63:41]};
    wire [63:0] x8 = x7 ^ (s7a & s7b) ^ s7c;
    // Final key mix
    wire [63:0] kr = {k[50:0], k[63:51]};
    assign o = x8 ^ kr;
endmodule
