module t6_chif4a(input [63:0] val, input [63:0] key, output [63:0] out);
  wire [63:0] st0 = val ^ key;
  wire [63:0] st1 = st0 ^ ({st0[62:0], st0[63:63]} & {st0[61:0], st0[63:62]}) ^ {st0[56:0], st0[63:57]};
  wire [63:0] st2 = st1 ^ ({st1[58:0], st1[63:59]} & {st1[57:0], st1[63:58]}) ^ {st1[40:0], st1[63:41]};
  wire [63:0] st3 = st2 ^ ({st2[54:0], st2[63:55]} & {st2[53:0], st2[63:54]}) ^ {st2[22:0], st2[63:23]};
  wire [63:0] st4 = st3 ^ ({st3[50:0], st3[63:51]} & {st3[49:0], st3[63:50]}) ^ {st3[34:0], st3[63:35]};
  wire [63:0] ch = st4 ^ (~{st4[0], st4[63:1]} & {st4[1], st4[0], st4[63:2]});
  assign out = ch ^ {key[50:0], key[63:51]};
endmodule
