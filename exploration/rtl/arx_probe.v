// Delay probe: one full ARX round = add-key + 3 sequential xorshifts
// rk0 = ROTL64(key,17) ^ RC0 (computed in parallel from key, not on crit path)
module arx_probe(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
  wire [63:0] rk0 = {key[46:0], key[63:47]} ^ 64'h9E3779B97F4A7C15;
  wire [63:0] t0 = (val ^ key) + rk0;
  wire [63:0] t1 = t0 ^ (t0 >> 27);
  wire [63:0] t2 = t1 ^ (t1 << 13);
  wire [63:0] t3 = t2 ^ (t2 >> 33);
  assign out = t3;
endmodule
