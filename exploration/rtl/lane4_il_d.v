// Round-2 lane4_il_d: bit-interleaved 4x16-bit lanes (D3 dead-lane fix).
// x = val ^ key; INTERLEAVE bit i of x -> bit (i%4)*16+(i/4) of y.
// Lane consts 16'h8517, 16'hCC6D, 16'h4E35, 16'hB729 (all odd => bijective 16-bit mults),
// followed by bijective downmix w^=w>>8; w^=w>>4 (high->low avalanche).
// Feistel cross rounds: pairs (L0,L1) rot(5,13)+ADD; pairs (L2,L3) rot(5,13)+ADD; pairs (L1,L2) rot(9,21)+ADD; pairs (L3,L0) rot(9,21)+ADD (sequential half-steps).
// out = DEINTERLEAVE(w) ^ ROTL64(key,7).
module lane4_il_d(
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

    wire [15:0] m0 = y[15:0]  * 16'h8517;
    wire [15:0] m1 = y[31:16] * 16'hCC6D;
    wire [15:0] m2 = y[47:32] * 16'h4E35;
    wire [15:0] m3 = y[63:48] * 16'hB729;

    // bijective downmix: e = ((m ^ (m>>8)) ^ ((m ^ (m>>8))>>4))  (~+2 delays)
    wire [15:0] d0 = m0 ^ (m0 >> 8);  wire [15:0] e0 = d0 ^ (d0 >> 4);
    wire [15:0] d1 = m1 ^ (m1 >> 8);  wire [15:0] e1 = d1 ^ (d1 >> 4);
    wire [15:0] d2 = m2 ^ (m2 >> 8);  wire [15:0] e2 = d2 ^ (d2 >> 4);
    wire [15:0] d3 = m3 ^ (m3 >> 8);  wire [15:0] e3 = d3 ^ (d3 >> 4);

    // Feistel cross rounds (sequential half-steps)
    wire [15:0] t_L0L1_513 = e0 ^ {e1[10:0], e1[15:11]};  // ROTL16(e1,5)
    wire [15:0] n_L1_513 = e1 + {t_L0L1_513[2:0], t_L0L1_513[15:3]};  // e1 + ROTL16(t_L0L1_513,13) mod 2^16
    wire [15:0] n_L0_513 = t_L0L1_513;
    wire [15:0] t_L2L3_513 = e2 ^ {e3[10:0], e3[15:11]};  // ROTL16(e3,5)
    wire [15:0] n_L3_513 = e3 + {t_L2L3_513[2:0], t_L2L3_513[15:3]};  // e3 + ROTL16(t_L2L3_513,13) mod 2^16
    wire [15:0] n_L2_513 = t_L2L3_513;
    wire [15:0] t_L1L2_921 = n_L1_513 ^ {n_L2_513[6:0], n_L2_513[15:7]};  // ROTL16(n_L2_513,9)
    wire [15:0] n_L2_921 = n_L2_513 + {t_L1L2_921[10:0], t_L1L2_921[15:11]};  // n_L2_513 + ROTL16(t_L1L2_921,21) mod 2^16
    wire [15:0] n_L1_921 = t_L1L2_921;
    wire [15:0] t_L3L0_921 = n_L3_513 ^ {n_L0_513[6:0], n_L0_513[15:7]};  // ROTL16(n_L0_513,9)
    wire [15:0] n_L0_921 = n_L0_513 + {t_L3L0_921[10:0], t_L3L0_921[15:11]};  // n_L0_513 + ROTL16(t_L3L0_921,21) mod 2^16
    wire [15:0] n_L3_921 = t_L3L0_921;
    wire [63:0] w;
    assign w = {n_L3_921, n_L2_921, n_L1_921, n_L0_921};

    // deinterleave (inverse bit permutation, free wiring)
    wire [63:0] z;
    generate
        for (i = 0; i < 64; i = i + 1)
            assign z[i] = w[((i % 4) * 16) + (i / 4)];
    endgenerate

    assign out = z ^ {key[56:0], key[63:57]};  // ROTL64(key,7)
endmodule
