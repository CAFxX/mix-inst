// L: bijective linear 64->64 diffusion map (decomp track, Task 1).
//
//   l_i = x_i ^ x_{i+A} ^ x_{i+B} ^ x_{i+C} ^ x_{i+D}    (indices mod 64)
//
// Weight-5 circulant. Odd weight => p(1)=1 => gcd(p(t), t^64+1)=1 =>
// invertible over GF(2) (rank 64, verified).
//
// Diffusion: every 6-consecutive-bit input window drives exactly 30 outputs
// (odd-dependency count) -- the theoretical maximum for weight-5, above the
// 24 target. Branch number 6 (max possible for weight-5).
// Cost: 3 XOR2 levels (~6.0u in mini.genlib).
//
// Chosen offsets (A,B,C,D) = (14,27,40,52): exhaustive search over all
// C(63,4)=595665 weight-5 patterns; see DESIGN_L.md.
module L (
  input  wire [63:0] x,
  output wire [63:0] y
);
  parameter A = 14;
  parameter B = 27;
  parameter C = 40;
  parameter D = 52;

  genvar i;
  generate
    for (i = 0; i < 64; i = i + 1) begin : g
      assign y[i] = x[i]
                  ^ x[(i+A)%64]
                  ^ x[(i+B)%64]
                  ^ x[(i+C)%64]
                  ^ x[(i+D)%64];
    end
  endgenerate
endmodule
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
module F_top (
  input  wire [63:0] x,
  output wire [63:0] y
);


endmodule
