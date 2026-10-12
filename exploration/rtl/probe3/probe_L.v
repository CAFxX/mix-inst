module probe_L(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
  assign out = val ^ {val[52:0], val[63:53]} ^ {val[26:0], val[63:27]};
endmodule
