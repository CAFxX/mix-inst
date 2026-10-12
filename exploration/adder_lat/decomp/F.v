// F: combined decomp design (Task 3). f_i = l_i ^ n_i.
// L: weight-5 circulant (14,27,40,52), 5.5u, D6=30, branch 6.
// N: bent AND-XOR, offsets [6,14,23,30,37,44,52,62], 4.6u.
// Total: max(5.5,4.6)+1.8 = 7.3u (under 10u and 8u).
module F (
  input  wire [63:0] x,
  output wire [63:0] y
);
  wire [63:0] l_out;
  wire [63:0] n_out;

  L l_inst (.x(x), .y(l_out));
  N n_inst (.x(x), .n(n_out));

  assign y = l_out ^ n_out;
endmodule
