module t6_andchi5a(input [63:0] val, input [63:0] key, output [63:0] out);
  wire [63:0] st0 = val ^ key;
  wire [63:0] rk0 = ({key[50:0], key[63:51]} ^ 64'h9e3779b97f4a7c15);
  wire [63:0] rk1 = ({key[37:0], key[63:38]} ^ 64'h3c6ef372fe94f82a);
  wire [63:0] rk2 = ({key[24:0], key[63:25]} ^ 64'hdaa66d2c7ddf743f);
  wire [63:0] rk3 = ({key[11:0], key[63:12]} ^ 64'h78dde6e5fd29f054);
  wire [63:0] st1 = st0 ^ ({st0[62:0], st0[63:63]} & {st0[61:0], st0[63:62]}) ^ {st0[52:0], st0[63:53]} ^ rk0;
  wire [63:0] st2 = st1 ^ ({st1[56:0], st1[63:57]} & {st1[55:0], st1[63:56]}) ^ {st1[40:0], st1[63:41]} ^ rk1;
  wire [63:0] st3 = st2 ^ ({st2[60:0], st2[63:61]} & {st2[59:0], st2[63:60]}) ^ {st2[26:0], st2[63:27]} ^ rk2;
  wire [63:0] st4 = st3 ^ ({st3[50:0], st3[63:51]} & {st3[49:0], st3[63:50]}) ^ {st3[12:0], st3[63:13]} ^ rk3;
  wire [63:0] rk4 = ({key[62:0], key[63:63]} ^ 64'h2545f4914f6cdd1d);
  wire [63:0] chip = st4;
  wire [63:0] chiq = {st4[52:0], st4[63:53]};
  wire [63:0] chir = {st4[40:0], st4[63:41]};
  wire [63:0] st5 = (chip ^ ((~chiq) & chir)) ^ rk4;
  assign out = st5 ^ {key[50:0], key[63:51]};
endmodule
