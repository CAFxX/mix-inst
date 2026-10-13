module t6_dual4a(input [63:0] val, input [63:0] key, output [63:0] out);
  wire [63:0] st0 = val ^ key;
  wire [63:0] rk0 = ({key[50:0], key[63:51]} ^ 64'h9e3779b97f4a7c15);
  wire [63:0] rk1 = ({key[37:0], key[63:38]} ^ 64'h3c6ef372fe94f82a);
  wire [63:0] rk2 = ({key[24:0], key[63:25]} ^ 64'hdaa66d2c7ddf743f);
  wire [63:0] rk3 = ({key[11:0], key[63:12]} ^ 64'h78dde6e5fd29f054);
  wire [63:0] st1 = st0 ^ ({st0[62:0], st0[63:63]} & {st0[61:0], st0[63:62]}) ^ ({st0[54:0], st0[63:55]} & {st0[53:0], st0[63:54]}) ^ rk0;
  wire [63:0] st2 = st1 ^ ({st1[50:0], st1[63:51]} & {st1[49:0], st1[63:50]}) ^ ({st1[42:0], st1[63:43]} & {st1[41:0], st1[63:42]}) ^ rk1;
  wire [63:0] st3 = st2 ^ ({st2[58:0], st2[63:59]} & {st2[57:0], st2[63:58]}) ^ ({st2[34:0], st2[63:35]} & {st2[33:0], st2[63:34]}) ^ rk2;
  wire [63:0] st4 = st3 ^ ({st3[46:0], st3[63:47]} & {st3[45:0], st3[63:46]}) ^ ({st3[26:0], st3[63:27]} & {st3[25:0], st3[63:26]}) ^ rk3;
  assign out = st4 ^ {key[50:0], key[63:51]};
endmodule
