module t6_xc4a(input [63:0] val, input [63:0] key, output [63:0] out);
  wire [63:0] st0 = val ^ key;
  wire [63:0] tp0 = 64'h0;
  wire [63:0] rk0 = ({key[50:0], key[63:51]} ^ 64'h9e3779b97f4a7c15);
  wire [63:0] rk1 = ({key[37:0], key[63:38]} ^ 64'h3c6ef372fe94f82a);
  wire [63:0] rk2 = ({key[24:0], key[63:25]} ^ 64'hdaa66d2c7ddf743f);
  wire [63:0] rk3 = ({key[11:0], key[63:12]} ^ 64'h78dde6e5fd29f054);
  wire [63:0] tp1 = ({st0[58:0], st0[63:59]} & {st0[46:0], st0[63:47]});
  wire [63:0] st1 = st0 ^ tp1 ^ {st0[34:0], st0[63:35]} ^ rk0 ^ {tp0[56:0], tp0[63:57]};
  wire [63:0] tp2 = ({st1[52:0], st1[63:53]} & {st1[40:0], st1[63:41]});
  wire [63:0] st2 = st1 ^ tp2 ^ {st1[26:0], st1[63:27]} ^ rk1 ^ {tp1[50:0], tp1[63:51]};
  wire [63:0] tp3 = ({st2[60:0], st2[63:61]} & {st2[44:0], st2[63:45]});
  wire [63:0] st3 = st2 ^ tp3 ^ {st2[32:0], st2[63:33]} ^ rk2 ^ {tp2[44:0], tp2[63:45]};
  wire [63:0] tp4 = ({st3[50:0], st3[63:51]} & {st3[36:0], st3[63:37]});
  wire [63:0] st4 = st3 ^ tp4 ^ {st3[24:0], st3[63:25]} ^ rk3 ^ {tp3[40:0], tp3[63:41]};
  wire [63:0] key_r13 = {key[50:0], key[63:51]};
  assign out = st4 ^ (key_r13 >> 32);
endmodule
