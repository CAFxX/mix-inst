module t6_xc4c(input [63:0] val, input [63:0] key, output [63:0] out);
  wire [63:0] st0 = val ^ key;
  wire [63:0] tp0 = 64'h0;
  wire [63:0] rk0 = ({key[50:0], key[63:51]} ^ 64'h9e3779b97f4a7c15);
  wire [63:0] rk1 = ({key[37:0], key[63:38]} ^ 64'h3c6ef372fe94f82a);
  wire [63:0] rk2 = ({key[24:0], key[63:25]} ^ 64'hdaa66d2c7ddf743f);
  wire [63:0] rk3 = ({key[11:0], key[63:12]} ^ 64'h78dde6e5fd29f054);
  wire [63:0] tp1 = ({st0[61:0], st0[63:62]} & {st0[60:0], st0[63:61]});
  wire [63:0] st1 = st0 ^ tp1 ^ {st0[46:0], st0[63:47]} ^ rk0 ^ {tp0[52:0], tp0[63:53]};
  wire [63:0] tp2 = ({st1[54:0], st1[63:55]} & {st1[53:0], st1[63:54]});
  wire [63:0] st2 = st1 ^ tp2 ^ {st1[38:0], st1[63:39]} ^ rk1 ^ {tp1[58:0], tp1[63:59]};
  wire [63:0] tp3 = ({st2[59:0], st2[63:60]} & {st2[57:0], st2[63:58]});
  wire [63:0] st3 = st2 ^ tp3 ^ {st2[22:0], st2[63:23]} ^ rk2 ^ {tp2[46:0], tp2[63:47]};
  wire [63:0] tp4 = ({st3[48:0], st3[63:49]} & {st3[47:0], st3[63:48]});
  wire [63:0] st4 = st3 ^ tp4 ^ {st3[30:0], st3[63:31]} ^ rk3 ^ {tp3[34:0], tp3[63:35]};
  wire [63:0] key_r13 = {key[50:0], key[63:51]};
  assign out = st4 ^ (key_r13 >> 32);
endmodule
