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
