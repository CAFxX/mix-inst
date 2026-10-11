// Round-2 lane4_il_a: bit-interleaved 4x16-bit lanes (D3 dead-lane fix).
// x = val ^ key; INTERLEAVE bit i of x -> bit (i%4)*16+(i/4) of y.
// Lane consts 16'h9E37, 16'h7F4B, 16'h85EB, 16'hC2B9 (all odd => bijective 16-bit mults),
// followed by bijective downmix w^=w>>8; w^=w>>4 (high->low avalanche).
// Feistel cross rounds: pairs (L0,L1) rot(11,17); pairs (L2,L3) rot(11,17) (sequential half-steps).
// out = DEINTERLEAVE(w) ^ ROTL64(key,7).
module lane4_il_a(
    input  wire [63:0] val,
    input  wire [63:0] key,
    output wire [63:0] out
);
    wire [63:0] x = val ^ key;

    // interleave (bit permutation, free wiring)
    wire [63:0] y;
    genvar i;
    generate
        for (i = 0; i < 64; i = i + 1)
            assign y[((i % 4) * 16) + (i / 4)] = x[i];
    endgenerate

    wire [15:0] m0 = y[15:0]  * 16'h9E37;
    wire [15:0] m1 = y[31:16] * 16'h7F4B;
    wire [15:0] m2 = y[47:32] * 16'h85EB;
    wire [15:0] m3 = y[63:48] * 16'hC2B9;

    // bijective downmix: e = ((m ^ (m>>8)) ^ ((m ^ (m>>8))>>4))  (~+2 delays)
    wire [15:0] d0 = m0 ^ (m0 >> 8);  wire [15:0] e0 = d0 ^ (d0 >> 4);
    wire [15:0] d1 = m1 ^ (m1 >> 8);  wire [15:0] e1 = d1 ^ (d1 >> 4);
    wire [15:0] d2 = m2 ^ (m2 >> 8);  wire [15:0] e2 = d2 ^ (d2 >> 4);
    wire [15:0] d3 = m3 ^ (m3 >> 8);  wire [15:0] e3 = d3 ^ (d3 >> 4);

    // Feistel cross rounds (sequential half-steps)
    wire [15:0] t_L0L1_1117 = e0 ^ {e1[4:0], e1[15:5]};  // ROTL16(e1,11)
    wire [15:0] n_L1_1117 = e1 ^ {t_L0L1_1117[14:0], t_L0L1_1117[15:15]};  // ROTL16(t_L0L1_1117,17)
    wire [15:0] n_L0_1117 = t_L0L1_1117;
    wire [15:0] t_L2L3_1117 = e2 ^ {e3[4:0], e3[15:5]};  // ROTL16(e3,11)
    wire [15:0] n_L3_1117 = e3 ^ {t_L2L3_1117[14:0], t_L2L3_1117[15:15]};  // ROTL16(t_L2L3_1117,17)
    wire [15:0] n_L2_1117 = t_L2L3_1117;
    wire [63:0] w;
    assign w = {n_L3_1117, n_L2_1117, n_L1_1117, n_L0_1117};

    // deinterleave (inverse bit permutation, free wiring)
    wire [63:0] z;
    generate
        for (i = 0; i < 64; i = i + 1)
            assign z[i] = w[((i % 4) * 16) + (i / 4)];
    endgenerate

    assign out = z ^ {key[56:0], key[63:57]};  // ROTL64(key,7)
endmodule
