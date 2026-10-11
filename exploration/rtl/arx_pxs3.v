// Delay probe: 3 sequential xorshift steps, no add (decompose round cost)
module arx_pxs3(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
  wire [63:0] t1 = val ^ (val >> 27);
  wire [63:0] t2 = t1 ^ (t1 << 13);
  wire [63:0] t3 = t2 ^ (t2 >> 33);
  assign out = t3;
endmodule
