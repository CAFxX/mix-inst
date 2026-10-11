// Batch B candidate B2: add2r_b
// x = val ^ key
// 2 rounds: t = x + rk[i]; x = t ^ ROTL64(t,29) ^ ROTL64(t,53)
// out = x ^ rk[2]; rk[i] = ROTL64(key, 23*(i+1) mod 64) ^ RC[i]
// RC = 0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F
module add2r_b(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
  wire [63:0] rk0 = {key[40:0], key[63:41]} ^ 64'h9E3779B97F4A7C15; // ROTL64(key,23)^RC0
  wire [63:0] rk1 = {key[17:0], key[63:18]} ^ 64'h3C6EF372FE94F82A; // ROTL64(key,46)^RC1
  wire [63:0] rk2 = {key[58:0], key[63:59]} ^ 64'hDAA66D2C7DDF743F; // ROTL64(key,5)^RC2
  wire [63:0] t0 = (val ^ key) + rk0;
  wire [63:0] x1 = t0 ^ {t0[34:0], t0[63:35]} ^ {t0[10:0], t0[63:11]}; // t^rotl29(t)^rotl53(t)
  wire [63:0] t1 = x1 + rk1;
  wire [63:0] x2 = t1 ^ {t1[34:0], t1[63:35]} ^ {t1[10:0], t1[63:11]};
  assign out = x2 ^ rk2;
endmodule
