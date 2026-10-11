// D3 lane4_s1_const: single stage, four 16-bit lanes.
// Lane constants 16'h9E37, 16'h7F4B, 16'h85EB, 16'hC2B9 (all odd; 0x7F4B is the
// brief's 0x7F4A corrected to the nearest odd — 0x7F4A is even, spec bug).
// Whitening mapping: per current lane position a^=9E37, b^=7F4B, c^=85EB, d^=C2B9.
module lane4_s1_const(
    input  wire [63:0] val,
    input  wire [63:0] key,
    output wire [63:0] out
);
    wire [63:0] x = val ^ key;

    wire [15:0] am = x[15:0]  * 16'h9E37;
    wire [15:0] bm = x[31:16] * 16'h7F4B;
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
    wire [15:0] wb = t2 ^ 16'h7F4B;
    wire [15:0] wc = d1 ^ 16'h85EB;
    wire [15:0] wd = t1 ^ 16'hC2B9;

    assign out = {wd, wc, wb, wa};
endmodule
