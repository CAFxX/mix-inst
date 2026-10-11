// Round-2 lane2_il_g: bit-interleaved 2x32-bit lanes.
// x = val ^ key; INTERLEAVE2 bit i of x -> bit (i%2)*32+(i/2) of y.
// Lane consts 32'h01010101, 32'h10101011 (both odd => bijective 32-bit mults),
// followed by bijective downmix w^=w>>16; w^=w>>8 (high->low avalanche).
// Feistel cross on (w0,w1), one round rot (11,17) (sequential half-steps).
// out = DEINTERLEAVE2(w) ^ ROTL64(key,7).
module lane2_il_g(
    input  wire [63:0] val,
    input  wire [63:0] key,
    output wire [63:0] out
);
    wire [63:0] x = val ^ key;

    // interleave2 (bit permutation, free wiring)
    wire [63:0] y;
    genvar i;
    generate
        for (i = 0; i < 64; i = i + 1)
            assign y[((i % 2) * 32) + (i / 2)] = x[i];
    endgenerate

    wire [31:0] m0 = y[31:0]  * 32'h01010101;
    wire [31:0] m1 = y[63:32] * 32'h10101011;

    // bijective downmix: d = m ^ (m>>16); e = d ^ (d>>8)
    wire [31:0] d0 = m0 ^ (m0 >> 16);  wire [31:0] e0 = d0 ^ (d0 >> 8);
    wire [31:0] d1 = m1 ^ (m1 >> 16);  wire [31:0] e1 = d1 ^ (d1 >> 8);

    // Feistel cross round 1: (e0,e1) rot (11,17)
    wire [31:0] t01 = e0 ^ {e1[20:0], e1[31:21]};  // ROTL32(e1,11)
    wire [31:0] b01 = e1 ^ {t01[14:0], t01[31:15]};  // ROTL32(t01,17)
    wire [31:0] a01 = t01;
    wire [63:0] w;
    assign w = {b01, a01};

    // deinterleave2 (inverse bit permutation, free wiring)
    wire [63:0] z;
    generate
        for (i = 0; i < 64; i = i + 1)
            assign z[i] = w[((i % 2) * 32) + (i / 2)];
    endgenerate

    assign out = z ^ {key[56:0], key[63:57]};  // ROTL64(key,7)
endmodule
