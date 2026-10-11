// Batch B candidate B1: add2r_a
// x = val ^ key
// 2 rounds: t = x + rk[i]; x = t ^ ROTL64(t,13) ^ ROTL64(t,41)
// out = x ^ rk[2]; rk[i] = ROTL64(key, 17*(i+1)) ^ RC[i]
// RC = 0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F
module add2r_a(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
  wire [63:0] rk0 = {key[46:0], key[63:47]} ^ 64'h9E3779B97F4A7C15; // ROTL64(key,17)^RC0
  wire [63:0] rk1 = {key[29:0], key[63:30]} ^ 64'h3C6EF372FE94F82A; // ROTL64(key,34)^RC1
  wire [63:0] rk2 = {key[12:0], key[63:13]} ^ 64'hDAA66D2C7DDF743F; // ROTL64(key,51)^RC2
  wire [63:0] t0 = (val ^ key) + rk0;
  wire [63:0] x1 = t0 ^ {t0[50:0], t0[63:51]} ^ {t0[22:0], t0[63:23]}; // t^rotl13(t)^rotl41(t)
  wire [63:0] t1 = x1 + rk1;
  wire [63:0] x2 = t1 ^ {t1[50:0], t1[63:51]} ^ {t1[22:0], t1[63:23]};
  assign out = x2 ^ rk2;
endmodule
