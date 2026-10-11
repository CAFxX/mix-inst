// D1 lane2_s2_const: 2-stage, two 32-bit lanes (delay documentation candidate).
// Per stage: a *= 32'h9E3779B1, b *= 32'h85EBCA77 (parallel const mults);
// Feistel cross: t = a ^ ROTL32(b,11); b ^= ROTL32(t,17); a = t;
// then a ^= RCa[i], b ^= RCb[i] with RCa[i]=(i+1)*0x9E3779B1 mod 2^32,
// RCb[i]=(i+1)*0x85EBCA77 mod 2^32. out = {b, a} after stage 2.
module lane2_s2_const(
    input  wire [63:0] val,
    input  wire [63:0] key,
    output wire [63:0] out
);
    wire [63:0] x = val ^ key;

    // ---- stage 0 ----
    wire [31:0] s0a = x[31:0]  * 32'h9E3779B1;
    wire [31:0] s0b = x[63:32] * 32'h85EBCA77;
    wire [31:0] s0t  = s0a ^ {s0b[20:0], s0b[31:21]};  // ROTL32(b,11)
    wire [31:0] s0b2 = s0b ^ {s0t[14:0], s0t[31:15]};  // ROTL32(t,17)
    wire [31:0] s0ax = s0t  ^ 32'h9E3779B1;           // RCa[0] = 1*0x9E3779B1
    wire [31:0] s0bx = s0b2 ^ 32'h85EBCA77;           // RCb[0] = 1*0x85EBCA77

    // ---- stage 1 ----
    wire [31:0] s1a = s0ax * 32'h9E3779B1;
    wire [31:0] s1b = s0bx * 32'h85EBCA77;
    wire [31:0] s1t  = s1a ^ {s1b[20:0], s1b[31:21]};
    wire [31:0] s1b2 = s1b ^ {s1t[14:0], s1t[31:15]};
    wire [31:0] s1ax = s1t  ^ (32'h9E3779B1 << 1);    // RCa[1] = 2*CA mod 2^32
    wire [31:0] s1bx = s1b2 ^ (32'h85EBCA77 << 1);    // RCb[1] = 2*CB mod 2^32

    assign out = {s1bx, s1ax};
endmodule
