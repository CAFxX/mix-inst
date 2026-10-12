// N: 64 nonlinear functions n_i = XOR of 4 AND2 terms (decomp Task 2).
// Pattern (offsets rotated across i):
//   n_i = (x[i+6]&x[i+37]) ^ (x[i+14]&x[i+44]) ^ (x[i+23]&x[i+52]) ^ (x[i+30]&x[i+62])
// Depth: 1 AND level + 2 XOR levels (~4.6u). No bijectivity constraint on n_i.
module N (
    input  wire [63:0] x,
    output wire [63:0] n
);
    genvar i;
    generate
        for (i = 0; i < 64; i = i + 1) begin : g
            wire t0 = x[(i+6)%64] & x[(i+37)%64];
            wire t1 = x[(i+14)%64] & x[(i+44)%64];
            wire t2 = x[(i+23)%64] & x[(i+52)%64];
            wire t3 = x[(i+30)%64] & x[(i+62)%64];
            assign n[i] = t0 ^ t1 ^ t2 ^ t3;
        end
    endgenerate
endmodule
