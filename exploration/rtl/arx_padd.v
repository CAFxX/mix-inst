// Delay probe: bare 64-bit add (decompose round cost)
module arx_padd(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
  assign out = val + key;
endmodule
