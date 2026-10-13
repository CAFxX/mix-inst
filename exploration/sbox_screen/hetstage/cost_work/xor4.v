module xor4 (input  [63:0] x, output [63:0] y);
  assign y = x ^ {x[58:0], x[63:59]} ^ {x[46:0], x[63:47]} ^ {x[30:0], x[63:31]} ^ {x[22:0], x[63:23]};
endmodule
