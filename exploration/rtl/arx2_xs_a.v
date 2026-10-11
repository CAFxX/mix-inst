// Round-2 deeper ARX candidate arx2_xs_a
// x=val; x+=rk0; x^=x>>30; x^=x<<27; x+=rk1; x^=x>>31; out=x^rk2
// rk[i] = ROTL64(key,17*(i+1)) ^ RC[i]
// RC = 0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F
module arx2_xs_a(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
  wire [63:0] rk0 = {key[46:0], key[63:47]} ^ 64'h9E3779B97F4A7C15; // ROTL64(key,17)^RC0
  wire [63:0] rk1 = {key[29:0], key[63:30]} ^ 64'h3C6EF372FE94F82A; // ROTL64(key,34)^RC1
  wire [63:0] rk2 = {key[12:0], key[63:13]} ^ 64'hDAA66D2C7DDF743F; // ROTL64(key,51)^RC2
  wire [63:0] a0 = val + rk0;
  wire [63:0] x1 = a0 ^ (a0 >> 30);
  wire [63:0] x2 = x1 ^ (x1 << 27);
  wire [63:0] a1 = x2 + rk1;
  wire [63:0] x3 = a1 ^ (a1 >> 31);
  assign out = x3 ^ rk2;
endmodule
