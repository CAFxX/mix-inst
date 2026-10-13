module t6_hyb5f(input [63:0] val, input [63:0] key, output [63:0] out);
  wire [63:0] st0 = val ^ key;
  wire [63:0] rk0 = ({key[50:0], key[63:51]} ^ 64'h9e3779b97f4a7c15);
  wire [63:0] rk1 = ({key[37:0], key[63:38]} ^ 64'h3c6ef372fe94f82a);
  wire [63:0] rk2 = ({key[24:0], key[63:25]} ^ 64'hdaa66d2c7ddf743f);
  wire [63:0] rk3 = ({key[11:0], key[63:12]} ^ 64'h78dde6e5fd29f054);
  wire [63:0] rk4 = ({key[62:0], key[63:63]} ^ 64'h2545f4914f6cdd1d);
  function [3:0] sb0(input [3:0] n);
    begin
      case (n)
      4'h0: sb0 = 4'hc; 4'h1: sb0 = 4'ha; 4'h2: sb0 = 4'hd; 4'h3: sb0 = 4'h3;
      4'h4: sb0 = 4'he; 4'h5: sb0 = 4'hb; 4'h6: sb0 = 4'hf; 4'h7: sb0 = 4'h7;
      4'h8: sb0 = 4'h8; 4'h9: sb0 = 4'h9; 4'ha: sb0 = 4'h1; 4'hb: sb0 = 4'h5;
      4'hc: sb0 = 4'h0; 4'hd: sb0 = 4'h2; 4'he: sb0 = 4'h4; 4'hf: sb0 = 4'h6;
      endcase
    end
  endfunction
  wire [63:0] kx0 = st0 ^ rk0;
  wire [63:0] sx0;
  genvar g0;
  generate for (g0=0; g0<16; g0=g0+1) begin : sbl0
    assign sx0[4*g0+3:4*g0] = sb0(kx0[4*g0+3:4*g0]);
  end endgenerate
  wire [63:0] px0;
  assign px0[0] = sx0[0]; assign px0[16] = sx0[1]; assign px0[32] = sx0[2]; assign px0[48] = sx0[3]; assign px0[1] = sx0[4]; assign px0[17] = sx0[5]; assign px0[33] = sx0[6]; assign px0[49] = sx0[7]; assign px0[2] = sx0[8]; assign px0[18] = sx0[9]; assign px0[34] = sx0[10]; assign px0[50] = sx0[11]; assign px0[3] = sx0[12]; assign px0[19] = sx0[13]; assign px0[35] = sx0[14]; assign px0[51] = sx0[15]; assign px0[4] = sx0[16]; assign px0[20] = sx0[17]; assign px0[36] = sx0[18]; assign px0[52] = sx0[19]; assign px0[5] = sx0[20]; assign px0[21] = sx0[21]; assign px0[37] = sx0[22]; assign px0[53] = sx0[23]; assign px0[6] = sx0[24]; assign px0[22] = sx0[25]; assign px0[38] = sx0[26]; assign px0[54] = sx0[27]; assign px0[7] = sx0[28]; assign px0[23] = sx0[29]; assign px0[39] = sx0[30]; assign px0[55] = sx0[31]; assign px0[8] = sx0[32]; assign px0[24] = sx0[33]; assign px0[40] = sx0[34]; assign px0[56] = sx0[35]; assign px0[9] = sx0[36]; assign px0[25] = sx0[37]; assign px0[41] = sx0[38]; assign px0[57] = sx0[39]; assign px0[10] = sx0[40]; assign px0[26] = sx0[41]; assign px0[42] = sx0[42]; assign px0[58] = sx0[43]; assign px0[11] = sx0[44]; assign px0[27] = sx0[45]; assign px0[43] = sx0[46]; assign px0[59] = sx0[47]; assign px0[12] = sx0[48]; assign px0[28] = sx0[49]; assign px0[44] = sx0[50]; assign px0[60] = sx0[51]; assign px0[13] = sx0[52]; assign px0[29] = sx0[53]; assign px0[45] = sx0[54]; assign px0[61] = sx0[55]; assign px0[14] = sx0[56]; assign px0[30] = sx0[57]; assign px0[46] = sx0[58]; assign px0[62] = sx0[59]; assign px0[15] = sx0[60]; assign px0[31] = sx0[61]; assign px0[47] = sx0[62]; assign px0[63] = sx0[63];
  wire [63:0] st1 = px0;
  wire [63:0] st2 = st1 ^ (({st1[60:0], st1[63:61]} & {st1[52:0], st1[63:53]}) ^ {st1[40:0], st1[63:41]}) ^ rk1;
  wire [63:0] st3 = st2 ^ (({st2[46:0], st2[63:47]} & {st2[34:0], st2[63:35]}) ^ {st2[22:0], st2[63:23]}) ^ rk2;
  wire [63:0] st4 = st3 ^ (({st3[56:0], st3[63:57]} & {st3[32:0], st3[63:33]}) ^ {st3[16:0], st3[63:17]}) ^ rk3;
  wire [63:0] st5 = st4 ^ (({st4[40:0], st4[63:41]} & {st4[20:0], st4[63:21]}) ^ {st4[4:0], st4[63:5]}) ^ rk4;
  wire [63:0] key_r13 = {key[50:0], key[63:51]};
  assign out = st5 ^ {32'h0, key_r13[63:32]};
endmodule
