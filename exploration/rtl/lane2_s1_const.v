// D2 lane2_s1_const: single stage, two 32-bit lanes.
// a *= 32'h9E3779B1; b *= 32'h85EBCA77 (parallel const mults);
// Feistel cross #1: t = a ^ ROTL32(b,11); b ^= ROTL32(t,17); a = t;
// Feistel cross #2: t = a ^ ROTL32(b,7);  b ^= ROTL32(t,19); a = t;
// whitening a ^= 32'h9E3779B1; b ^= 32'h85EBCA77; out = {b, a}.
module lane2_s1_const(
    input  wire [63:0] val,
    input  wire [63:0] key,
    output wire [63:0] out
);
    wire [63:0] x = val ^ key;

    wire [31:0] am = x[31:0]  * 32'h9E3779B1;
    wire [31:0] bm = x[63:32] * 32'h85EBCA77;

    // Feistel cross #1, rotations (11,17)
    wire [31:0] t1 = am ^ {bm[20:0], bm[31:21]};  // ROTL32(b,11)
    wire [31:0] b1 = bm ^ {t1[14:0], t1[31:15]};  // ROTL32(t,17)

    // Feistel cross #2, rotations (7,19)
    wire [31:0] t2 = t1 ^ {b1[24:0], b1[31:25]};  // ROTL32(b,7)
    wire [31:0] b2 = b1 ^ {t2[12:0], t2[31:13]};  // ROTL32(t,19)

    wire [31:0] a2 = t2 ^ 32'h9E3779B1;
    wire [31:0] b3 = b2 ^ 32'h85EBCA77;

    assign out = {b3, a2};
endmodule
