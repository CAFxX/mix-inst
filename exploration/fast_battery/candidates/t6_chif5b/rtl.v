module t6_chif5b(input [63:0] val, input [63:0] key, output [63:0] out);
  wire [63:0] st0 = val ^ key;
  wire [63:0] st1 = st0 ^ ({st0[60:0], st0[63:61]} & {st0[59:0], st0[63:60]}) ^ {st0[32:0], st0[63:33]};
  wire [63:0] st2 = st1 ^ ({st1[56:0], st1[63:57]} & {st1[55:0], st1[63:56]}) ^ {st1[50:0], st1[63:51]};
  wire [63:0] st3 = st2 ^ ({st2[52:0], st2[63:53]} & {st2[51:0], st2[63:52]}) ^ {st2[26:0], st2[63:27]};
  wire [63:0] st4 = st3 ^ ({st3[48:0], st3[63:49]} & {st3[47:0], st3[63:48]}) ^ {st3[58:0], st3[63:59]};
  wire [63:0] st5 = st4 ^ ({st4[44:0], st4[63:45]} & {st4[43:0], st4[63:44]}) ^ {st4[20:0], st4[63:21]};
  wire [63:0] ch = st5 ^ (~{st5[0], st5[63:1]} & {st5[1], st5[0], st5[63:2]});
  assign out = ch ^ {key[50:0], key[63:51]};
endmodule
