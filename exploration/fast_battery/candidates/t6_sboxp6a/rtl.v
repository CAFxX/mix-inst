module t6_sboxp6a(input [63:0] val, input [63:0] key, output [63:0] out);
  wire [63:0] st0 = val ^ key;
  wire [63:0] rk0 = ({key[50:0], key[63:51]} ^ 64'h9e3779b97f4a7c15);
  wire [63:0] rk1 = ({key[37:0], key[63:38]} ^ 64'h3c6ef372fe94f82a);
  wire [63:0] rk2 = ({key[24:0], key[63:25]} ^ 64'hdaa66d2c7ddf743f);
  wire [63:0] rk3 = ({key[11:0], key[63:12]} ^ 64'h78dde6e5fd29f054);
  wire [63:0] rk4 = ({key[62:0], key[63:63]} ^ 64'h2545f4914f6cdd1d);
  wire [63:0] rk5 = ({key[49:0], key[63:50]} ^ 64'h9e3779b9a1e7c2fa);
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
  wire [63:0] kx1 = st1 ^ rk1;
  wire [63:0] sx1;
  genvar g1;
  generate for (g1=0; g1<16; g1=g1+1) begin : sbl1
    assign sx1[4*g1+3:4*g1] = sb0(kx1[4*g1+3:4*g1]);
  end endgenerate
  wire [63:0] px1;
  assign px1[0] = sx1[0]; assign px1[16] = sx1[1]; assign px1[32] = sx1[2]; assign px1[48] = sx1[3]; assign px1[1] = sx1[4]; assign px1[17] = sx1[5]; assign px1[33] = sx1[6]; assign px1[49] = sx1[7]; assign px1[2] = sx1[8]; assign px1[18] = sx1[9]; assign px1[34] = sx1[10]; assign px1[50] = sx1[11]; assign px1[3] = sx1[12]; assign px1[19] = sx1[13]; assign px1[35] = sx1[14]; assign px1[51] = sx1[15]; assign px1[4] = sx1[16]; assign px1[20] = sx1[17]; assign px1[36] = sx1[18]; assign px1[52] = sx1[19]; assign px1[5] = sx1[20]; assign px1[21] = sx1[21]; assign px1[37] = sx1[22]; assign px1[53] = sx1[23]; assign px1[6] = sx1[24]; assign px1[22] = sx1[25]; assign px1[38] = sx1[26]; assign px1[54] = sx1[27]; assign px1[7] = sx1[28]; assign px1[23] = sx1[29]; assign px1[39] = sx1[30]; assign px1[55] = sx1[31]; assign px1[8] = sx1[32]; assign px1[24] = sx1[33]; assign px1[40] = sx1[34]; assign px1[56] = sx1[35]; assign px1[9] = sx1[36]; assign px1[25] = sx1[37]; assign px1[41] = sx1[38]; assign px1[57] = sx1[39]; assign px1[10] = sx1[40]; assign px1[26] = sx1[41]; assign px1[42] = sx1[42]; assign px1[58] = sx1[43]; assign px1[11] = sx1[44]; assign px1[27] = sx1[45]; assign px1[43] = sx1[46]; assign px1[59] = sx1[47]; assign px1[12] = sx1[48]; assign px1[28] = sx1[49]; assign px1[44] = sx1[50]; assign px1[60] = sx1[51]; assign px1[13] = sx1[52]; assign px1[29] = sx1[53]; assign px1[45] = sx1[54]; assign px1[61] = sx1[55]; assign px1[14] = sx1[56]; assign px1[30] = sx1[57]; assign px1[46] = sx1[58]; assign px1[62] = sx1[59]; assign px1[15] = sx1[60]; assign px1[31] = sx1[61]; assign px1[47] = sx1[62]; assign px1[63] = sx1[63];
  wire [63:0] st2 = px1;
  wire [63:0] kx2 = st2 ^ rk2;
  wire [63:0] sx2;
  genvar g2;
  generate for (g2=0; g2<16; g2=g2+1) begin : sbl2
    assign sx2[4*g2+3:4*g2] = sb0(kx2[4*g2+3:4*g2]);
  end endgenerate
  wire [63:0] px2;
  assign px2[0] = sx2[0]; assign px2[16] = sx2[1]; assign px2[32] = sx2[2]; assign px2[48] = sx2[3]; assign px2[1] = sx2[4]; assign px2[17] = sx2[5]; assign px2[33] = sx2[6]; assign px2[49] = sx2[7]; assign px2[2] = sx2[8]; assign px2[18] = sx2[9]; assign px2[34] = sx2[10]; assign px2[50] = sx2[11]; assign px2[3] = sx2[12]; assign px2[19] = sx2[13]; assign px2[35] = sx2[14]; assign px2[51] = sx2[15]; assign px2[4] = sx2[16]; assign px2[20] = sx2[17]; assign px2[36] = sx2[18]; assign px2[52] = sx2[19]; assign px2[5] = sx2[20]; assign px2[21] = sx2[21]; assign px2[37] = sx2[22]; assign px2[53] = sx2[23]; assign px2[6] = sx2[24]; assign px2[22] = sx2[25]; assign px2[38] = sx2[26]; assign px2[54] = sx2[27]; assign px2[7] = sx2[28]; assign px2[23] = sx2[29]; assign px2[39] = sx2[30]; assign px2[55] = sx2[31]; assign px2[8] = sx2[32]; assign px2[24] = sx2[33]; assign px2[40] = sx2[34]; assign px2[56] = sx2[35]; assign px2[9] = sx2[36]; assign px2[25] = sx2[37]; assign px2[41] = sx2[38]; assign px2[57] = sx2[39]; assign px2[10] = sx2[40]; assign px2[26] = sx2[41]; assign px2[42] = sx2[42]; assign px2[58] = sx2[43]; assign px2[11] = sx2[44]; assign px2[27] = sx2[45]; assign px2[43] = sx2[46]; assign px2[59] = sx2[47]; assign px2[12] = sx2[48]; assign px2[28] = sx2[49]; assign px2[44] = sx2[50]; assign px2[60] = sx2[51]; assign px2[13] = sx2[52]; assign px2[29] = sx2[53]; assign px2[45] = sx2[54]; assign px2[61] = sx2[55]; assign px2[14] = sx2[56]; assign px2[30] = sx2[57]; assign px2[46] = sx2[58]; assign px2[62] = sx2[59]; assign px2[15] = sx2[60]; assign px2[31] = sx2[61]; assign px2[47] = sx2[62]; assign px2[63] = sx2[63];
  wire [63:0] st3 = px2;
  wire [63:0] kx3 = st3 ^ rk3;
  wire [63:0] sx3;
  genvar g3;
  generate for (g3=0; g3<16; g3=g3+1) begin : sbl3
    assign sx3[4*g3+3:4*g3] = sb0(kx3[4*g3+3:4*g3]);
  end endgenerate
  wire [63:0] px3;
  assign px3[0] = sx3[0]; assign px3[16] = sx3[1]; assign px3[32] = sx3[2]; assign px3[48] = sx3[3]; assign px3[1] = sx3[4]; assign px3[17] = sx3[5]; assign px3[33] = sx3[6]; assign px3[49] = sx3[7]; assign px3[2] = sx3[8]; assign px3[18] = sx3[9]; assign px3[34] = sx3[10]; assign px3[50] = sx3[11]; assign px3[3] = sx3[12]; assign px3[19] = sx3[13]; assign px3[35] = sx3[14]; assign px3[51] = sx3[15]; assign px3[4] = sx3[16]; assign px3[20] = sx3[17]; assign px3[36] = sx3[18]; assign px3[52] = sx3[19]; assign px3[5] = sx3[20]; assign px3[21] = sx3[21]; assign px3[37] = sx3[22]; assign px3[53] = sx3[23]; assign px3[6] = sx3[24]; assign px3[22] = sx3[25]; assign px3[38] = sx3[26]; assign px3[54] = sx3[27]; assign px3[7] = sx3[28]; assign px3[23] = sx3[29]; assign px3[39] = sx3[30]; assign px3[55] = sx3[31]; assign px3[8] = sx3[32]; assign px3[24] = sx3[33]; assign px3[40] = sx3[34]; assign px3[56] = sx3[35]; assign px3[9] = sx3[36]; assign px3[25] = sx3[37]; assign px3[41] = sx3[38]; assign px3[57] = sx3[39]; assign px3[10] = sx3[40]; assign px3[26] = sx3[41]; assign px3[42] = sx3[42]; assign px3[58] = sx3[43]; assign px3[11] = sx3[44]; assign px3[27] = sx3[45]; assign px3[43] = sx3[46]; assign px3[59] = sx3[47]; assign px3[12] = sx3[48]; assign px3[28] = sx3[49]; assign px3[44] = sx3[50]; assign px3[60] = sx3[51]; assign px3[13] = sx3[52]; assign px3[29] = sx3[53]; assign px3[45] = sx3[54]; assign px3[61] = sx3[55]; assign px3[14] = sx3[56]; assign px3[30] = sx3[57]; assign px3[46] = sx3[58]; assign px3[62] = sx3[59]; assign px3[15] = sx3[60]; assign px3[31] = sx3[61]; assign px3[47] = sx3[62]; assign px3[63] = sx3[63];
  wire [63:0] st4 = px3;
  wire [63:0] kx4 = st4 ^ rk4;
  wire [63:0] sx4;
  genvar g4;
  generate for (g4=0; g4<16; g4=g4+1) begin : sbl4
    assign sx4[4*g4+3:4*g4] = sb0(kx4[4*g4+3:4*g4]);
  end endgenerate
  wire [63:0] px4;
  assign px4[0] = sx4[0]; assign px4[16] = sx4[1]; assign px4[32] = sx4[2]; assign px4[48] = sx4[3]; assign px4[1] = sx4[4]; assign px4[17] = sx4[5]; assign px4[33] = sx4[6]; assign px4[49] = sx4[7]; assign px4[2] = sx4[8]; assign px4[18] = sx4[9]; assign px4[34] = sx4[10]; assign px4[50] = sx4[11]; assign px4[3] = sx4[12]; assign px4[19] = sx4[13]; assign px4[35] = sx4[14]; assign px4[51] = sx4[15]; assign px4[4] = sx4[16]; assign px4[20] = sx4[17]; assign px4[36] = sx4[18]; assign px4[52] = sx4[19]; assign px4[5] = sx4[20]; assign px4[21] = sx4[21]; assign px4[37] = sx4[22]; assign px4[53] = sx4[23]; assign px4[6] = sx4[24]; assign px4[22] = sx4[25]; assign px4[38] = sx4[26]; assign px4[54] = sx4[27]; assign px4[7] = sx4[28]; assign px4[23] = sx4[29]; assign px4[39] = sx4[30]; assign px4[55] = sx4[31]; assign px4[8] = sx4[32]; assign px4[24] = sx4[33]; assign px4[40] = sx4[34]; assign px4[56] = sx4[35]; assign px4[9] = sx4[36]; assign px4[25] = sx4[37]; assign px4[41] = sx4[38]; assign px4[57] = sx4[39]; assign px4[10] = sx4[40]; assign px4[26] = sx4[41]; assign px4[42] = sx4[42]; assign px4[58] = sx4[43]; assign px4[11] = sx4[44]; assign px4[27] = sx4[45]; assign px4[43] = sx4[46]; assign px4[59] = sx4[47]; assign px4[12] = sx4[48]; assign px4[28] = sx4[49]; assign px4[44] = sx4[50]; assign px4[60] = sx4[51]; assign px4[13] = sx4[52]; assign px4[29] = sx4[53]; assign px4[45] = sx4[54]; assign px4[61] = sx4[55]; assign px4[14] = sx4[56]; assign px4[30] = sx4[57]; assign px4[46] = sx4[58]; assign px4[62] = sx4[59]; assign px4[15] = sx4[60]; assign px4[31] = sx4[61]; assign px4[47] = sx4[62]; assign px4[63] = sx4[63];
  wire [63:0] st5 = px4;
  wire [63:0] kx5 = st5 ^ rk5;
  wire [63:0] sx5;
  genvar g5;
  generate for (g5=0; g5<16; g5=g5+1) begin : sbl5
    assign sx5[4*g5+3:4*g5] = sb0(kx5[4*g5+3:4*g5]);
  end endgenerate
  wire [63:0] px5;
  assign px5[0] = sx5[0]; assign px5[16] = sx5[1]; assign px5[32] = sx5[2]; assign px5[48] = sx5[3]; assign px5[1] = sx5[4]; assign px5[17] = sx5[5]; assign px5[33] = sx5[6]; assign px5[49] = sx5[7]; assign px5[2] = sx5[8]; assign px5[18] = sx5[9]; assign px5[34] = sx5[10]; assign px5[50] = sx5[11]; assign px5[3] = sx5[12]; assign px5[19] = sx5[13]; assign px5[35] = sx5[14]; assign px5[51] = sx5[15]; assign px5[4] = sx5[16]; assign px5[20] = sx5[17]; assign px5[36] = sx5[18]; assign px5[52] = sx5[19]; assign px5[5] = sx5[20]; assign px5[21] = sx5[21]; assign px5[37] = sx5[22]; assign px5[53] = sx5[23]; assign px5[6] = sx5[24]; assign px5[22] = sx5[25]; assign px5[38] = sx5[26]; assign px5[54] = sx5[27]; assign px5[7] = sx5[28]; assign px5[23] = sx5[29]; assign px5[39] = sx5[30]; assign px5[55] = sx5[31]; assign px5[8] = sx5[32]; assign px5[24] = sx5[33]; assign px5[40] = sx5[34]; assign px5[56] = sx5[35]; assign px5[9] = sx5[36]; assign px5[25] = sx5[37]; assign px5[41] = sx5[38]; assign px5[57] = sx5[39]; assign px5[10] = sx5[40]; assign px5[26] = sx5[41]; assign px5[42] = sx5[42]; assign px5[58] = sx5[43]; assign px5[11] = sx5[44]; assign px5[27] = sx5[45]; assign px5[43] = sx5[46]; assign px5[59] = sx5[47]; assign px5[12] = sx5[48]; assign px5[28] = sx5[49]; assign px5[44] = sx5[50]; assign px5[60] = sx5[51]; assign px5[13] = sx5[52]; assign px5[29] = sx5[53]; assign px5[45] = sx5[54]; assign px5[61] = sx5[55]; assign px5[14] = sx5[56]; assign px5[30] = sx5[57]; assign px5[46] = sx5[58]; assign px5[62] = sx5[59]; assign px5[15] = sx5[60]; assign px5[31] = sx5[61]; assign px5[47] = sx5[62]; assign px5[63] = sx5[63];
  wire [63:0] st6 = px5;
  wire [63:0] key_r13 = {key[50:0], key[63:51]};
  assign out = st6 ^ {32'h0, key_r13[63:32]};
endmodule
