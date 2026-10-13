module t6_hyb5e(input [63:0] val, input [63:0] key, output [63:0] out);
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
  wire [63:0] st1 = st0 ^ (({st0[60:0], st0[63:61]} & {st0[52:0], st0[63:53]}) ^ {st0[40:0], st0[63:41]}) ^ rk0;
  wire [63:0] st2 = st1 ^ (({st1[46:0], st1[63:47]} & {st1[34:0], st1[63:35]}) ^ {st1[22:0], st1[63:23]}) ^ rk1;
  wire [63:0] st3 = st2 ^ (({st2[56:0], st2[63:57]} & {st2[32:0], st2[63:33]}) ^ {st2[16:0], st2[63:17]}) ^ rk2;
  wire [63:0] st4 = st3 ^ (({st3[40:0], st3[63:41]} & {st3[20:0], st3[63:21]}) ^ {st3[4:0], st3[63:5]}) ^ rk3;
  wire [63:0] kx4 = st4 ^ rk4;
  wire [63:0] sx4;
  genvar g4;
  generate for (g4=0; g4<16; g4=g4+1) begin : sbl4
    assign sx4[4*g4+3:4*g4] = sb0(kx4[4*g4+3:4*g4]);
  end endgenerate
  wire [63:0] px4;
  assign px4[0] = sx4[0]; assign px4[16] = sx4[1]; assign px4[32] = sx4[2]; assign px4[48] = sx4[3]; assign px4[1] = sx4[4]; assign px4[17] = sx4[5]; assign px4[33] = sx4[6]; assign px4[49] = sx4[7]; assign px4[2] = sx4[8]; assign px4[18] = sx4[9]; assign px4[34] = sx4[10]; assign px4[50] = sx4[11]; assign px4[3] = sx4[12]; assign px4[19] = sx4[13]; assign px4[35] = sx4[14]; assign px4[51] = sx4[15]; assign px4[4] = sx4[16]; assign px4[20] = sx4[17]; assign px4[36] = sx4[18]; assign px4[52] = sx4[19]; assign px4[5] = sx4[20]; assign px4[21] = sx4[21]; assign px4[37] = sx4[22]; assign px4[53] = sx4[23]; assign px4[6] = sx4[24]; assign px4[22] = sx4[25]; assign px4[38] = sx4[26]; assign px4[54] = sx4[27]; assign px4[7] = sx4[28]; assign px4[23] = sx4[29]; assign px4[39] = sx4[30]; assign px4[55] = sx4[31]; assign px4[8] = sx4[32]; assign px4[24] = sx4[33]; assign px4[40] = sx4[34]; assign px4[56] = sx4[35]; assign px4[9] = sx4[36]; assign px4[25] = sx4[37]; assign px4[41] = sx4[38]; assign px4[57] = sx4[39]; assign px4[10] = sx4[40]; assign px4[26] = sx4[41]; assign px4[42] = sx4[42]; assign px4[58] = sx4[43]; assign px4[11] = sx4[44]; assign px4[27] = sx4[45]; assign px4[43] = sx4[46]; assign px4[59] = sx4[47]; assign px4[12] = sx4[48]; assign px4[28] = sx4[49]; assign px4[44] = sx4[50]; assign px4[60] = sx4[51]; assign px4[13] = sx4[52]; assign px4[29] = sx4[53]; assign px4[45] = sx4[54]; assign px4[61] = sx4[55]; assign px4[14] = sx4[56]; assign px4[30] = sx4[57]; assign px4[46] = sx4[58]; assign px4[62] = sx4[59]; assign px4[15] = sx4[60]; assign px4[31] = sx4[61]; assign px4[47] = sx4[62]; assign px4[63] = sx4[63];
  wire [63:0] st5 = px4;
  wire [63:0] key_r13 = {key[50:0], key[63:51]};
  assign out = st5 ^ {32'h0, key_r13[63:32]};
endmodule
