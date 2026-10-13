module t6_or6a(input [63:0] val, input [63:0] key, output [63:0] out);
  wire [63:0] st0 = val ^ key;
  wire [63:0] rk0 = ({key[50:0], key[63:51]} ^ 64'h9e3779b97f4a7c15);
  wire [63:0] rk1 = ({key[37:0], key[63:38]} ^ 64'h3c6ef372fe94f82a);
  wire [63:0] rk2 = ({key[24:0], key[63:25]} ^ 64'hdaa66d2c7ddf743f);
  wire [63:0] rk3 = ({key[11:0], key[63:12]} ^ 64'h78dde6e5fd29f054);
  wire [63:0] rk4 = ({key[62:0], key[63:63]} ^ 64'h2545f4914f6cdd1d);
  wire [63:0] rk5 = ({key[49:0], key[63:50]} ^ 64'h9e3779b9a1e7c2fa);
  wire [63:0] st1 = st0 ^ ({st0[60:0], st0[63:61]} | {st0[52:0], st0[63:53]}) ^ {st0[40:0], st0[63:41]} ^ rk0;
  wire [63:0] st2 = st1 ^ ({st1[46:0], st1[63:47]} | {st1[34:0], st1[63:35]}) ^ {st1[22:0], st1[63:23]} ^ rk1;
  wire [63:0] st3 = st2 ^ ({st2[56:0], st2[63:57]} | {st2[32:0], st2[63:33]}) ^ {st2[16:0], st2[63:17]} ^ rk2;
  wire [63:0] st4 = st3 ^ ({st3[40:0], st3[63:41]} | {st3[20:0], st3[63:21]}) ^ {st3[4:0], st3[63:5]} ^ rk3;
  wire [63:0] st5 = st4 ^ ({st4[52:0], st4[63:53]} | {st4[26:0], st4[63:27]}) ^ {st4[10:0], st4[63:11]} ^ rk4;
  wire [63:0] st6 = st5 ^ ({st5[58:0], st5[63:59]} | {st5[44:0], st5[63:45]}) ^ {st5[2:0], st5[63:3]} ^ rk5;
  wire [63:0] key_r13 = {key[50:0], key[63:51]};
  assign out = st6 ^ (key_r13 >> 32);
endmodule
