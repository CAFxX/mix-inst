module probe_keyxor(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
  assign out = val ^ {key[50:0], key[63:51]} ^ 64'h9e3779b97f4a7c15;
endmodule
