module circ2 (input  [63:0] x, output [63:0] y);
  assign y = x ^ {x[50:0], x[63:51]} ^ {x[26:0], x[63:27]};
endmodule
