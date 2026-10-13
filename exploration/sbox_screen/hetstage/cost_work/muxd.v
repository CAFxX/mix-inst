module muxd (input  [63:0] x, output [63:0] y);
  wire [63:0] m = ({x[58:0], x[63:59]} & {x[46:0], x[63:47]}) | (~{x[58:0], x[63:59]} & {x[30:0], x[63:31]});
  assign y = x ^ m ^ {x[22:0], x[63:23]};
endmodule
