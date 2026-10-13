module circ1 (input  [63:0] x, output [63:0] y);
  assign y = x ^ {x[50:0], x[63:51]};
endmodule
