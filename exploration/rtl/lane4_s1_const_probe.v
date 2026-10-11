// DELAY PROBE ONLY - NOT A CANDIDATE.
// lane4_s1_const as specified in the brief, with the specified (even)
// 16'h7F4A lane constant. This structure is NOT bijective (0x7F4A is even;
// the model's oddness assert fires). Synthesized here solely to measure
// the delay of the 16-bit-lane structure, to inform the fix/no-fix decision.
// Whitening mapping: per current lane position a^=9E37, b^=7F4A, c^=85EB, d^=C2B9.
module lane4_s1_const_probe(
    input  wire [63:0] val,
    input  wire [63:0] key,
    output wire [63:0] out
);
    wire [63:0] x = val ^ key;

    wire [15:0] am = x[15:0]  * 16'h9E37;
    wire [15:0] bm = x[31:16] * 16'h7F4A;  // EVEN: non-bijective (probe only)
    wire [15:0] cm = x[47:32] * 16'h85EB;
    wire [15:0] dm = x[63:48] * 16'hC2B9;

    // Feistel cross on (a,b), rotations (5,9)
    wire [15:0] t1 = am ^ {bm[10:0], bm[15:11]};  // ROTL16(b,5)
    wire [15:0] b1 = bm ^ {t1[6:0],  t1[15:7]};   // ROTL16(t,9)
    // Feistel cross on (c,d), rotations (5,9)
    wire [15:0] t2 = cm ^ {dm[10:0], dm[15:11]};
    wire [15:0] d1 = dm ^ {t2[6:0],  t2[15:7]};

    // lane rotate (a,b,c,d) -> (b,c,d,a): new a=b1, b=t2, c=d1, d=t1
    wire [15:0] wa = b1 ^ 16'h9E37;
    wire [15:0] wb = t2 ^ 16'h7F4A;
    wire [15:0] wc = d1 ^ 16'h85EB;
    wire [15:0] wd = t1 ^ 16'hC2B9;

    assign out = {wd, wc, wb, wa};
endmodule
