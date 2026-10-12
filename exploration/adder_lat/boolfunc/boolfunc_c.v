// boolfunc_c.v -- Design C (track-3 boolfunc): 2-round bit-Feistel, 64-bit.
//
// Split: L = din[63:32], R = din[31:0].
// Round:  (L', R') = (R XOR F(L), L).
//   The F-input half L is passed through untouched, so the round inverts as
//   L = R', R = L' XOR F(L) for ANY F (standard Feistel argument).
//
//   NOTE on the brief: its literal formulas "(L0,R0) -> (R0, R0 XOR F(L0))"
//   are NOT bijective -- F's input L0 never reaches the output (with F=0 the
//   map is (L0,R0) -> (R0,R0), erasing L0; brute-forced collisions at n=8).
//   The brief's prose "L' = L, R' = R XOR F(L), then swap L/R for next round"
//   is the bijective round implemented here: after the swap the state is
//   (R XOR F(L), L).
//
//   Round 1: (L0,R0) -> (R0 XOR F(L0), L0)             = (L1,R1)
//   Round 2: (L1,R1) -> (R1 XOR F(L1), L1)             = (L2,R2)
//   dout = {L2, R2} = { L0 XOR F(R0 XOR F(L0)),  R0 XOR F(L0) }.
//
// F is a 2-level AND-XOR network (need NOT be bijective):
//   F(L)[i] = (L[(i+A)&31] AND L[(i+B)&31]) XOR (L[(i+C)&31] AND L[(i+D)&31])
//
// Cost (mini.genlib): F = AND2(1.5u) + XOR2(2.0u) = 3.5u; the bijective
// 2-round critical path is L2 = L0 XOR F(R0 XOR F(L0)):
//   AND(1.5) + XOR(2.0) + XOR(2.0) + AND(1.5) + XOR(2.0) + XOR(2.0) = 11.0u.
module boolfunc_c #(
  parameter A = 1,
  parameter B = 3,
  parameter C = 5,
  parameter D = 7
)(
  input  wire [63:0] din,
  output wire [63:0] dout
);

  // ---------------------------------------------------------------- F
  // Bit-exact: out[i] = (x[(i+A)%32] & x[(i+B)%32])
  //                    ^ (x[(i+C)%32] & x[(i+D)%32])
  function automatic [31:0] F;
    input [31:0] x;
    integer i;
    begin
      for (i = 0; i < 32; i = i + 1)
        F[i] = (x[(i+A)%32] & x[(i+B)%32])
             ^ (x[(i+C)%32] & x[(i+D)%32]);
    end
  endfunction

  // ---------------------------------------------------------------- rounds
  wire [31:0] L0 = din[63:32];
  wire [31:0] R0 = din[31:0];

  wire [31:0] F0 = F(L0);

  wire [31:0] L1 = R0 ^ F0;   // R XOR F(L); swap folded in
  wire [31:0] R1 = L0;        // F-input half passed through -> invertible

  wire [31:0] F1 = F(L1);

  wire [31:0] L2 = R1 ^ F1;
  wire [31:0] R2 = L1;

  assign dout = {L2, R2};

endmodule
