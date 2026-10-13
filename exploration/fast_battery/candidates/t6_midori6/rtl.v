module t6_midori6(input [63:0] val, input [63:0] key, output [63:0] out);
  wire [63:0] st0 = val ^ key;
  reg [63:0] r0_a_sb_r;
  wire [63:0] r0_a_sb = r0_a_sb_r;
  always @(*) begin
    r0_a_sb_r = 64'h0;
    case (st0[3:0])
      4'h0: r0_a_sb_r[3:0] = 4'hc;
      4'h1: r0_a_sb_r[3:0] = 4'ha;
      4'h2: r0_a_sb_r[3:0] = 4'hd;
      4'h3: r0_a_sb_r[3:0] = 4'h3;
      4'h4: r0_a_sb_r[3:0] = 4'he;
      4'h5: r0_a_sb_r[3:0] = 4'hb;
      4'h6: r0_a_sb_r[3:0] = 4'hf;
      4'h7: r0_a_sb_r[3:0] = 4'h7;
      4'h8: r0_a_sb_r[3:0] = 4'h8;
      4'h9: r0_a_sb_r[3:0] = 4'h9;
      4'ha: r0_a_sb_r[3:0] = 4'h1;
      4'hb: r0_a_sb_r[3:0] = 4'h5;
      4'hc: r0_a_sb_r[3:0] = 4'h0;
      4'hd: r0_a_sb_r[3:0] = 4'h2;
      4'he: r0_a_sb_r[3:0] = 4'h4;
      4'hf: r0_a_sb_r[3:0] = 4'h6;
    endcase
    case (st0[7:4])
      4'h0: r0_a_sb_r[7:4] = 4'hc;
      4'h1: r0_a_sb_r[7:4] = 4'ha;
      4'h2: r0_a_sb_r[7:4] = 4'hd;
      4'h3: r0_a_sb_r[7:4] = 4'h3;
      4'h4: r0_a_sb_r[7:4] = 4'he;
      4'h5: r0_a_sb_r[7:4] = 4'hb;
      4'h6: r0_a_sb_r[7:4] = 4'hf;
      4'h7: r0_a_sb_r[7:4] = 4'h7;
      4'h8: r0_a_sb_r[7:4] = 4'h8;
      4'h9: r0_a_sb_r[7:4] = 4'h9;
      4'ha: r0_a_sb_r[7:4] = 4'h1;
      4'hb: r0_a_sb_r[7:4] = 4'h5;
      4'hc: r0_a_sb_r[7:4] = 4'h0;
      4'hd: r0_a_sb_r[7:4] = 4'h2;
      4'he: r0_a_sb_r[7:4] = 4'h4;
      4'hf: r0_a_sb_r[7:4] = 4'h6;
    endcase
    case (st0[11:8])
      4'h0: r0_a_sb_r[11:8] = 4'hc;
      4'h1: r0_a_sb_r[11:8] = 4'ha;
      4'h2: r0_a_sb_r[11:8] = 4'hd;
      4'h3: r0_a_sb_r[11:8] = 4'h3;
      4'h4: r0_a_sb_r[11:8] = 4'he;
      4'h5: r0_a_sb_r[11:8] = 4'hb;
      4'h6: r0_a_sb_r[11:8] = 4'hf;
      4'h7: r0_a_sb_r[11:8] = 4'h7;
      4'h8: r0_a_sb_r[11:8] = 4'h8;
      4'h9: r0_a_sb_r[11:8] = 4'h9;
      4'ha: r0_a_sb_r[11:8] = 4'h1;
      4'hb: r0_a_sb_r[11:8] = 4'h5;
      4'hc: r0_a_sb_r[11:8] = 4'h0;
      4'hd: r0_a_sb_r[11:8] = 4'h2;
      4'he: r0_a_sb_r[11:8] = 4'h4;
      4'hf: r0_a_sb_r[11:8] = 4'h6;
    endcase
    case (st0[15:12])
      4'h0: r0_a_sb_r[15:12] = 4'hc;
      4'h1: r0_a_sb_r[15:12] = 4'ha;
      4'h2: r0_a_sb_r[15:12] = 4'hd;
      4'h3: r0_a_sb_r[15:12] = 4'h3;
      4'h4: r0_a_sb_r[15:12] = 4'he;
      4'h5: r0_a_sb_r[15:12] = 4'hb;
      4'h6: r0_a_sb_r[15:12] = 4'hf;
      4'h7: r0_a_sb_r[15:12] = 4'h7;
      4'h8: r0_a_sb_r[15:12] = 4'h8;
      4'h9: r0_a_sb_r[15:12] = 4'h9;
      4'ha: r0_a_sb_r[15:12] = 4'h1;
      4'hb: r0_a_sb_r[15:12] = 4'h5;
      4'hc: r0_a_sb_r[15:12] = 4'h0;
      4'hd: r0_a_sb_r[15:12] = 4'h2;
      4'he: r0_a_sb_r[15:12] = 4'h4;
      4'hf: r0_a_sb_r[15:12] = 4'h6;
    endcase
    case (st0[19:16])
      4'h0: r0_a_sb_r[19:16] = 4'hc;
      4'h1: r0_a_sb_r[19:16] = 4'ha;
      4'h2: r0_a_sb_r[19:16] = 4'hd;
      4'h3: r0_a_sb_r[19:16] = 4'h3;
      4'h4: r0_a_sb_r[19:16] = 4'he;
      4'h5: r0_a_sb_r[19:16] = 4'hb;
      4'h6: r0_a_sb_r[19:16] = 4'hf;
      4'h7: r0_a_sb_r[19:16] = 4'h7;
      4'h8: r0_a_sb_r[19:16] = 4'h8;
      4'h9: r0_a_sb_r[19:16] = 4'h9;
      4'ha: r0_a_sb_r[19:16] = 4'h1;
      4'hb: r0_a_sb_r[19:16] = 4'h5;
      4'hc: r0_a_sb_r[19:16] = 4'h0;
      4'hd: r0_a_sb_r[19:16] = 4'h2;
      4'he: r0_a_sb_r[19:16] = 4'h4;
      4'hf: r0_a_sb_r[19:16] = 4'h6;
    endcase
    case (st0[23:20])
      4'h0: r0_a_sb_r[23:20] = 4'hc;
      4'h1: r0_a_sb_r[23:20] = 4'ha;
      4'h2: r0_a_sb_r[23:20] = 4'hd;
      4'h3: r0_a_sb_r[23:20] = 4'h3;
      4'h4: r0_a_sb_r[23:20] = 4'he;
      4'h5: r0_a_sb_r[23:20] = 4'hb;
      4'h6: r0_a_sb_r[23:20] = 4'hf;
      4'h7: r0_a_sb_r[23:20] = 4'h7;
      4'h8: r0_a_sb_r[23:20] = 4'h8;
      4'h9: r0_a_sb_r[23:20] = 4'h9;
      4'ha: r0_a_sb_r[23:20] = 4'h1;
      4'hb: r0_a_sb_r[23:20] = 4'h5;
      4'hc: r0_a_sb_r[23:20] = 4'h0;
      4'hd: r0_a_sb_r[23:20] = 4'h2;
      4'he: r0_a_sb_r[23:20] = 4'h4;
      4'hf: r0_a_sb_r[23:20] = 4'h6;
    endcase
    case (st0[27:24])
      4'h0: r0_a_sb_r[27:24] = 4'hc;
      4'h1: r0_a_sb_r[27:24] = 4'ha;
      4'h2: r0_a_sb_r[27:24] = 4'hd;
      4'h3: r0_a_sb_r[27:24] = 4'h3;
      4'h4: r0_a_sb_r[27:24] = 4'he;
      4'h5: r0_a_sb_r[27:24] = 4'hb;
      4'h6: r0_a_sb_r[27:24] = 4'hf;
      4'h7: r0_a_sb_r[27:24] = 4'h7;
      4'h8: r0_a_sb_r[27:24] = 4'h8;
      4'h9: r0_a_sb_r[27:24] = 4'h9;
      4'ha: r0_a_sb_r[27:24] = 4'h1;
      4'hb: r0_a_sb_r[27:24] = 4'h5;
      4'hc: r0_a_sb_r[27:24] = 4'h0;
      4'hd: r0_a_sb_r[27:24] = 4'h2;
      4'he: r0_a_sb_r[27:24] = 4'h4;
      4'hf: r0_a_sb_r[27:24] = 4'h6;
    endcase
    case (st0[31:28])
      4'h0: r0_a_sb_r[31:28] = 4'hc;
      4'h1: r0_a_sb_r[31:28] = 4'ha;
      4'h2: r0_a_sb_r[31:28] = 4'hd;
      4'h3: r0_a_sb_r[31:28] = 4'h3;
      4'h4: r0_a_sb_r[31:28] = 4'he;
      4'h5: r0_a_sb_r[31:28] = 4'hb;
      4'h6: r0_a_sb_r[31:28] = 4'hf;
      4'h7: r0_a_sb_r[31:28] = 4'h7;
      4'h8: r0_a_sb_r[31:28] = 4'h8;
      4'h9: r0_a_sb_r[31:28] = 4'h9;
      4'ha: r0_a_sb_r[31:28] = 4'h1;
      4'hb: r0_a_sb_r[31:28] = 4'h5;
      4'hc: r0_a_sb_r[31:28] = 4'h0;
      4'hd: r0_a_sb_r[31:28] = 4'h2;
      4'he: r0_a_sb_r[31:28] = 4'h4;
      4'hf: r0_a_sb_r[31:28] = 4'h6;
    endcase
    case (st0[35:32])
      4'h0: r0_a_sb_r[35:32] = 4'hc;
      4'h1: r0_a_sb_r[35:32] = 4'ha;
      4'h2: r0_a_sb_r[35:32] = 4'hd;
      4'h3: r0_a_sb_r[35:32] = 4'h3;
      4'h4: r0_a_sb_r[35:32] = 4'he;
      4'h5: r0_a_sb_r[35:32] = 4'hb;
      4'h6: r0_a_sb_r[35:32] = 4'hf;
      4'h7: r0_a_sb_r[35:32] = 4'h7;
      4'h8: r0_a_sb_r[35:32] = 4'h8;
      4'h9: r0_a_sb_r[35:32] = 4'h9;
      4'ha: r0_a_sb_r[35:32] = 4'h1;
      4'hb: r0_a_sb_r[35:32] = 4'h5;
      4'hc: r0_a_sb_r[35:32] = 4'h0;
      4'hd: r0_a_sb_r[35:32] = 4'h2;
      4'he: r0_a_sb_r[35:32] = 4'h4;
      4'hf: r0_a_sb_r[35:32] = 4'h6;
    endcase
    case (st0[39:36])
      4'h0: r0_a_sb_r[39:36] = 4'hc;
      4'h1: r0_a_sb_r[39:36] = 4'ha;
      4'h2: r0_a_sb_r[39:36] = 4'hd;
      4'h3: r0_a_sb_r[39:36] = 4'h3;
      4'h4: r0_a_sb_r[39:36] = 4'he;
      4'h5: r0_a_sb_r[39:36] = 4'hb;
      4'h6: r0_a_sb_r[39:36] = 4'hf;
      4'h7: r0_a_sb_r[39:36] = 4'h7;
      4'h8: r0_a_sb_r[39:36] = 4'h8;
      4'h9: r0_a_sb_r[39:36] = 4'h9;
      4'ha: r0_a_sb_r[39:36] = 4'h1;
      4'hb: r0_a_sb_r[39:36] = 4'h5;
      4'hc: r0_a_sb_r[39:36] = 4'h0;
      4'hd: r0_a_sb_r[39:36] = 4'h2;
      4'he: r0_a_sb_r[39:36] = 4'h4;
      4'hf: r0_a_sb_r[39:36] = 4'h6;
    endcase
    case (st0[43:40])
      4'h0: r0_a_sb_r[43:40] = 4'hc;
      4'h1: r0_a_sb_r[43:40] = 4'ha;
      4'h2: r0_a_sb_r[43:40] = 4'hd;
      4'h3: r0_a_sb_r[43:40] = 4'h3;
      4'h4: r0_a_sb_r[43:40] = 4'he;
      4'h5: r0_a_sb_r[43:40] = 4'hb;
      4'h6: r0_a_sb_r[43:40] = 4'hf;
      4'h7: r0_a_sb_r[43:40] = 4'h7;
      4'h8: r0_a_sb_r[43:40] = 4'h8;
      4'h9: r0_a_sb_r[43:40] = 4'h9;
      4'ha: r0_a_sb_r[43:40] = 4'h1;
      4'hb: r0_a_sb_r[43:40] = 4'h5;
      4'hc: r0_a_sb_r[43:40] = 4'h0;
      4'hd: r0_a_sb_r[43:40] = 4'h2;
      4'he: r0_a_sb_r[43:40] = 4'h4;
      4'hf: r0_a_sb_r[43:40] = 4'h6;
    endcase
    case (st0[47:44])
      4'h0: r0_a_sb_r[47:44] = 4'hc;
      4'h1: r0_a_sb_r[47:44] = 4'ha;
      4'h2: r0_a_sb_r[47:44] = 4'hd;
      4'h3: r0_a_sb_r[47:44] = 4'h3;
      4'h4: r0_a_sb_r[47:44] = 4'he;
      4'h5: r0_a_sb_r[47:44] = 4'hb;
      4'h6: r0_a_sb_r[47:44] = 4'hf;
      4'h7: r0_a_sb_r[47:44] = 4'h7;
      4'h8: r0_a_sb_r[47:44] = 4'h8;
      4'h9: r0_a_sb_r[47:44] = 4'h9;
      4'ha: r0_a_sb_r[47:44] = 4'h1;
      4'hb: r0_a_sb_r[47:44] = 4'h5;
      4'hc: r0_a_sb_r[47:44] = 4'h0;
      4'hd: r0_a_sb_r[47:44] = 4'h2;
      4'he: r0_a_sb_r[47:44] = 4'h4;
      4'hf: r0_a_sb_r[47:44] = 4'h6;
    endcase
    case (st0[51:48])
      4'h0: r0_a_sb_r[51:48] = 4'hc;
      4'h1: r0_a_sb_r[51:48] = 4'ha;
      4'h2: r0_a_sb_r[51:48] = 4'hd;
      4'h3: r0_a_sb_r[51:48] = 4'h3;
      4'h4: r0_a_sb_r[51:48] = 4'he;
      4'h5: r0_a_sb_r[51:48] = 4'hb;
      4'h6: r0_a_sb_r[51:48] = 4'hf;
      4'h7: r0_a_sb_r[51:48] = 4'h7;
      4'h8: r0_a_sb_r[51:48] = 4'h8;
      4'h9: r0_a_sb_r[51:48] = 4'h9;
      4'ha: r0_a_sb_r[51:48] = 4'h1;
      4'hb: r0_a_sb_r[51:48] = 4'h5;
      4'hc: r0_a_sb_r[51:48] = 4'h0;
      4'hd: r0_a_sb_r[51:48] = 4'h2;
      4'he: r0_a_sb_r[51:48] = 4'h4;
      4'hf: r0_a_sb_r[51:48] = 4'h6;
    endcase
    case (st0[55:52])
      4'h0: r0_a_sb_r[55:52] = 4'hc;
      4'h1: r0_a_sb_r[55:52] = 4'ha;
      4'h2: r0_a_sb_r[55:52] = 4'hd;
      4'h3: r0_a_sb_r[55:52] = 4'h3;
      4'h4: r0_a_sb_r[55:52] = 4'he;
      4'h5: r0_a_sb_r[55:52] = 4'hb;
      4'h6: r0_a_sb_r[55:52] = 4'hf;
      4'h7: r0_a_sb_r[55:52] = 4'h7;
      4'h8: r0_a_sb_r[55:52] = 4'h8;
      4'h9: r0_a_sb_r[55:52] = 4'h9;
      4'ha: r0_a_sb_r[55:52] = 4'h1;
      4'hb: r0_a_sb_r[55:52] = 4'h5;
      4'hc: r0_a_sb_r[55:52] = 4'h0;
      4'hd: r0_a_sb_r[55:52] = 4'h2;
      4'he: r0_a_sb_r[55:52] = 4'h4;
      4'hf: r0_a_sb_r[55:52] = 4'h6;
    endcase
    case (st0[59:56])
      4'h0: r0_a_sb_r[59:56] = 4'hc;
      4'h1: r0_a_sb_r[59:56] = 4'ha;
      4'h2: r0_a_sb_r[59:56] = 4'hd;
      4'h3: r0_a_sb_r[59:56] = 4'h3;
      4'h4: r0_a_sb_r[59:56] = 4'he;
      4'h5: r0_a_sb_r[59:56] = 4'hb;
      4'h6: r0_a_sb_r[59:56] = 4'hf;
      4'h7: r0_a_sb_r[59:56] = 4'h7;
      4'h8: r0_a_sb_r[59:56] = 4'h8;
      4'h9: r0_a_sb_r[59:56] = 4'h9;
      4'ha: r0_a_sb_r[59:56] = 4'h1;
      4'hb: r0_a_sb_r[59:56] = 4'h5;
      4'hc: r0_a_sb_r[59:56] = 4'h0;
      4'hd: r0_a_sb_r[59:56] = 4'h2;
      4'he: r0_a_sb_r[59:56] = 4'h4;
      4'hf: r0_a_sb_r[59:56] = 4'h6;
    endcase
    case (st0[63:60])
      4'h0: r0_a_sb_r[63:60] = 4'hc;
      4'h1: r0_a_sb_r[63:60] = 4'ha;
      4'h2: r0_a_sb_r[63:60] = 4'hd;
      4'h3: r0_a_sb_r[63:60] = 4'h3;
      4'h4: r0_a_sb_r[63:60] = 4'he;
      4'h5: r0_a_sb_r[63:60] = 4'hb;
      4'h6: r0_a_sb_r[63:60] = 4'hf;
      4'h7: r0_a_sb_r[63:60] = 4'h7;
      4'h8: r0_a_sb_r[63:60] = 4'h8;
      4'h9: r0_a_sb_r[63:60] = 4'h9;
      4'ha: r0_a_sb_r[63:60] = 4'h1;
      4'hb: r0_a_sb_r[63:60] = 4'h5;
      4'hc: r0_a_sb_r[63:60] = 4'h0;
      4'hd: r0_a_sb_r[63:60] = 4'h2;
      4'he: r0_a_sb_r[63:60] = 4'h4;
      4'hf: r0_a_sb_r[63:60] = 4'h6;
    endcase
  end
  // Midori ShuffleCell
  wire [63:0] r0_b_sh = {r0_a_sb[35:32], r0_a_sb[11:8], r0_a_sb[55:52], r0_a_sb[31:28], r0_a_sb[27:24], r0_a_sb[51:48], r0_a_sb[15:12], r0_a_sb[39:36], r0_a_sb[7:4], r0_a_sb[47:44], r0_a_sb[19:16], r0_a_sb[59:56], r0_a_sb[63:60], r0_a_sb[23:20], r0_a_sb[43:40], r0_a_sb[3:0]};
  // Midori MixColumn
  wire [63:0] r0_c_mc;
  assign r0_c_mc[3:0] = r0_b_sh[19:16] ^ r0_b_sh[35:32] ^ r0_b_sh[51:48];
  assign r0_c_mc[19:16] = r0_b_sh[3:0] ^ r0_b_sh[35:32] ^ r0_b_sh[51:48];
  assign r0_c_mc[35:32] = r0_b_sh[3:0] ^ r0_b_sh[19:16] ^ r0_b_sh[51:48];
  assign r0_c_mc[51:48] = r0_b_sh[3:0] ^ r0_b_sh[19:16] ^ r0_b_sh[35:32];
  assign r0_c_mc[7:4] = r0_b_sh[23:20] ^ r0_b_sh[39:36] ^ r0_b_sh[55:52];
  assign r0_c_mc[23:20] = r0_b_sh[7:4] ^ r0_b_sh[39:36] ^ r0_b_sh[55:52];
  assign r0_c_mc[39:36] = r0_b_sh[7:4] ^ r0_b_sh[23:20] ^ r0_b_sh[55:52];
  assign r0_c_mc[55:52] = r0_b_sh[7:4] ^ r0_b_sh[23:20] ^ r0_b_sh[39:36];
  assign r0_c_mc[11:8] = r0_b_sh[27:24] ^ r0_b_sh[43:40] ^ r0_b_sh[59:56];
  assign r0_c_mc[27:24] = r0_b_sh[11:8] ^ r0_b_sh[43:40] ^ r0_b_sh[59:56];
  assign r0_c_mc[43:40] = r0_b_sh[11:8] ^ r0_b_sh[27:24] ^ r0_b_sh[59:56];
  assign r0_c_mc[59:56] = r0_b_sh[11:8] ^ r0_b_sh[27:24] ^ r0_b_sh[43:40];
  assign r0_c_mc[15:12] = r0_b_sh[31:28] ^ r0_b_sh[47:44] ^ r0_b_sh[63:60];
  assign r0_c_mc[31:28] = r0_b_sh[15:12] ^ r0_b_sh[47:44] ^ r0_b_sh[63:60];
  assign r0_c_mc[47:44] = r0_b_sh[15:12] ^ r0_b_sh[31:28] ^ r0_b_sh[63:60];
  assign r0_c_mc[63:60] = r0_b_sh[15:12] ^ r0_b_sh[31:28] ^ r0_b_sh[47:44];
  wire [63:0] st1 = r0_c_mc ^ 64'h9e3779b97f4a7c15 ^ {key[50:0], key[63:51]};
  reg [63:0] r1_a_sb_r;
  wire [63:0] r1_a_sb = r1_a_sb_r;
  always @(*) begin
    r1_a_sb_r = 64'h0;
    case (st1[3:0])
      4'h0: r1_a_sb_r[3:0] = 4'hc;
      4'h1: r1_a_sb_r[3:0] = 4'ha;
      4'h2: r1_a_sb_r[3:0] = 4'hd;
      4'h3: r1_a_sb_r[3:0] = 4'h3;
      4'h4: r1_a_sb_r[3:0] = 4'he;
      4'h5: r1_a_sb_r[3:0] = 4'hb;
      4'h6: r1_a_sb_r[3:0] = 4'hf;
      4'h7: r1_a_sb_r[3:0] = 4'h7;
      4'h8: r1_a_sb_r[3:0] = 4'h8;
      4'h9: r1_a_sb_r[3:0] = 4'h9;
      4'ha: r1_a_sb_r[3:0] = 4'h1;
      4'hb: r1_a_sb_r[3:0] = 4'h5;
      4'hc: r1_a_sb_r[3:0] = 4'h0;
      4'hd: r1_a_sb_r[3:0] = 4'h2;
      4'he: r1_a_sb_r[3:0] = 4'h4;
      4'hf: r1_a_sb_r[3:0] = 4'h6;
    endcase
    case (st1[7:4])
      4'h0: r1_a_sb_r[7:4] = 4'hc;
      4'h1: r1_a_sb_r[7:4] = 4'ha;
      4'h2: r1_a_sb_r[7:4] = 4'hd;
      4'h3: r1_a_sb_r[7:4] = 4'h3;
      4'h4: r1_a_sb_r[7:4] = 4'he;
      4'h5: r1_a_sb_r[7:4] = 4'hb;
      4'h6: r1_a_sb_r[7:4] = 4'hf;
      4'h7: r1_a_sb_r[7:4] = 4'h7;
      4'h8: r1_a_sb_r[7:4] = 4'h8;
      4'h9: r1_a_sb_r[7:4] = 4'h9;
      4'ha: r1_a_sb_r[7:4] = 4'h1;
      4'hb: r1_a_sb_r[7:4] = 4'h5;
      4'hc: r1_a_sb_r[7:4] = 4'h0;
      4'hd: r1_a_sb_r[7:4] = 4'h2;
      4'he: r1_a_sb_r[7:4] = 4'h4;
      4'hf: r1_a_sb_r[7:4] = 4'h6;
    endcase
    case (st1[11:8])
      4'h0: r1_a_sb_r[11:8] = 4'hc;
      4'h1: r1_a_sb_r[11:8] = 4'ha;
      4'h2: r1_a_sb_r[11:8] = 4'hd;
      4'h3: r1_a_sb_r[11:8] = 4'h3;
      4'h4: r1_a_sb_r[11:8] = 4'he;
      4'h5: r1_a_sb_r[11:8] = 4'hb;
      4'h6: r1_a_sb_r[11:8] = 4'hf;
      4'h7: r1_a_sb_r[11:8] = 4'h7;
      4'h8: r1_a_sb_r[11:8] = 4'h8;
      4'h9: r1_a_sb_r[11:8] = 4'h9;
      4'ha: r1_a_sb_r[11:8] = 4'h1;
      4'hb: r1_a_sb_r[11:8] = 4'h5;
      4'hc: r1_a_sb_r[11:8] = 4'h0;
      4'hd: r1_a_sb_r[11:8] = 4'h2;
      4'he: r1_a_sb_r[11:8] = 4'h4;
      4'hf: r1_a_sb_r[11:8] = 4'h6;
    endcase
    case (st1[15:12])
      4'h0: r1_a_sb_r[15:12] = 4'hc;
      4'h1: r1_a_sb_r[15:12] = 4'ha;
      4'h2: r1_a_sb_r[15:12] = 4'hd;
      4'h3: r1_a_sb_r[15:12] = 4'h3;
      4'h4: r1_a_sb_r[15:12] = 4'he;
      4'h5: r1_a_sb_r[15:12] = 4'hb;
      4'h6: r1_a_sb_r[15:12] = 4'hf;
      4'h7: r1_a_sb_r[15:12] = 4'h7;
      4'h8: r1_a_sb_r[15:12] = 4'h8;
      4'h9: r1_a_sb_r[15:12] = 4'h9;
      4'ha: r1_a_sb_r[15:12] = 4'h1;
      4'hb: r1_a_sb_r[15:12] = 4'h5;
      4'hc: r1_a_sb_r[15:12] = 4'h0;
      4'hd: r1_a_sb_r[15:12] = 4'h2;
      4'he: r1_a_sb_r[15:12] = 4'h4;
      4'hf: r1_a_sb_r[15:12] = 4'h6;
    endcase
    case (st1[19:16])
      4'h0: r1_a_sb_r[19:16] = 4'hc;
      4'h1: r1_a_sb_r[19:16] = 4'ha;
      4'h2: r1_a_sb_r[19:16] = 4'hd;
      4'h3: r1_a_sb_r[19:16] = 4'h3;
      4'h4: r1_a_sb_r[19:16] = 4'he;
      4'h5: r1_a_sb_r[19:16] = 4'hb;
      4'h6: r1_a_sb_r[19:16] = 4'hf;
      4'h7: r1_a_sb_r[19:16] = 4'h7;
      4'h8: r1_a_sb_r[19:16] = 4'h8;
      4'h9: r1_a_sb_r[19:16] = 4'h9;
      4'ha: r1_a_sb_r[19:16] = 4'h1;
      4'hb: r1_a_sb_r[19:16] = 4'h5;
      4'hc: r1_a_sb_r[19:16] = 4'h0;
      4'hd: r1_a_sb_r[19:16] = 4'h2;
      4'he: r1_a_sb_r[19:16] = 4'h4;
      4'hf: r1_a_sb_r[19:16] = 4'h6;
    endcase
    case (st1[23:20])
      4'h0: r1_a_sb_r[23:20] = 4'hc;
      4'h1: r1_a_sb_r[23:20] = 4'ha;
      4'h2: r1_a_sb_r[23:20] = 4'hd;
      4'h3: r1_a_sb_r[23:20] = 4'h3;
      4'h4: r1_a_sb_r[23:20] = 4'he;
      4'h5: r1_a_sb_r[23:20] = 4'hb;
      4'h6: r1_a_sb_r[23:20] = 4'hf;
      4'h7: r1_a_sb_r[23:20] = 4'h7;
      4'h8: r1_a_sb_r[23:20] = 4'h8;
      4'h9: r1_a_sb_r[23:20] = 4'h9;
      4'ha: r1_a_sb_r[23:20] = 4'h1;
      4'hb: r1_a_sb_r[23:20] = 4'h5;
      4'hc: r1_a_sb_r[23:20] = 4'h0;
      4'hd: r1_a_sb_r[23:20] = 4'h2;
      4'he: r1_a_sb_r[23:20] = 4'h4;
      4'hf: r1_a_sb_r[23:20] = 4'h6;
    endcase
    case (st1[27:24])
      4'h0: r1_a_sb_r[27:24] = 4'hc;
      4'h1: r1_a_sb_r[27:24] = 4'ha;
      4'h2: r1_a_sb_r[27:24] = 4'hd;
      4'h3: r1_a_sb_r[27:24] = 4'h3;
      4'h4: r1_a_sb_r[27:24] = 4'he;
      4'h5: r1_a_sb_r[27:24] = 4'hb;
      4'h6: r1_a_sb_r[27:24] = 4'hf;
      4'h7: r1_a_sb_r[27:24] = 4'h7;
      4'h8: r1_a_sb_r[27:24] = 4'h8;
      4'h9: r1_a_sb_r[27:24] = 4'h9;
      4'ha: r1_a_sb_r[27:24] = 4'h1;
      4'hb: r1_a_sb_r[27:24] = 4'h5;
      4'hc: r1_a_sb_r[27:24] = 4'h0;
      4'hd: r1_a_sb_r[27:24] = 4'h2;
      4'he: r1_a_sb_r[27:24] = 4'h4;
      4'hf: r1_a_sb_r[27:24] = 4'h6;
    endcase
    case (st1[31:28])
      4'h0: r1_a_sb_r[31:28] = 4'hc;
      4'h1: r1_a_sb_r[31:28] = 4'ha;
      4'h2: r1_a_sb_r[31:28] = 4'hd;
      4'h3: r1_a_sb_r[31:28] = 4'h3;
      4'h4: r1_a_sb_r[31:28] = 4'he;
      4'h5: r1_a_sb_r[31:28] = 4'hb;
      4'h6: r1_a_sb_r[31:28] = 4'hf;
      4'h7: r1_a_sb_r[31:28] = 4'h7;
      4'h8: r1_a_sb_r[31:28] = 4'h8;
      4'h9: r1_a_sb_r[31:28] = 4'h9;
      4'ha: r1_a_sb_r[31:28] = 4'h1;
      4'hb: r1_a_sb_r[31:28] = 4'h5;
      4'hc: r1_a_sb_r[31:28] = 4'h0;
      4'hd: r1_a_sb_r[31:28] = 4'h2;
      4'he: r1_a_sb_r[31:28] = 4'h4;
      4'hf: r1_a_sb_r[31:28] = 4'h6;
    endcase
    case (st1[35:32])
      4'h0: r1_a_sb_r[35:32] = 4'hc;
      4'h1: r1_a_sb_r[35:32] = 4'ha;
      4'h2: r1_a_sb_r[35:32] = 4'hd;
      4'h3: r1_a_sb_r[35:32] = 4'h3;
      4'h4: r1_a_sb_r[35:32] = 4'he;
      4'h5: r1_a_sb_r[35:32] = 4'hb;
      4'h6: r1_a_sb_r[35:32] = 4'hf;
      4'h7: r1_a_sb_r[35:32] = 4'h7;
      4'h8: r1_a_sb_r[35:32] = 4'h8;
      4'h9: r1_a_sb_r[35:32] = 4'h9;
      4'ha: r1_a_sb_r[35:32] = 4'h1;
      4'hb: r1_a_sb_r[35:32] = 4'h5;
      4'hc: r1_a_sb_r[35:32] = 4'h0;
      4'hd: r1_a_sb_r[35:32] = 4'h2;
      4'he: r1_a_sb_r[35:32] = 4'h4;
      4'hf: r1_a_sb_r[35:32] = 4'h6;
    endcase
    case (st1[39:36])
      4'h0: r1_a_sb_r[39:36] = 4'hc;
      4'h1: r1_a_sb_r[39:36] = 4'ha;
      4'h2: r1_a_sb_r[39:36] = 4'hd;
      4'h3: r1_a_sb_r[39:36] = 4'h3;
      4'h4: r1_a_sb_r[39:36] = 4'he;
      4'h5: r1_a_sb_r[39:36] = 4'hb;
      4'h6: r1_a_sb_r[39:36] = 4'hf;
      4'h7: r1_a_sb_r[39:36] = 4'h7;
      4'h8: r1_a_sb_r[39:36] = 4'h8;
      4'h9: r1_a_sb_r[39:36] = 4'h9;
      4'ha: r1_a_sb_r[39:36] = 4'h1;
      4'hb: r1_a_sb_r[39:36] = 4'h5;
      4'hc: r1_a_sb_r[39:36] = 4'h0;
      4'hd: r1_a_sb_r[39:36] = 4'h2;
      4'he: r1_a_sb_r[39:36] = 4'h4;
      4'hf: r1_a_sb_r[39:36] = 4'h6;
    endcase
    case (st1[43:40])
      4'h0: r1_a_sb_r[43:40] = 4'hc;
      4'h1: r1_a_sb_r[43:40] = 4'ha;
      4'h2: r1_a_sb_r[43:40] = 4'hd;
      4'h3: r1_a_sb_r[43:40] = 4'h3;
      4'h4: r1_a_sb_r[43:40] = 4'he;
      4'h5: r1_a_sb_r[43:40] = 4'hb;
      4'h6: r1_a_sb_r[43:40] = 4'hf;
      4'h7: r1_a_sb_r[43:40] = 4'h7;
      4'h8: r1_a_sb_r[43:40] = 4'h8;
      4'h9: r1_a_sb_r[43:40] = 4'h9;
      4'ha: r1_a_sb_r[43:40] = 4'h1;
      4'hb: r1_a_sb_r[43:40] = 4'h5;
      4'hc: r1_a_sb_r[43:40] = 4'h0;
      4'hd: r1_a_sb_r[43:40] = 4'h2;
      4'he: r1_a_sb_r[43:40] = 4'h4;
      4'hf: r1_a_sb_r[43:40] = 4'h6;
    endcase
    case (st1[47:44])
      4'h0: r1_a_sb_r[47:44] = 4'hc;
      4'h1: r1_a_sb_r[47:44] = 4'ha;
      4'h2: r1_a_sb_r[47:44] = 4'hd;
      4'h3: r1_a_sb_r[47:44] = 4'h3;
      4'h4: r1_a_sb_r[47:44] = 4'he;
      4'h5: r1_a_sb_r[47:44] = 4'hb;
      4'h6: r1_a_sb_r[47:44] = 4'hf;
      4'h7: r1_a_sb_r[47:44] = 4'h7;
      4'h8: r1_a_sb_r[47:44] = 4'h8;
      4'h9: r1_a_sb_r[47:44] = 4'h9;
      4'ha: r1_a_sb_r[47:44] = 4'h1;
      4'hb: r1_a_sb_r[47:44] = 4'h5;
      4'hc: r1_a_sb_r[47:44] = 4'h0;
      4'hd: r1_a_sb_r[47:44] = 4'h2;
      4'he: r1_a_sb_r[47:44] = 4'h4;
      4'hf: r1_a_sb_r[47:44] = 4'h6;
    endcase
    case (st1[51:48])
      4'h0: r1_a_sb_r[51:48] = 4'hc;
      4'h1: r1_a_sb_r[51:48] = 4'ha;
      4'h2: r1_a_sb_r[51:48] = 4'hd;
      4'h3: r1_a_sb_r[51:48] = 4'h3;
      4'h4: r1_a_sb_r[51:48] = 4'he;
      4'h5: r1_a_sb_r[51:48] = 4'hb;
      4'h6: r1_a_sb_r[51:48] = 4'hf;
      4'h7: r1_a_sb_r[51:48] = 4'h7;
      4'h8: r1_a_sb_r[51:48] = 4'h8;
      4'h9: r1_a_sb_r[51:48] = 4'h9;
      4'ha: r1_a_sb_r[51:48] = 4'h1;
      4'hb: r1_a_sb_r[51:48] = 4'h5;
      4'hc: r1_a_sb_r[51:48] = 4'h0;
      4'hd: r1_a_sb_r[51:48] = 4'h2;
      4'he: r1_a_sb_r[51:48] = 4'h4;
      4'hf: r1_a_sb_r[51:48] = 4'h6;
    endcase
    case (st1[55:52])
      4'h0: r1_a_sb_r[55:52] = 4'hc;
      4'h1: r1_a_sb_r[55:52] = 4'ha;
      4'h2: r1_a_sb_r[55:52] = 4'hd;
      4'h3: r1_a_sb_r[55:52] = 4'h3;
      4'h4: r1_a_sb_r[55:52] = 4'he;
      4'h5: r1_a_sb_r[55:52] = 4'hb;
      4'h6: r1_a_sb_r[55:52] = 4'hf;
      4'h7: r1_a_sb_r[55:52] = 4'h7;
      4'h8: r1_a_sb_r[55:52] = 4'h8;
      4'h9: r1_a_sb_r[55:52] = 4'h9;
      4'ha: r1_a_sb_r[55:52] = 4'h1;
      4'hb: r1_a_sb_r[55:52] = 4'h5;
      4'hc: r1_a_sb_r[55:52] = 4'h0;
      4'hd: r1_a_sb_r[55:52] = 4'h2;
      4'he: r1_a_sb_r[55:52] = 4'h4;
      4'hf: r1_a_sb_r[55:52] = 4'h6;
    endcase
    case (st1[59:56])
      4'h0: r1_a_sb_r[59:56] = 4'hc;
      4'h1: r1_a_sb_r[59:56] = 4'ha;
      4'h2: r1_a_sb_r[59:56] = 4'hd;
      4'h3: r1_a_sb_r[59:56] = 4'h3;
      4'h4: r1_a_sb_r[59:56] = 4'he;
      4'h5: r1_a_sb_r[59:56] = 4'hb;
      4'h6: r1_a_sb_r[59:56] = 4'hf;
      4'h7: r1_a_sb_r[59:56] = 4'h7;
      4'h8: r1_a_sb_r[59:56] = 4'h8;
      4'h9: r1_a_sb_r[59:56] = 4'h9;
      4'ha: r1_a_sb_r[59:56] = 4'h1;
      4'hb: r1_a_sb_r[59:56] = 4'h5;
      4'hc: r1_a_sb_r[59:56] = 4'h0;
      4'hd: r1_a_sb_r[59:56] = 4'h2;
      4'he: r1_a_sb_r[59:56] = 4'h4;
      4'hf: r1_a_sb_r[59:56] = 4'h6;
    endcase
    case (st1[63:60])
      4'h0: r1_a_sb_r[63:60] = 4'hc;
      4'h1: r1_a_sb_r[63:60] = 4'ha;
      4'h2: r1_a_sb_r[63:60] = 4'hd;
      4'h3: r1_a_sb_r[63:60] = 4'h3;
      4'h4: r1_a_sb_r[63:60] = 4'he;
      4'h5: r1_a_sb_r[63:60] = 4'hb;
      4'h6: r1_a_sb_r[63:60] = 4'hf;
      4'h7: r1_a_sb_r[63:60] = 4'h7;
      4'h8: r1_a_sb_r[63:60] = 4'h8;
      4'h9: r1_a_sb_r[63:60] = 4'h9;
      4'ha: r1_a_sb_r[63:60] = 4'h1;
      4'hb: r1_a_sb_r[63:60] = 4'h5;
      4'hc: r1_a_sb_r[63:60] = 4'h0;
      4'hd: r1_a_sb_r[63:60] = 4'h2;
      4'he: r1_a_sb_r[63:60] = 4'h4;
      4'hf: r1_a_sb_r[63:60] = 4'h6;
    endcase
  end
  // Midori ShuffleCell
  wire [63:0] r1_b_sh = {r1_a_sb[35:32], r1_a_sb[11:8], r1_a_sb[55:52], r1_a_sb[31:28], r1_a_sb[27:24], r1_a_sb[51:48], r1_a_sb[15:12], r1_a_sb[39:36], r1_a_sb[7:4], r1_a_sb[47:44], r1_a_sb[19:16], r1_a_sb[59:56], r1_a_sb[63:60], r1_a_sb[23:20], r1_a_sb[43:40], r1_a_sb[3:0]};
  // Midori MixColumn
  wire [63:0] r1_c_mc;
  assign r1_c_mc[3:0] = r1_b_sh[19:16] ^ r1_b_sh[35:32] ^ r1_b_sh[51:48];
  assign r1_c_mc[19:16] = r1_b_sh[3:0] ^ r1_b_sh[35:32] ^ r1_b_sh[51:48];
  assign r1_c_mc[35:32] = r1_b_sh[3:0] ^ r1_b_sh[19:16] ^ r1_b_sh[51:48];
  assign r1_c_mc[51:48] = r1_b_sh[3:0] ^ r1_b_sh[19:16] ^ r1_b_sh[35:32];
  assign r1_c_mc[7:4] = r1_b_sh[23:20] ^ r1_b_sh[39:36] ^ r1_b_sh[55:52];
  assign r1_c_mc[23:20] = r1_b_sh[7:4] ^ r1_b_sh[39:36] ^ r1_b_sh[55:52];
  assign r1_c_mc[39:36] = r1_b_sh[7:4] ^ r1_b_sh[23:20] ^ r1_b_sh[55:52];
  assign r1_c_mc[55:52] = r1_b_sh[7:4] ^ r1_b_sh[23:20] ^ r1_b_sh[39:36];
  assign r1_c_mc[11:8] = r1_b_sh[27:24] ^ r1_b_sh[43:40] ^ r1_b_sh[59:56];
  assign r1_c_mc[27:24] = r1_b_sh[11:8] ^ r1_b_sh[43:40] ^ r1_b_sh[59:56];
  assign r1_c_mc[43:40] = r1_b_sh[11:8] ^ r1_b_sh[27:24] ^ r1_b_sh[59:56];
  assign r1_c_mc[59:56] = r1_b_sh[11:8] ^ r1_b_sh[27:24] ^ r1_b_sh[43:40];
  assign r1_c_mc[15:12] = r1_b_sh[31:28] ^ r1_b_sh[47:44] ^ r1_b_sh[63:60];
  assign r1_c_mc[31:28] = r1_b_sh[15:12] ^ r1_b_sh[47:44] ^ r1_b_sh[63:60];
  assign r1_c_mc[47:44] = r1_b_sh[15:12] ^ r1_b_sh[31:28] ^ r1_b_sh[63:60];
  assign r1_c_mc[63:60] = r1_b_sh[15:12] ^ r1_b_sh[31:28] ^ r1_b_sh[47:44];
  wire [63:0] st2 = r1_c_mc ^ 64'h3c6ef372fe94f82a ^ {key[37:0], key[63:38]};
  reg [63:0] r2_a_sb_r;
  wire [63:0] r2_a_sb = r2_a_sb_r;
  always @(*) begin
    r2_a_sb_r = 64'h0;
    case (st2[3:0])
      4'h0: r2_a_sb_r[3:0] = 4'hc;
      4'h1: r2_a_sb_r[3:0] = 4'ha;
      4'h2: r2_a_sb_r[3:0] = 4'hd;
      4'h3: r2_a_sb_r[3:0] = 4'h3;
      4'h4: r2_a_sb_r[3:0] = 4'he;
      4'h5: r2_a_sb_r[3:0] = 4'hb;
      4'h6: r2_a_sb_r[3:0] = 4'hf;
      4'h7: r2_a_sb_r[3:0] = 4'h7;
      4'h8: r2_a_sb_r[3:0] = 4'h8;
      4'h9: r2_a_sb_r[3:0] = 4'h9;
      4'ha: r2_a_sb_r[3:0] = 4'h1;
      4'hb: r2_a_sb_r[3:0] = 4'h5;
      4'hc: r2_a_sb_r[3:0] = 4'h0;
      4'hd: r2_a_sb_r[3:0] = 4'h2;
      4'he: r2_a_sb_r[3:0] = 4'h4;
      4'hf: r2_a_sb_r[3:0] = 4'h6;
    endcase
    case (st2[7:4])
      4'h0: r2_a_sb_r[7:4] = 4'hc;
      4'h1: r2_a_sb_r[7:4] = 4'ha;
      4'h2: r2_a_sb_r[7:4] = 4'hd;
      4'h3: r2_a_sb_r[7:4] = 4'h3;
      4'h4: r2_a_sb_r[7:4] = 4'he;
      4'h5: r2_a_sb_r[7:4] = 4'hb;
      4'h6: r2_a_sb_r[7:4] = 4'hf;
      4'h7: r2_a_sb_r[7:4] = 4'h7;
      4'h8: r2_a_sb_r[7:4] = 4'h8;
      4'h9: r2_a_sb_r[7:4] = 4'h9;
      4'ha: r2_a_sb_r[7:4] = 4'h1;
      4'hb: r2_a_sb_r[7:4] = 4'h5;
      4'hc: r2_a_sb_r[7:4] = 4'h0;
      4'hd: r2_a_sb_r[7:4] = 4'h2;
      4'he: r2_a_sb_r[7:4] = 4'h4;
      4'hf: r2_a_sb_r[7:4] = 4'h6;
    endcase
    case (st2[11:8])
      4'h0: r2_a_sb_r[11:8] = 4'hc;
      4'h1: r2_a_sb_r[11:8] = 4'ha;
      4'h2: r2_a_sb_r[11:8] = 4'hd;
      4'h3: r2_a_sb_r[11:8] = 4'h3;
      4'h4: r2_a_sb_r[11:8] = 4'he;
      4'h5: r2_a_sb_r[11:8] = 4'hb;
      4'h6: r2_a_sb_r[11:8] = 4'hf;
      4'h7: r2_a_sb_r[11:8] = 4'h7;
      4'h8: r2_a_sb_r[11:8] = 4'h8;
      4'h9: r2_a_sb_r[11:8] = 4'h9;
      4'ha: r2_a_sb_r[11:8] = 4'h1;
      4'hb: r2_a_sb_r[11:8] = 4'h5;
      4'hc: r2_a_sb_r[11:8] = 4'h0;
      4'hd: r2_a_sb_r[11:8] = 4'h2;
      4'he: r2_a_sb_r[11:8] = 4'h4;
      4'hf: r2_a_sb_r[11:8] = 4'h6;
    endcase
    case (st2[15:12])
      4'h0: r2_a_sb_r[15:12] = 4'hc;
      4'h1: r2_a_sb_r[15:12] = 4'ha;
      4'h2: r2_a_sb_r[15:12] = 4'hd;
      4'h3: r2_a_sb_r[15:12] = 4'h3;
      4'h4: r2_a_sb_r[15:12] = 4'he;
      4'h5: r2_a_sb_r[15:12] = 4'hb;
      4'h6: r2_a_sb_r[15:12] = 4'hf;
      4'h7: r2_a_sb_r[15:12] = 4'h7;
      4'h8: r2_a_sb_r[15:12] = 4'h8;
      4'h9: r2_a_sb_r[15:12] = 4'h9;
      4'ha: r2_a_sb_r[15:12] = 4'h1;
      4'hb: r2_a_sb_r[15:12] = 4'h5;
      4'hc: r2_a_sb_r[15:12] = 4'h0;
      4'hd: r2_a_sb_r[15:12] = 4'h2;
      4'he: r2_a_sb_r[15:12] = 4'h4;
      4'hf: r2_a_sb_r[15:12] = 4'h6;
    endcase
    case (st2[19:16])
      4'h0: r2_a_sb_r[19:16] = 4'hc;
      4'h1: r2_a_sb_r[19:16] = 4'ha;
      4'h2: r2_a_sb_r[19:16] = 4'hd;
      4'h3: r2_a_sb_r[19:16] = 4'h3;
      4'h4: r2_a_sb_r[19:16] = 4'he;
      4'h5: r2_a_sb_r[19:16] = 4'hb;
      4'h6: r2_a_sb_r[19:16] = 4'hf;
      4'h7: r2_a_sb_r[19:16] = 4'h7;
      4'h8: r2_a_sb_r[19:16] = 4'h8;
      4'h9: r2_a_sb_r[19:16] = 4'h9;
      4'ha: r2_a_sb_r[19:16] = 4'h1;
      4'hb: r2_a_sb_r[19:16] = 4'h5;
      4'hc: r2_a_sb_r[19:16] = 4'h0;
      4'hd: r2_a_sb_r[19:16] = 4'h2;
      4'he: r2_a_sb_r[19:16] = 4'h4;
      4'hf: r2_a_sb_r[19:16] = 4'h6;
    endcase
    case (st2[23:20])
      4'h0: r2_a_sb_r[23:20] = 4'hc;
      4'h1: r2_a_sb_r[23:20] = 4'ha;
      4'h2: r2_a_sb_r[23:20] = 4'hd;
      4'h3: r2_a_sb_r[23:20] = 4'h3;
      4'h4: r2_a_sb_r[23:20] = 4'he;
      4'h5: r2_a_sb_r[23:20] = 4'hb;
      4'h6: r2_a_sb_r[23:20] = 4'hf;
      4'h7: r2_a_sb_r[23:20] = 4'h7;
      4'h8: r2_a_sb_r[23:20] = 4'h8;
      4'h9: r2_a_sb_r[23:20] = 4'h9;
      4'ha: r2_a_sb_r[23:20] = 4'h1;
      4'hb: r2_a_sb_r[23:20] = 4'h5;
      4'hc: r2_a_sb_r[23:20] = 4'h0;
      4'hd: r2_a_sb_r[23:20] = 4'h2;
      4'he: r2_a_sb_r[23:20] = 4'h4;
      4'hf: r2_a_sb_r[23:20] = 4'h6;
    endcase
    case (st2[27:24])
      4'h0: r2_a_sb_r[27:24] = 4'hc;
      4'h1: r2_a_sb_r[27:24] = 4'ha;
      4'h2: r2_a_sb_r[27:24] = 4'hd;
      4'h3: r2_a_sb_r[27:24] = 4'h3;
      4'h4: r2_a_sb_r[27:24] = 4'he;
      4'h5: r2_a_sb_r[27:24] = 4'hb;
      4'h6: r2_a_sb_r[27:24] = 4'hf;
      4'h7: r2_a_sb_r[27:24] = 4'h7;
      4'h8: r2_a_sb_r[27:24] = 4'h8;
      4'h9: r2_a_sb_r[27:24] = 4'h9;
      4'ha: r2_a_sb_r[27:24] = 4'h1;
      4'hb: r2_a_sb_r[27:24] = 4'h5;
      4'hc: r2_a_sb_r[27:24] = 4'h0;
      4'hd: r2_a_sb_r[27:24] = 4'h2;
      4'he: r2_a_sb_r[27:24] = 4'h4;
      4'hf: r2_a_sb_r[27:24] = 4'h6;
    endcase
    case (st2[31:28])
      4'h0: r2_a_sb_r[31:28] = 4'hc;
      4'h1: r2_a_sb_r[31:28] = 4'ha;
      4'h2: r2_a_sb_r[31:28] = 4'hd;
      4'h3: r2_a_sb_r[31:28] = 4'h3;
      4'h4: r2_a_sb_r[31:28] = 4'he;
      4'h5: r2_a_sb_r[31:28] = 4'hb;
      4'h6: r2_a_sb_r[31:28] = 4'hf;
      4'h7: r2_a_sb_r[31:28] = 4'h7;
      4'h8: r2_a_sb_r[31:28] = 4'h8;
      4'h9: r2_a_sb_r[31:28] = 4'h9;
      4'ha: r2_a_sb_r[31:28] = 4'h1;
      4'hb: r2_a_sb_r[31:28] = 4'h5;
      4'hc: r2_a_sb_r[31:28] = 4'h0;
      4'hd: r2_a_sb_r[31:28] = 4'h2;
      4'he: r2_a_sb_r[31:28] = 4'h4;
      4'hf: r2_a_sb_r[31:28] = 4'h6;
    endcase
    case (st2[35:32])
      4'h0: r2_a_sb_r[35:32] = 4'hc;
      4'h1: r2_a_sb_r[35:32] = 4'ha;
      4'h2: r2_a_sb_r[35:32] = 4'hd;
      4'h3: r2_a_sb_r[35:32] = 4'h3;
      4'h4: r2_a_sb_r[35:32] = 4'he;
      4'h5: r2_a_sb_r[35:32] = 4'hb;
      4'h6: r2_a_sb_r[35:32] = 4'hf;
      4'h7: r2_a_sb_r[35:32] = 4'h7;
      4'h8: r2_a_sb_r[35:32] = 4'h8;
      4'h9: r2_a_sb_r[35:32] = 4'h9;
      4'ha: r2_a_sb_r[35:32] = 4'h1;
      4'hb: r2_a_sb_r[35:32] = 4'h5;
      4'hc: r2_a_sb_r[35:32] = 4'h0;
      4'hd: r2_a_sb_r[35:32] = 4'h2;
      4'he: r2_a_sb_r[35:32] = 4'h4;
      4'hf: r2_a_sb_r[35:32] = 4'h6;
    endcase
    case (st2[39:36])
      4'h0: r2_a_sb_r[39:36] = 4'hc;
      4'h1: r2_a_sb_r[39:36] = 4'ha;
      4'h2: r2_a_sb_r[39:36] = 4'hd;
      4'h3: r2_a_sb_r[39:36] = 4'h3;
      4'h4: r2_a_sb_r[39:36] = 4'he;
      4'h5: r2_a_sb_r[39:36] = 4'hb;
      4'h6: r2_a_sb_r[39:36] = 4'hf;
      4'h7: r2_a_sb_r[39:36] = 4'h7;
      4'h8: r2_a_sb_r[39:36] = 4'h8;
      4'h9: r2_a_sb_r[39:36] = 4'h9;
      4'ha: r2_a_sb_r[39:36] = 4'h1;
      4'hb: r2_a_sb_r[39:36] = 4'h5;
      4'hc: r2_a_sb_r[39:36] = 4'h0;
      4'hd: r2_a_sb_r[39:36] = 4'h2;
      4'he: r2_a_sb_r[39:36] = 4'h4;
      4'hf: r2_a_sb_r[39:36] = 4'h6;
    endcase
    case (st2[43:40])
      4'h0: r2_a_sb_r[43:40] = 4'hc;
      4'h1: r2_a_sb_r[43:40] = 4'ha;
      4'h2: r2_a_sb_r[43:40] = 4'hd;
      4'h3: r2_a_sb_r[43:40] = 4'h3;
      4'h4: r2_a_sb_r[43:40] = 4'he;
      4'h5: r2_a_sb_r[43:40] = 4'hb;
      4'h6: r2_a_sb_r[43:40] = 4'hf;
      4'h7: r2_a_sb_r[43:40] = 4'h7;
      4'h8: r2_a_sb_r[43:40] = 4'h8;
      4'h9: r2_a_sb_r[43:40] = 4'h9;
      4'ha: r2_a_sb_r[43:40] = 4'h1;
      4'hb: r2_a_sb_r[43:40] = 4'h5;
      4'hc: r2_a_sb_r[43:40] = 4'h0;
      4'hd: r2_a_sb_r[43:40] = 4'h2;
      4'he: r2_a_sb_r[43:40] = 4'h4;
      4'hf: r2_a_sb_r[43:40] = 4'h6;
    endcase
    case (st2[47:44])
      4'h0: r2_a_sb_r[47:44] = 4'hc;
      4'h1: r2_a_sb_r[47:44] = 4'ha;
      4'h2: r2_a_sb_r[47:44] = 4'hd;
      4'h3: r2_a_sb_r[47:44] = 4'h3;
      4'h4: r2_a_sb_r[47:44] = 4'he;
      4'h5: r2_a_sb_r[47:44] = 4'hb;
      4'h6: r2_a_sb_r[47:44] = 4'hf;
      4'h7: r2_a_sb_r[47:44] = 4'h7;
      4'h8: r2_a_sb_r[47:44] = 4'h8;
      4'h9: r2_a_sb_r[47:44] = 4'h9;
      4'ha: r2_a_sb_r[47:44] = 4'h1;
      4'hb: r2_a_sb_r[47:44] = 4'h5;
      4'hc: r2_a_sb_r[47:44] = 4'h0;
      4'hd: r2_a_sb_r[47:44] = 4'h2;
      4'he: r2_a_sb_r[47:44] = 4'h4;
      4'hf: r2_a_sb_r[47:44] = 4'h6;
    endcase
    case (st2[51:48])
      4'h0: r2_a_sb_r[51:48] = 4'hc;
      4'h1: r2_a_sb_r[51:48] = 4'ha;
      4'h2: r2_a_sb_r[51:48] = 4'hd;
      4'h3: r2_a_sb_r[51:48] = 4'h3;
      4'h4: r2_a_sb_r[51:48] = 4'he;
      4'h5: r2_a_sb_r[51:48] = 4'hb;
      4'h6: r2_a_sb_r[51:48] = 4'hf;
      4'h7: r2_a_sb_r[51:48] = 4'h7;
      4'h8: r2_a_sb_r[51:48] = 4'h8;
      4'h9: r2_a_sb_r[51:48] = 4'h9;
      4'ha: r2_a_sb_r[51:48] = 4'h1;
      4'hb: r2_a_sb_r[51:48] = 4'h5;
      4'hc: r2_a_sb_r[51:48] = 4'h0;
      4'hd: r2_a_sb_r[51:48] = 4'h2;
      4'he: r2_a_sb_r[51:48] = 4'h4;
      4'hf: r2_a_sb_r[51:48] = 4'h6;
    endcase
    case (st2[55:52])
      4'h0: r2_a_sb_r[55:52] = 4'hc;
      4'h1: r2_a_sb_r[55:52] = 4'ha;
      4'h2: r2_a_sb_r[55:52] = 4'hd;
      4'h3: r2_a_sb_r[55:52] = 4'h3;
      4'h4: r2_a_sb_r[55:52] = 4'he;
      4'h5: r2_a_sb_r[55:52] = 4'hb;
      4'h6: r2_a_sb_r[55:52] = 4'hf;
      4'h7: r2_a_sb_r[55:52] = 4'h7;
      4'h8: r2_a_sb_r[55:52] = 4'h8;
      4'h9: r2_a_sb_r[55:52] = 4'h9;
      4'ha: r2_a_sb_r[55:52] = 4'h1;
      4'hb: r2_a_sb_r[55:52] = 4'h5;
      4'hc: r2_a_sb_r[55:52] = 4'h0;
      4'hd: r2_a_sb_r[55:52] = 4'h2;
      4'he: r2_a_sb_r[55:52] = 4'h4;
      4'hf: r2_a_sb_r[55:52] = 4'h6;
    endcase
    case (st2[59:56])
      4'h0: r2_a_sb_r[59:56] = 4'hc;
      4'h1: r2_a_sb_r[59:56] = 4'ha;
      4'h2: r2_a_sb_r[59:56] = 4'hd;
      4'h3: r2_a_sb_r[59:56] = 4'h3;
      4'h4: r2_a_sb_r[59:56] = 4'he;
      4'h5: r2_a_sb_r[59:56] = 4'hb;
      4'h6: r2_a_sb_r[59:56] = 4'hf;
      4'h7: r2_a_sb_r[59:56] = 4'h7;
      4'h8: r2_a_sb_r[59:56] = 4'h8;
      4'h9: r2_a_sb_r[59:56] = 4'h9;
      4'ha: r2_a_sb_r[59:56] = 4'h1;
      4'hb: r2_a_sb_r[59:56] = 4'h5;
      4'hc: r2_a_sb_r[59:56] = 4'h0;
      4'hd: r2_a_sb_r[59:56] = 4'h2;
      4'he: r2_a_sb_r[59:56] = 4'h4;
      4'hf: r2_a_sb_r[59:56] = 4'h6;
    endcase
    case (st2[63:60])
      4'h0: r2_a_sb_r[63:60] = 4'hc;
      4'h1: r2_a_sb_r[63:60] = 4'ha;
      4'h2: r2_a_sb_r[63:60] = 4'hd;
      4'h3: r2_a_sb_r[63:60] = 4'h3;
      4'h4: r2_a_sb_r[63:60] = 4'he;
      4'h5: r2_a_sb_r[63:60] = 4'hb;
      4'h6: r2_a_sb_r[63:60] = 4'hf;
      4'h7: r2_a_sb_r[63:60] = 4'h7;
      4'h8: r2_a_sb_r[63:60] = 4'h8;
      4'h9: r2_a_sb_r[63:60] = 4'h9;
      4'ha: r2_a_sb_r[63:60] = 4'h1;
      4'hb: r2_a_sb_r[63:60] = 4'h5;
      4'hc: r2_a_sb_r[63:60] = 4'h0;
      4'hd: r2_a_sb_r[63:60] = 4'h2;
      4'he: r2_a_sb_r[63:60] = 4'h4;
      4'hf: r2_a_sb_r[63:60] = 4'h6;
    endcase
  end
  // Midori ShuffleCell
  wire [63:0] r2_b_sh = {r2_a_sb[35:32], r2_a_sb[11:8], r2_a_sb[55:52], r2_a_sb[31:28], r2_a_sb[27:24], r2_a_sb[51:48], r2_a_sb[15:12], r2_a_sb[39:36], r2_a_sb[7:4], r2_a_sb[47:44], r2_a_sb[19:16], r2_a_sb[59:56], r2_a_sb[63:60], r2_a_sb[23:20], r2_a_sb[43:40], r2_a_sb[3:0]};
  // Midori MixColumn
  wire [63:0] r2_c_mc;
  assign r2_c_mc[3:0] = r2_b_sh[19:16] ^ r2_b_sh[35:32] ^ r2_b_sh[51:48];
  assign r2_c_mc[19:16] = r2_b_sh[3:0] ^ r2_b_sh[35:32] ^ r2_b_sh[51:48];
  assign r2_c_mc[35:32] = r2_b_sh[3:0] ^ r2_b_sh[19:16] ^ r2_b_sh[51:48];
  assign r2_c_mc[51:48] = r2_b_sh[3:0] ^ r2_b_sh[19:16] ^ r2_b_sh[35:32];
  assign r2_c_mc[7:4] = r2_b_sh[23:20] ^ r2_b_sh[39:36] ^ r2_b_sh[55:52];
  assign r2_c_mc[23:20] = r2_b_sh[7:4] ^ r2_b_sh[39:36] ^ r2_b_sh[55:52];
  assign r2_c_mc[39:36] = r2_b_sh[7:4] ^ r2_b_sh[23:20] ^ r2_b_sh[55:52];
  assign r2_c_mc[55:52] = r2_b_sh[7:4] ^ r2_b_sh[23:20] ^ r2_b_sh[39:36];
  assign r2_c_mc[11:8] = r2_b_sh[27:24] ^ r2_b_sh[43:40] ^ r2_b_sh[59:56];
  assign r2_c_mc[27:24] = r2_b_sh[11:8] ^ r2_b_sh[43:40] ^ r2_b_sh[59:56];
  assign r2_c_mc[43:40] = r2_b_sh[11:8] ^ r2_b_sh[27:24] ^ r2_b_sh[59:56];
  assign r2_c_mc[59:56] = r2_b_sh[11:8] ^ r2_b_sh[27:24] ^ r2_b_sh[43:40];
  assign r2_c_mc[15:12] = r2_b_sh[31:28] ^ r2_b_sh[47:44] ^ r2_b_sh[63:60];
  assign r2_c_mc[31:28] = r2_b_sh[15:12] ^ r2_b_sh[47:44] ^ r2_b_sh[63:60];
  assign r2_c_mc[47:44] = r2_b_sh[15:12] ^ r2_b_sh[31:28] ^ r2_b_sh[63:60];
  assign r2_c_mc[63:60] = r2_b_sh[15:12] ^ r2_b_sh[31:28] ^ r2_b_sh[47:44];
  wire [63:0] st3 = r2_c_mc ^ 64'hdaa66d2c7ddf743f ^ {key[24:0], key[63:25]};
  reg [63:0] r3_a_sb_r;
  wire [63:0] r3_a_sb = r3_a_sb_r;
  always @(*) begin
    r3_a_sb_r = 64'h0;
    case (st3[3:0])
      4'h0: r3_a_sb_r[3:0] = 4'hc;
      4'h1: r3_a_sb_r[3:0] = 4'ha;
      4'h2: r3_a_sb_r[3:0] = 4'hd;
      4'h3: r3_a_sb_r[3:0] = 4'h3;
      4'h4: r3_a_sb_r[3:0] = 4'he;
      4'h5: r3_a_sb_r[3:0] = 4'hb;
      4'h6: r3_a_sb_r[3:0] = 4'hf;
      4'h7: r3_a_sb_r[3:0] = 4'h7;
      4'h8: r3_a_sb_r[3:0] = 4'h8;
      4'h9: r3_a_sb_r[3:0] = 4'h9;
      4'ha: r3_a_sb_r[3:0] = 4'h1;
      4'hb: r3_a_sb_r[3:0] = 4'h5;
      4'hc: r3_a_sb_r[3:0] = 4'h0;
      4'hd: r3_a_sb_r[3:0] = 4'h2;
      4'he: r3_a_sb_r[3:0] = 4'h4;
      4'hf: r3_a_sb_r[3:0] = 4'h6;
    endcase
    case (st3[7:4])
      4'h0: r3_a_sb_r[7:4] = 4'hc;
      4'h1: r3_a_sb_r[7:4] = 4'ha;
      4'h2: r3_a_sb_r[7:4] = 4'hd;
      4'h3: r3_a_sb_r[7:4] = 4'h3;
      4'h4: r3_a_sb_r[7:4] = 4'he;
      4'h5: r3_a_sb_r[7:4] = 4'hb;
      4'h6: r3_a_sb_r[7:4] = 4'hf;
      4'h7: r3_a_sb_r[7:4] = 4'h7;
      4'h8: r3_a_sb_r[7:4] = 4'h8;
      4'h9: r3_a_sb_r[7:4] = 4'h9;
      4'ha: r3_a_sb_r[7:4] = 4'h1;
      4'hb: r3_a_sb_r[7:4] = 4'h5;
      4'hc: r3_a_sb_r[7:4] = 4'h0;
      4'hd: r3_a_sb_r[7:4] = 4'h2;
      4'he: r3_a_sb_r[7:4] = 4'h4;
      4'hf: r3_a_sb_r[7:4] = 4'h6;
    endcase
    case (st3[11:8])
      4'h0: r3_a_sb_r[11:8] = 4'hc;
      4'h1: r3_a_sb_r[11:8] = 4'ha;
      4'h2: r3_a_sb_r[11:8] = 4'hd;
      4'h3: r3_a_sb_r[11:8] = 4'h3;
      4'h4: r3_a_sb_r[11:8] = 4'he;
      4'h5: r3_a_sb_r[11:8] = 4'hb;
      4'h6: r3_a_sb_r[11:8] = 4'hf;
      4'h7: r3_a_sb_r[11:8] = 4'h7;
      4'h8: r3_a_sb_r[11:8] = 4'h8;
      4'h9: r3_a_sb_r[11:8] = 4'h9;
      4'ha: r3_a_sb_r[11:8] = 4'h1;
      4'hb: r3_a_sb_r[11:8] = 4'h5;
      4'hc: r3_a_sb_r[11:8] = 4'h0;
      4'hd: r3_a_sb_r[11:8] = 4'h2;
      4'he: r3_a_sb_r[11:8] = 4'h4;
      4'hf: r3_a_sb_r[11:8] = 4'h6;
    endcase
    case (st3[15:12])
      4'h0: r3_a_sb_r[15:12] = 4'hc;
      4'h1: r3_a_sb_r[15:12] = 4'ha;
      4'h2: r3_a_sb_r[15:12] = 4'hd;
      4'h3: r3_a_sb_r[15:12] = 4'h3;
      4'h4: r3_a_sb_r[15:12] = 4'he;
      4'h5: r3_a_sb_r[15:12] = 4'hb;
      4'h6: r3_a_sb_r[15:12] = 4'hf;
      4'h7: r3_a_sb_r[15:12] = 4'h7;
      4'h8: r3_a_sb_r[15:12] = 4'h8;
      4'h9: r3_a_sb_r[15:12] = 4'h9;
      4'ha: r3_a_sb_r[15:12] = 4'h1;
      4'hb: r3_a_sb_r[15:12] = 4'h5;
      4'hc: r3_a_sb_r[15:12] = 4'h0;
      4'hd: r3_a_sb_r[15:12] = 4'h2;
      4'he: r3_a_sb_r[15:12] = 4'h4;
      4'hf: r3_a_sb_r[15:12] = 4'h6;
    endcase
    case (st3[19:16])
      4'h0: r3_a_sb_r[19:16] = 4'hc;
      4'h1: r3_a_sb_r[19:16] = 4'ha;
      4'h2: r3_a_sb_r[19:16] = 4'hd;
      4'h3: r3_a_sb_r[19:16] = 4'h3;
      4'h4: r3_a_sb_r[19:16] = 4'he;
      4'h5: r3_a_sb_r[19:16] = 4'hb;
      4'h6: r3_a_sb_r[19:16] = 4'hf;
      4'h7: r3_a_sb_r[19:16] = 4'h7;
      4'h8: r3_a_sb_r[19:16] = 4'h8;
      4'h9: r3_a_sb_r[19:16] = 4'h9;
      4'ha: r3_a_sb_r[19:16] = 4'h1;
      4'hb: r3_a_sb_r[19:16] = 4'h5;
      4'hc: r3_a_sb_r[19:16] = 4'h0;
      4'hd: r3_a_sb_r[19:16] = 4'h2;
      4'he: r3_a_sb_r[19:16] = 4'h4;
      4'hf: r3_a_sb_r[19:16] = 4'h6;
    endcase
    case (st3[23:20])
      4'h0: r3_a_sb_r[23:20] = 4'hc;
      4'h1: r3_a_sb_r[23:20] = 4'ha;
      4'h2: r3_a_sb_r[23:20] = 4'hd;
      4'h3: r3_a_sb_r[23:20] = 4'h3;
      4'h4: r3_a_sb_r[23:20] = 4'he;
      4'h5: r3_a_sb_r[23:20] = 4'hb;
      4'h6: r3_a_sb_r[23:20] = 4'hf;
      4'h7: r3_a_sb_r[23:20] = 4'h7;
      4'h8: r3_a_sb_r[23:20] = 4'h8;
      4'h9: r3_a_sb_r[23:20] = 4'h9;
      4'ha: r3_a_sb_r[23:20] = 4'h1;
      4'hb: r3_a_sb_r[23:20] = 4'h5;
      4'hc: r3_a_sb_r[23:20] = 4'h0;
      4'hd: r3_a_sb_r[23:20] = 4'h2;
      4'he: r3_a_sb_r[23:20] = 4'h4;
      4'hf: r3_a_sb_r[23:20] = 4'h6;
    endcase
    case (st3[27:24])
      4'h0: r3_a_sb_r[27:24] = 4'hc;
      4'h1: r3_a_sb_r[27:24] = 4'ha;
      4'h2: r3_a_sb_r[27:24] = 4'hd;
      4'h3: r3_a_sb_r[27:24] = 4'h3;
      4'h4: r3_a_sb_r[27:24] = 4'he;
      4'h5: r3_a_sb_r[27:24] = 4'hb;
      4'h6: r3_a_sb_r[27:24] = 4'hf;
      4'h7: r3_a_sb_r[27:24] = 4'h7;
      4'h8: r3_a_sb_r[27:24] = 4'h8;
      4'h9: r3_a_sb_r[27:24] = 4'h9;
      4'ha: r3_a_sb_r[27:24] = 4'h1;
      4'hb: r3_a_sb_r[27:24] = 4'h5;
      4'hc: r3_a_sb_r[27:24] = 4'h0;
      4'hd: r3_a_sb_r[27:24] = 4'h2;
      4'he: r3_a_sb_r[27:24] = 4'h4;
      4'hf: r3_a_sb_r[27:24] = 4'h6;
    endcase
    case (st3[31:28])
      4'h0: r3_a_sb_r[31:28] = 4'hc;
      4'h1: r3_a_sb_r[31:28] = 4'ha;
      4'h2: r3_a_sb_r[31:28] = 4'hd;
      4'h3: r3_a_sb_r[31:28] = 4'h3;
      4'h4: r3_a_sb_r[31:28] = 4'he;
      4'h5: r3_a_sb_r[31:28] = 4'hb;
      4'h6: r3_a_sb_r[31:28] = 4'hf;
      4'h7: r3_a_sb_r[31:28] = 4'h7;
      4'h8: r3_a_sb_r[31:28] = 4'h8;
      4'h9: r3_a_sb_r[31:28] = 4'h9;
      4'ha: r3_a_sb_r[31:28] = 4'h1;
      4'hb: r3_a_sb_r[31:28] = 4'h5;
      4'hc: r3_a_sb_r[31:28] = 4'h0;
      4'hd: r3_a_sb_r[31:28] = 4'h2;
      4'he: r3_a_sb_r[31:28] = 4'h4;
      4'hf: r3_a_sb_r[31:28] = 4'h6;
    endcase
    case (st3[35:32])
      4'h0: r3_a_sb_r[35:32] = 4'hc;
      4'h1: r3_a_sb_r[35:32] = 4'ha;
      4'h2: r3_a_sb_r[35:32] = 4'hd;
      4'h3: r3_a_sb_r[35:32] = 4'h3;
      4'h4: r3_a_sb_r[35:32] = 4'he;
      4'h5: r3_a_sb_r[35:32] = 4'hb;
      4'h6: r3_a_sb_r[35:32] = 4'hf;
      4'h7: r3_a_sb_r[35:32] = 4'h7;
      4'h8: r3_a_sb_r[35:32] = 4'h8;
      4'h9: r3_a_sb_r[35:32] = 4'h9;
      4'ha: r3_a_sb_r[35:32] = 4'h1;
      4'hb: r3_a_sb_r[35:32] = 4'h5;
      4'hc: r3_a_sb_r[35:32] = 4'h0;
      4'hd: r3_a_sb_r[35:32] = 4'h2;
      4'he: r3_a_sb_r[35:32] = 4'h4;
      4'hf: r3_a_sb_r[35:32] = 4'h6;
    endcase
    case (st3[39:36])
      4'h0: r3_a_sb_r[39:36] = 4'hc;
      4'h1: r3_a_sb_r[39:36] = 4'ha;
      4'h2: r3_a_sb_r[39:36] = 4'hd;
      4'h3: r3_a_sb_r[39:36] = 4'h3;
      4'h4: r3_a_sb_r[39:36] = 4'he;
      4'h5: r3_a_sb_r[39:36] = 4'hb;
      4'h6: r3_a_sb_r[39:36] = 4'hf;
      4'h7: r3_a_sb_r[39:36] = 4'h7;
      4'h8: r3_a_sb_r[39:36] = 4'h8;
      4'h9: r3_a_sb_r[39:36] = 4'h9;
      4'ha: r3_a_sb_r[39:36] = 4'h1;
      4'hb: r3_a_sb_r[39:36] = 4'h5;
      4'hc: r3_a_sb_r[39:36] = 4'h0;
      4'hd: r3_a_sb_r[39:36] = 4'h2;
      4'he: r3_a_sb_r[39:36] = 4'h4;
      4'hf: r3_a_sb_r[39:36] = 4'h6;
    endcase
    case (st3[43:40])
      4'h0: r3_a_sb_r[43:40] = 4'hc;
      4'h1: r3_a_sb_r[43:40] = 4'ha;
      4'h2: r3_a_sb_r[43:40] = 4'hd;
      4'h3: r3_a_sb_r[43:40] = 4'h3;
      4'h4: r3_a_sb_r[43:40] = 4'he;
      4'h5: r3_a_sb_r[43:40] = 4'hb;
      4'h6: r3_a_sb_r[43:40] = 4'hf;
      4'h7: r3_a_sb_r[43:40] = 4'h7;
      4'h8: r3_a_sb_r[43:40] = 4'h8;
      4'h9: r3_a_sb_r[43:40] = 4'h9;
      4'ha: r3_a_sb_r[43:40] = 4'h1;
      4'hb: r3_a_sb_r[43:40] = 4'h5;
      4'hc: r3_a_sb_r[43:40] = 4'h0;
      4'hd: r3_a_sb_r[43:40] = 4'h2;
      4'he: r3_a_sb_r[43:40] = 4'h4;
      4'hf: r3_a_sb_r[43:40] = 4'h6;
    endcase
    case (st3[47:44])
      4'h0: r3_a_sb_r[47:44] = 4'hc;
      4'h1: r3_a_sb_r[47:44] = 4'ha;
      4'h2: r3_a_sb_r[47:44] = 4'hd;
      4'h3: r3_a_sb_r[47:44] = 4'h3;
      4'h4: r3_a_sb_r[47:44] = 4'he;
      4'h5: r3_a_sb_r[47:44] = 4'hb;
      4'h6: r3_a_sb_r[47:44] = 4'hf;
      4'h7: r3_a_sb_r[47:44] = 4'h7;
      4'h8: r3_a_sb_r[47:44] = 4'h8;
      4'h9: r3_a_sb_r[47:44] = 4'h9;
      4'ha: r3_a_sb_r[47:44] = 4'h1;
      4'hb: r3_a_sb_r[47:44] = 4'h5;
      4'hc: r3_a_sb_r[47:44] = 4'h0;
      4'hd: r3_a_sb_r[47:44] = 4'h2;
      4'he: r3_a_sb_r[47:44] = 4'h4;
      4'hf: r3_a_sb_r[47:44] = 4'h6;
    endcase
    case (st3[51:48])
      4'h0: r3_a_sb_r[51:48] = 4'hc;
      4'h1: r3_a_sb_r[51:48] = 4'ha;
      4'h2: r3_a_sb_r[51:48] = 4'hd;
      4'h3: r3_a_sb_r[51:48] = 4'h3;
      4'h4: r3_a_sb_r[51:48] = 4'he;
      4'h5: r3_a_sb_r[51:48] = 4'hb;
      4'h6: r3_a_sb_r[51:48] = 4'hf;
      4'h7: r3_a_sb_r[51:48] = 4'h7;
      4'h8: r3_a_sb_r[51:48] = 4'h8;
      4'h9: r3_a_sb_r[51:48] = 4'h9;
      4'ha: r3_a_sb_r[51:48] = 4'h1;
      4'hb: r3_a_sb_r[51:48] = 4'h5;
      4'hc: r3_a_sb_r[51:48] = 4'h0;
      4'hd: r3_a_sb_r[51:48] = 4'h2;
      4'he: r3_a_sb_r[51:48] = 4'h4;
      4'hf: r3_a_sb_r[51:48] = 4'h6;
    endcase
    case (st3[55:52])
      4'h0: r3_a_sb_r[55:52] = 4'hc;
      4'h1: r3_a_sb_r[55:52] = 4'ha;
      4'h2: r3_a_sb_r[55:52] = 4'hd;
      4'h3: r3_a_sb_r[55:52] = 4'h3;
      4'h4: r3_a_sb_r[55:52] = 4'he;
      4'h5: r3_a_sb_r[55:52] = 4'hb;
      4'h6: r3_a_sb_r[55:52] = 4'hf;
      4'h7: r3_a_sb_r[55:52] = 4'h7;
      4'h8: r3_a_sb_r[55:52] = 4'h8;
      4'h9: r3_a_sb_r[55:52] = 4'h9;
      4'ha: r3_a_sb_r[55:52] = 4'h1;
      4'hb: r3_a_sb_r[55:52] = 4'h5;
      4'hc: r3_a_sb_r[55:52] = 4'h0;
      4'hd: r3_a_sb_r[55:52] = 4'h2;
      4'he: r3_a_sb_r[55:52] = 4'h4;
      4'hf: r3_a_sb_r[55:52] = 4'h6;
    endcase
    case (st3[59:56])
      4'h0: r3_a_sb_r[59:56] = 4'hc;
      4'h1: r3_a_sb_r[59:56] = 4'ha;
      4'h2: r3_a_sb_r[59:56] = 4'hd;
      4'h3: r3_a_sb_r[59:56] = 4'h3;
      4'h4: r3_a_sb_r[59:56] = 4'he;
      4'h5: r3_a_sb_r[59:56] = 4'hb;
      4'h6: r3_a_sb_r[59:56] = 4'hf;
      4'h7: r3_a_sb_r[59:56] = 4'h7;
      4'h8: r3_a_sb_r[59:56] = 4'h8;
      4'h9: r3_a_sb_r[59:56] = 4'h9;
      4'ha: r3_a_sb_r[59:56] = 4'h1;
      4'hb: r3_a_sb_r[59:56] = 4'h5;
      4'hc: r3_a_sb_r[59:56] = 4'h0;
      4'hd: r3_a_sb_r[59:56] = 4'h2;
      4'he: r3_a_sb_r[59:56] = 4'h4;
      4'hf: r3_a_sb_r[59:56] = 4'h6;
    endcase
    case (st3[63:60])
      4'h0: r3_a_sb_r[63:60] = 4'hc;
      4'h1: r3_a_sb_r[63:60] = 4'ha;
      4'h2: r3_a_sb_r[63:60] = 4'hd;
      4'h3: r3_a_sb_r[63:60] = 4'h3;
      4'h4: r3_a_sb_r[63:60] = 4'he;
      4'h5: r3_a_sb_r[63:60] = 4'hb;
      4'h6: r3_a_sb_r[63:60] = 4'hf;
      4'h7: r3_a_sb_r[63:60] = 4'h7;
      4'h8: r3_a_sb_r[63:60] = 4'h8;
      4'h9: r3_a_sb_r[63:60] = 4'h9;
      4'ha: r3_a_sb_r[63:60] = 4'h1;
      4'hb: r3_a_sb_r[63:60] = 4'h5;
      4'hc: r3_a_sb_r[63:60] = 4'h0;
      4'hd: r3_a_sb_r[63:60] = 4'h2;
      4'he: r3_a_sb_r[63:60] = 4'h4;
      4'hf: r3_a_sb_r[63:60] = 4'h6;
    endcase
  end
  // Midori ShuffleCell
  wire [63:0] r3_b_sh = {r3_a_sb[35:32], r3_a_sb[11:8], r3_a_sb[55:52], r3_a_sb[31:28], r3_a_sb[27:24], r3_a_sb[51:48], r3_a_sb[15:12], r3_a_sb[39:36], r3_a_sb[7:4], r3_a_sb[47:44], r3_a_sb[19:16], r3_a_sb[59:56], r3_a_sb[63:60], r3_a_sb[23:20], r3_a_sb[43:40], r3_a_sb[3:0]};
  // Midori MixColumn
  wire [63:0] r3_c_mc;
  assign r3_c_mc[3:0] = r3_b_sh[19:16] ^ r3_b_sh[35:32] ^ r3_b_sh[51:48];
  assign r3_c_mc[19:16] = r3_b_sh[3:0] ^ r3_b_sh[35:32] ^ r3_b_sh[51:48];
  assign r3_c_mc[35:32] = r3_b_sh[3:0] ^ r3_b_sh[19:16] ^ r3_b_sh[51:48];
  assign r3_c_mc[51:48] = r3_b_sh[3:0] ^ r3_b_sh[19:16] ^ r3_b_sh[35:32];
  assign r3_c_mc[7:4] = r3_b_sh[23:20] ^ r3_b_sh[39:36] ^ r3_b_sh[55:52];
  assign r3_c_mc[23:20] = r3_b_sh[7:4] ^ r3_b_sh[39:36] ^ r3_b_sh[55:52];
  assign r3_c_mc[39:36] = r3_b_sh[7:4] ^ r3_b_sh[23:20] ^ r3_b_sh[55:52];
  assign r3_c_mc[55:52] = r3_b_sh[7:4] ^ r3_b_sh[23:20] ^ r3_b_sh[39:36];
  assign r3_c_mc[11:8] = r3_b_sh[27:24] ^ r3_b_sh[43:40] ^ r3_b_sh[59:56];
  assign r3_c_mc[27:24] = r3_b_sh[11:8] ^ r3_b_sh[43:40] ^ r3_b_sh[59:56];
  assign r3_c_mc[43:40] = r3_b_sh[11:8] ^ r3_b_sh[27:24] ^ r3_b_sh[59:56];
  assign r3_c_mc[59:56] = r3_b_sh[11:8] ^ r3_b_sh[27:24] ^ r3_b_sh[43:40];
  assign r3_c_mc[15:12] = r3_b_sh[31:28] ^ r3_b_sh[47:44] ^ r3_b_sh[63:60];
  assign r3_c_mc[31:28] = r3_b_sh[15:12] ^ r3_b_sh[47:44] ^ r3_b_sh[63:60];
  assign r3_c_mc[47:44] = r3_b_sh[15:12] ^ r3_b_sh[31:28] ^ r3_b_sh[63:60];
  assign r3_c_mc[63:60] = r3_b_sh[15:12] ^ r3_b_sh[31:28] ^ r3_b_sh[47:44];
  wire [63:0] st4 = r3_c_mc ^ 64'h78dde6e5fd29f054 ^ {key[11:0], key[63:12]};
  reg [63:0] r4_a_sb_r;
  wire [63:0] r4_a_sb = r4_a_sb_r;
  always @(*) begin
    r4_a_sb_r = 64'h0;
    case (st4[3:0])
      4'h0: r4_a_sb_r[3:0] = 4'hc;
      4'h1: r4_a_sb_r[3:0] = 4'ha;
      4'h2: r4_a_sb_r[3:0] = 4'hd;
      4'h3: r4_a_sb_r[3:0] = 4'h3;
      4'h4: r4_a_sb_r[3:0] = 4'he;
      4'h5: r4_a_sb_r[3:0] = 4'hb;
      4'h6: r4_a_sb_r[3:0] = 4'hf;
      4'h7: r4_a_sb_r[3:0] = 4'h7;
      4'h8: r4_a_sb_r[3:0] = 4'h8;
      4'h9: r4_a_sb_r[3:0] = 4'h9;
      4'ha: r4_a_sb_r[3:0] = 4'h1;
      4'hb: r4_a_sb_r[3:0] = 4'h5;
      4'hc: r4_a_sb_r[3:0] = 4'h0;
      4'hd: r4_a_sb_r[3:0] = 4'h2;
      4'he: r4_a_sb_r[3:0] = 4'h4;
      4'hf: r4_a_sb_r[3:0] = 4'h6;
    endcase
    case (st4[7:4])
      4'h0: r4_a_sb_r[7:4] = 4'hc;
      4'h1: r4_a_sb_r[7:4] = 4'ha;
      4'h2: r4_a_sb_r[7:4] = 4'hd;
      4'h3: r4_a_sb_r[7:4] = 4'h3;
      4'h4: r4_a_sb_r[7:4] = 4'he;
      4'h5: r4_a_sb_r[7:4] = 4'hb;
      4'h6: r4_a_sb_r[7:4] = 4'hf;
      4'h7: r4_a_sb_r[7:4] = 4'h7;
      4'h8: r4_a_sb_r[7:4] = 4'h8;
      4'h9: r4_a_sb_r[7:4] = 4'h9;
      4'ha: r4_a_sb_r[7:4] = 4'h1;
      4'hb: r4_a_sb_r[7:4] = 4'h5;
      4'hc: r4_a_sb_r[7:4] = 4'h0;
      4'hd: r4_a_sb_r[7:4] = 4'h2;
      4'he: r4_a_sb_r[7:4] = 4'h4;
      4'hf: r4_a_sb_r[7:4] = 4'h6;
    endcase
    case (st4[11:8])
      4'h0: r4_a_sb_r[11:8] = 4'hc;
      4'h1: r4_a_sb_r[11:8] = 4'ha;
      4'h2: r4_a_sb_r[11:8] = 4'hd;
      4'h3: r4_a_sb_r[11:8] = 4'h3;
      4'h4: r4_a_sb_r[11:8] = 4'he;
      4'h5: r4_a_sb_r[11:8] = 4'hb;
      4'h6: r4_a_sb_r[11:8] = 4'hf;
      4'h7: r4_a_sb_r[11:8] = 4'h7;
      4'h8: r4_a_sb_r[11:8] = 4'h8;
      4'h9: r4_a_sb_r[11:8] = 4'h9;
      4'ha: r4_a_sb_r[11:8] = 4'h1;
      4'hb: r4_a_sb_r[11:8] = 4'h5;
      4'hc: r4_a_sb_r[11:8] = 4'h0;
      4'hd: r4_a_sb_r[11:8] = 4'h2;
      4'he: r4_a_sb_r[11:8] = 4'h4;
      4'hf: r4_a_sb_r[11:8] = 4'h6;
    endcase
    case (st4[15:12])
      4'h0: r4_a_sb_r[15:12] = 4'hc;
      4'h1: r4_a_sb_r[15:12] = 4'ha;
      4'h2: r4_a_sb_r[15:12] = 4'hd;
      4'h3: r4_a_sb_r[15:12] = 4'h3;
      4'h4: r4_a_sb_r[15:12] = 4'he;
      4'h5: r4_a_sb_r[15:12] = 4'hb;
      4'h6: r4_a_sb_r[15:12] = 4'hf;
      4'h7: r4_a_sb_r[15:12] = 4'h7;
      4'h8: r4_a_sb_r[15:12] = 4'h8;
      4'h9: r4_a_sb_r[15:12] = 4'h9;
      4'ha: r4_a_sb_r[15:12] = 4'h1;
      4'hb: r4_a_sb_r[15:12] = 4'h5;
      4'hc: r4_a_sb_r[15:12] = 4'h0;
      4'hd: r4_a_sb_r[15:12] = 4'h2;
      4'he: r4_a_sb_r[15:12] = 4'h4;
      4'hf: r4_a_sb_r[15:12] = 4'h6;
    endcase
    case (st4[19:16])
      4'h0: r4_a_sb_r[19:16] = 4'hc;
      4'h1: r4_a_sb_r[19:16] = 4'ha;
      4'h2: r4_a_sb_r[19:16] = 4'hd;
      4'h3: r4_a_sb_r[19:16] = 4'h3;
      4'h4: r4_a_sb_r[19:16] = 4'he;
      4'h5: r4_a_sb_r[19:16] = 4'hb;
      4'h6: r4_a_sb_r[19:16] = 4'hf;
      4'h7: r4_a_sb_r[19:16] = 4'h7;
      4'h8: r4_a_sb_r[19:16] = 4'h8;
      4'h9: r4_a_sb_r[19:16] = 4'h9;
      4'ha: r4_a_sb_r[19:16] = 4'h1;
      4'hb: r4_a_sb_r[19:16] = 4'h5;
      4'hc: r4_a_sb_r[19:16] = 4'h0;
      4'hd: r4_a_sb_r[19:16] = 4'h2;
      4'he: r4_a_sb_r[19:16] = 4'h4;
      4'hf: r4_a_sb_r[19:16] = 4'h6;
    endcase
    case (st4[23:20])
      4'h0: r4_a_sb_r[23:20] = 4'hc;
      4'h1: r4_a_sb_r[23:20] = 4'ha;
      4'h2: r4_a_sb_r[23:20] = 4'hd;
      4'h3: r4_a_sb_r[23:20] = 4'h3;
      4'h4: r4_a_sb_r[23:20] = 4'he;
      4'h5: r4_a_sb_r[23:20] = 4'hb;
      4'h6: r4_a_sb_r[23:20] = 4'hf;
      4'h7: r4_a_sb_r[23:20] = 4'h7;
      4'h8: r4_a_sb_r[23:20] = 4'h8;
      4'h9: r4_a_sb_r[23:20] = 4'h9;
      4'ha: r4_a_sb_r[23:20] = 4'h1;
      4'hb: r4_a_sb_r[23:20] = 4'h5;
      4'hc: r4_a_sb_r[23:20] = 4'h0;
      4'hd: r4_a_sb_r[23:20] = 4'h2;
      4'he: r4_a_sb_r[23:20] = 4'h4;
      4'hf: r4_a_sb_r[23:20] = 4'h6;
    endcase
    case (st4[27:24])
      4'h0: r4_a_sb_r[27:24] = 4'hc;
      4'h1: r4_a_sb_r[27:24] = 4'ha;
      4'h2: r4_a_sb_r[27:24] = 4'hd;
      4'h3: r4_a_sb_r[27:24] = 4'h3;
      4'h4: r4_a_sb_r[27:24] = 4'he;
      4'h5: r4_a_sb_r[27:24] = 4'hb;
      4'h6: r4_a_sb_r[27:24] = 4'hf;
      4'h7: r4_a_sb_r[27:24] = 4'h7;
      4'h8: r4_a_sb_r[27:24] = 4'h8;
      4'h9: r4_a_sb_r[27:24] = 4'h9;
      4'ha: r4_a_sb_r[27:24] = 4'h1;
      4'hb: r4_a_sb_r[27:24] = 4'h5;
      4'hc: r4_a_sb_r[27:24] = 4'h0;
      4'hd: r4_a_sb_r[27:24] = 4'h2;
      4'he: r4_a_sb_r[27:24] = 4'h4;
      4'hf: r4_a_sb_r[27:24] = 4'h6;
    endcase
    case (st4[31:28])
      4'h0: r4_a_sb_r[31:28] = 4'hc;
      4'h1: r4_a_sb_r[31:28] = 4'ha;
      4'h2: r4_a_sb_r[31:28] = 4'hd;
      4'h3: r4_a_sb_r[31:28] = 4'h3;
      4'h4: r4_a_sb_r[31:28] = 4'he;
      4'h5: r4_a_sb_r[31:28] = 4'hb;
      4'h6: r4_a_sb_r[31:28] = 4'hf;
      4'h7: r4_a_sb_r[31:28] = 4'h7;
      4'h8: r4_a_sb_r[31:28] = 4'h8;
      4'h9: r4_a_sb_r[31:28] = 4'h9;
      4'ha: r4_a_sb_r[31:28] = 4'h1;
      4'hb: r4_a_sb_r[31:28] = 4'h5;
      4'hc: r4_a_sb_r[31:28] = 4'h0;
      4'hd: r4_a_sb_r[31:28] = 4'h2;
      4'he: r4_a_sb_r[31:28] = 4'h4;
      4'hf: r4_a_sb_r[31:28] = 4'h6;
    endcase
    case (st4[35:32])
      4'h0: r4_a_sb_r[35:32] = 4'hc;
      4'h1: r4_a_sb_r[35:32] = 4'ha;
      4'h2: r4_a_sb_r[35:32] = 4'hd;
      4'h3: r4_a_sb_r[35:32] = 4'h3;
      4'h4: r4_a_sb_r[35:32] = 4'he;
      4'h5: r4_a_sb_r[35:32] = 4'hb;
      4'h6: r4_a_sb_r[35:32] = 4'hf;
      4'h7: r4_a_sb_r[35:32] = 4'h7;
      4'h8: r4_a_sb_r[35:32] = 4'h8;
      4'h9: r4_a_sb_r[35:32] = 4'h9;
      4'ha: r4_a_sb_r[35:32] = 4'h1;
      4'hb: r4_a_sb_r[35:32] = 4'h5;
      4'hc: r4_a_sb_r[35:32] = 4'h0;
      4'hd: r4_a_sb_r[35:32] = 4'h2;
      4'he: r4_a_sb_r[35:32] = 4'h4;
      4'hf: r4_a_sb_r[35:32] = 4'h6;
    endcase
    case (st4[39:36])
      4'h0: r4_a_sb_r[39:36] = 4'hc;
      4'h1: r4_a_sb_r[39:36] = 4'ha;
      4'h2: r4_a_sb_r[39:36] = 4'hd;
      4'h3: r4_a_sb_r[39:36] = 4'h3;
      4'h4: r4_a_sb_r[39:36] = 4'he;
      4'h5: r4_a_sb_r[39:36] = 4'hb;
      4'h6: r4_a_sb_r[39:36] = 4'hf;
      4'h7: r4_a_sb_r[39:36] = 4'h7;
      4'h8: r4_a_sb_r[39:36] = 4'h8;
      4'h9: r4_a_sb_r[39:36] = 4'h9;
      4'ha: r4_a_sb_r[39:36] = 4'h1;
      4'hb: r4_a_sb_r[39:36] = 4'h5;
      4'hc: r4_a_sb_r[39:36] = 4'h0;
      4'hd: r4_a_sb_r[39:36] = 4'h2;
      4'he: r4_a_sb_r[39:36] = 4'h4;
      4'hf: r4_a_sb_r[39:36] = 4'h6;
    endcase
    case (st4[43:40])
      4'h0: r4_a_sb_r[43:40] = 4'hc;
      4'h1: r4_a_sb_r[43:40] = 4'ha;
      4'h2: r4_a_sb_r[43:40] = 4'hd;
      4'h3: r4_a_sb_r[43:40] = 4'h3;
      4'h4: r4_a_sb_r[43:40] = 4'he;
      4'h5: r4_a_sb_r[43:40] = 4'hb;
      4'h6: r4_a_sb_r[43:40] = 4'hf;
      4'h7: r4_a_sb_r[43:40] = 4'h7;
      4'h8: r4_a_sb_r[43:40] = 4'h8;
      4'h9: r4_a_sb_r[43:40] = 4'h9;
      4'ha: r4_a_sb_r[43:40] = 4'h1;
      4'hb: r4_a_sb_r[43:40] = 4'h5;
      4'hc: r4_a_sb_r[43:40] = 4'h0;
      4'hd: r4_a_sb_r[43:40] = 4'h2;
      4'he: r4_a_sb_r[43:40] = 4'h4;
      4'hf: r4_a_sb_r[43:40] = 4'h6;
    endcase
    case (st4[47:44])
      4'h0: r4_a_sb_r[47:44] = 4'hc;
      4'h1: r4_a_sb_r[47:44] = 4'ha;
      4'h2: r4_a_sb_r[47:44] = 4'hd;
      4'h3: r4_a_sb_r[47:44] = 4'h3;
      4'h4: r4_a_sb_r[47:44] = 4'he;
      4'h5: r4_a_sb_r[47:44] = 4'hb;
      4'h6: r4_a_sb_r[47:44] = 4'hf;
      4'h7: r4_a_sb_r[47:44] = 4'h7;
      4'h8: r4_a_sb_r[47:44] = 4'h8;
      4'h9: r4_a_sb_r[47:44] = 4'h9;
      4'ha: r4_a_sb_r[47:44] = 4'h1;
      4'hb: r4_a_sb_r[47:44] = 4'h5;
      4'hc: r4_a_sb_r[47:44] = 4'h0;
      4'hd: r4_a_sb_r[47:44] = 4'h2;
      4'he: r4_a_sb_r[47:44] = 4'h4;
      4'hf: r4_a_sb_r[47:44] = 4'h6;
    endcase
    case (st4[51:48])
      4'h0: r4_a_sb_r[51:48] = 4'hc;
      4'h1: r4_a_sb_r[51:48] = 4'ha;
      4'h2: r4_a_sb_r[51:48] = 4'hd;
      4'h3: r4_a_sb_r[51:48] = 4'h3;
      4'h4: r4_a_sb_r[51:48] = 4'he;
      4'h5: r4_a_sb_r[51:48] = 4'hb;
      4'h6: r4_a_sb_r[51:48] = 4'hf;
      4'h7: r4_a_sb_r[51:48] = 4'h7;
      4'h8: r4_a_sb_r[51:48] = 4'h8;
      4'h9: r4_a_sb_r[51:48] = 4'h9;
      4'ha: r4_a_sb_r[51:48] = 4'h1;
      4'hb: r4_a_sb_r[51:48] = 4'h5;
      4'hc: r4_a_sb_r[51:48] = 4'h0;
      4'hd: r4_a_sb_r[51:48] = 4'h2;
      4'he: r4_a_sb_r[51:48] = 4'h4;
      4'hf: r4_a_sb_r[51:48] = 4'h6;
    endcase
    case (st4[55:52])
      4'h0: r4_a_sb_r[55:52] = 4'hc;
      4'h1: r4_a_sb_r[55:52] = 4'ha;
      4'h2: r4_a_sb_r[55:52] = 4'hd;
      4'h3: r4_a_sb_r[55:52] = 4'h3;
      4'h4: r4_a_sb_r[55:52] = 4'he;
      4'h5: r4_a_sb_r[55:52] = 4'hb;
      4'h6: r4_a_sb_r[55:52] = 4'hf;
      4'h7: r4_a_sb_r[55:52] = 4'h7;
      4'h8: r4_a_sb_r[55:52] = 4'h8;
      4'h9: r4_a_sb_r[55:52] = 4'h9;
      4'ha: r4_a_sb_r[55:52] = 4'h1;
      4'hb: r4_a_sb_r[55:52] = 4'h5;
      4'hc: r4_a_sb_r[55:52] = 4'h0;
      4'hd: r4_a_sb_r[55:52] = 4'h2;
      4'he: r4_a_sb_r[55:52] = 4'h4;
      4'hf: r4_a_sb_r[55:52] = 4'h6;
    endcase
    case (st4[59:56])
      4'h0: r4_a_sb_r[59:56] = 4'hc;
      4'h1: r4_a_sb_r[59:56] = 4'ha;
      4'h2: r4_a_sb_r[59:56] = 4'hd;
      4'h3: r4_a_sb_r[59:56] = 4'h3;
      4'h4: r4_a_sb_r[59:56] = 4'he;
      4'h5: r4_a_sb_r[59:56] = 4'hb;
      4'h6: r4_a_sb_r[59:56] = 4'hf;
      4'h7: r4_a_sb_r[59:56] = 4'h7;
      4'h8: r4_a_sb_r[59:56] = 4'h8;
      4'h9: r4_a_sb_r[59:56] = 4'h9;
      4'ha: r4_a_sb_r[59:56] = 4'h1;
      4'hb: r4_a_sb_r[59:56] = 4'h5;
      4'hc: r4_a_sb_r[59:56] = 4'h0;
      4'hd: r4_a_sb_r[59:56] = 4'h2;
      4'he: r4_a_sb_r[59:56] = 4'h4;
      4'hf: r4_a_sb_r[59:56] = 4'h6;
    endcase
    case (st4[63:60])
      4'h0: r4_a_sb_r[63:60] = 4'hc;
      4'h1: r4_a_sb_r[63:60] = 4'ha;
      4'h2: r4_a_sb_r[63:60] = 4'hd;
      4'h3: r4_a_sb_r[63:60] = 4'h3;
      4'h4: r4_a_sb_r[63:60] = 4'he;
      4'h5: r4_a_sb_r[63:60] = 4'hb;
      4'h6: r4_a_sb_r[63:60] = 4'hf;
      4'h7: r4_a_sb_r[63:60] = 4'h7;
      4'h8: r4_a_sb_r[63:60] = 4'h8;
      4'h9: r4_a_sb_r[63:60] = 4'h9;
      4'ha: r4_a_sb_r[63:60] = 4'h1;
      4'hb: r4_a_sb_r[63:60] = 4'h5;
      4'hc: r4_a_sb_r[63:60] = 4'h0;
      4'hd: r4_a_sb_r[63:60] = 4'h2;
      4'he: r4_a_sb_r[63:60] = 4'h4;
      4'hf: r4_a_sb_r[63:60] = 4'h6;
    endcase
  end
  // Midori ShuffleCell
  wire [63:0] r4_b_sh = {r4_a_sb[35:32], r4_a_sb[11:8], r4_a_sb[55:52], r4_a_sb[31:28], r4_a_sb[27:24], r4_a_sb[51:48], r4_a_sb[15:12], r4_a_sb[39:36], r4_a_sb[7:4], r4_a_sb[47:44], r4_a_sb[19:16], r4_a_sb[59:56], r4_a_sb[63:60], r4_a_sb[23:20], r4_a_sb[43:40], r4_a_sb[3:0]};
  // Midori MixColumn
  wire [63:0] r4_c_mc;
  assign r4_c_mc[3:0] = r4_b_sh[19:16] ^ r4_b_sh[35:32] ^ r4_b_sh[51:48];
  assign r4_c_mc[19:16] = r4_b_sh[3:0] ^ r4_b_sh[35:32] ^ r4_b_sh[51:48];
  assign r4_c_mc[35:32] = r4_b_sh[3:0] ^ r4_b_sh[19:16] ^ r4_b_sh[51:48];
  assign r4_c_mc[51:48] = r4_b_sh[3:0] ^ r4_b_sh[19:16] ^ r4_b_sh[35:32];
  assign r4_c_mc[7:4] = r4_b_sh[23:20] ^ r4_b_sh[39:36] ^ r4_b_sh[55:52];
  assign r4_c_mc[23:20] = r4_b_sh[7:4] ^ r4_b_sh[39:36] ^ r4_b_sh[55:52];
  assign r4_c_mc[39:36] = r4_b_sh[7:4] ^ r4_b_sh[23:20] ^ r4_b_sh[55:52];
  assign r4_c_mc[55:52] = r4_b_sh[7:4] ^ r4_b_sh[23:20] ^ r4_b_sh[39:36];
  assign r4_c_mc[11:8] = r4_b_sh[27:24] ^ r4_b_sh[43:40] ^ r4_b_sh[59:56];
  assign r4_c_mc[27:24] = r4_b_sh[11:8] ^ r4_b_sh[43:40] ^ r4_b_sh[59:56];
  assign r4_c_mc[43:40] = r4_b_sh[11:8] ^ r4_b_sh[27:24] ^ r4_b_sh[59:56];
  assign r4_c_mc[59:56] = r4_b_sh[11:8] ^ r4_b_sh[27:24] ^ r4_b_sh[43:40];
  assign r4_c_mc[15:12] = r4_b_sh[31:28] ^ r4_b_sh[47:44] ^ r4_b_sh[63:60];
  assign r4_c_mc[31:28] = r4_b_sh[15:12] ^ r4_b_sh[47:44] ^ r4_b_sh[63:60];
  assign r4_c_mc[47:44] = r4_b_sh[15:12] ^ r4_b_sh[31:28] ^ r4_b_sh[63:60];
  assign r4_c_mc[63:60] = r4_b_sh[15:12] ^ r4_b_sh[31:28] ^ r4_b_sh[47:44];
  wire [63:0] st5 = r4_c_mc ^ 64'h2545f4914f6cdd1d ^ {key[62:0], key[63:63]};
  reg [63:0] r5_a_sb_r;
  wire [63:0] r5_a_sb = r5_a_sb_r;
  always @(*) begin
    r5_a_sb_r = 64'h0;
    case (st5[3:0])
      4'h0: r5_a_sb_r[3:0] = 4'hc;
      4'h1: r5_a_sb_r[3:0] = 4'ha;
      4'h2: r5_a_sb_r[3:0] = 4'hd;
      4'h3: r5_a_sb_r[3:0] = 4'h3;
      4'h4: r5_a_sb_r[3:0] = 4'he;
      4'h5: r5_a_sb_r[3:0] = 4'hb;
      4'h6: r5_a_sb_r[3:0] = 4'hf;
      4'h7: r5_a_sb_r[3:0] = 4'h7;
      4'h8: r5_a_sb_r[3:0] = 4'h8;
      4'h9: r5_a_sb_r[3:0] = 4'h9;
      4'ha: r5_a_sb_r[3:0] = 4'h1;
      4'hb: r5_a_sb_r[3:0] = 4'h5;
      4'hc: r5_a_sb_r[3:0] = 4'h0;
      4'hd: r5_a_sb_r[3:0] = 4'h2;
      4'he: r5_a_sb_r[3:0] = 4'h4;
      4'hf: r5_a_sb_r[3:0] = 4'h6;
    endcase
    case (st5[7:4])
      4'h0: r5_a_sb_r[7:4] = 4'hc;
      4'h1: r5_a_sb_r[7:4] = 4'ha;
      4'h2: r5_a_sb_r[7:4] = 4'hd;
      4'h3: r5_a_sb_r[7:4] = 4'h3;
      4'h4: r5_a_sb_r[7:4] = 4'he;
      4'h5: r5_a_sb_r[7:4] = 4'hb;
      4'h6: r5_a_sb_r[7:4] = 4'hf;
      4'h7: r5_a_sb_r[7:4] = 4'h7;
      4'h8: r5_a_sb_r[7:4] = 4'h8;
      4'h9: r5_a_sb_r[7:4] = 4'h9;
      4'ha: r5_a_sb_r[7:4] = 4'h1;
      4'hb: r5_a_sb_r[7:4] = 4'h5;
      4'hc: r5_a_sb_r[7:4] = 4'h0;
      4'hd: r5_a_sb_r[7:4] = 4'h2;
      4'he: r5_a_sb_r[7:4] = 4'h4;
      4'hf: r5_a_sb_r[7:4] = 4'h6;
    endcase
    case (st5[11:8])
      4'h0: r5_a_sb_r[11:8] = 4'hc;
      4'h1: r5_a_sb_r[11:8] = 4'ha;
      4'h2: r5_a_sb_r[11:8] = 4'hd;
      4'h3: r5_a_sb_r[11:8] = 4'h3;
      4'h4: r5_a_sb_r[11:8] = 4'he;
      4'h5: r5_a_sb_r[11:8] = 4'hb;
      4'h6: r5_a_sb_r[11:8] = 4'hf;
      4'h7: r5_a_sb_r[11:8] = 4'h7;
      4'h8: r5_a_sb_r[11:8] = 4'h8;
      4'h9: r5_a_sb_r[11:8] = 4'h9;
      4'ha: r5_a_sb_r[11:8] = 4'h1;
      4'hb: r5_a_sb_r[11:8] = 4'h5;
      4'hc: r5_a_sb_r[11:8] = 4'h0;
      4'hd: r5_a_sb_r[11:8] = 4'h2;
      4'he: r5_a_sb_r[11:8] = 4'h4;
      4'hf: r5_a_sb_r[11:8] = 4'h6;
    endcase
    case (st5[15:12])
      4'h0: r5_a_sb_r[15:12] = 4'hc;
      4'h1: r5_a_sb_r[15:12] = 4'ha;
      4'h2: r5_a_sb_r[15:12] = 4'hd;
      4'h3: r5_a_sb_r[15:12] = 4'h3;
      4'h4: r5_a_sb_r[15:12] = 4'he;
      4'h5: r5_a_sb_r[15:12] = 4'hb;
      4'h6: r5_a_sb_r[15:12] = 4'hf;
      4'h7: r5_a_sb_r[15:12] = 4'h7;
      4'h8: r5_a_sb_r[15:12] = 4'h8;
      4'h9: r5_a_sb_r[15:12] = 4'h9;
      4'ha: r5_a_sb_r[15:12] = 4'h1;
      4'hb: r5_a_sb_r[15:12] = 4'h5;
      4'hc: r5_a_sb_r[15:12] = 4'h0;
      4'hd: r5_a_sb_r[15:12] = 4'h2;
      4'he: r5_a_sb_r[15:12] = 4'h4;
      4'hf: r5_a_sb_r[15:12] = 4'h6;
    endcase
    case (st5[19:16])
      4'h0: r5_a_sb_r[19:16] = 4'hc;
      4'h1: r5_a_sb_r[19:16] = 4'ha;
      4'h2: r5_a_sb_r[19:16] = 4'hd;
      4'h3: r5_a_sb_r[19:16] = 4'h3;
      4'h4: r5_a_sb_r[19:16] = 4'he;
      4'h5: r5_a_sb_r[19:16] = 4'hb;
      4'h6: r5_a_sb_r[19:16] = 4'hf;
      4'h7: r5_a_sb_r[19:16] = 4'h7;
      4'h8: r5_a_sb_r[19:16] = 4'h8;
      4'h9: r5_a_sb_r[19:16] = 4'h9;
      4'ha: r5_a_sb_r[19:16] = 4'h1;
      4'hb: r5_a_sb_r[19:16] = 4'h5;
      4'hc: r5_a_sb_r[19:16] = 4'h0;
      4'hd: r5_a_sb_r[19:16] = 4'h2;
      4'he: r5_a_sb_r[19:16] = 4'h4;
      4'hf: r5_a_sb_r[19:16] = 4'h6;
    endcase
    case (st5[23:20])
      4'h0: r5_a_sb_r[23:20] = 4'hc;
      4'h1: r5_a_sb_r[23:20] = 4'ha;
      4'h2: r5_a_sb_r[23:20] = 4'hd;
      4'h3: r5_a_sb_r[23:20] = 4'h3;
      4'h4: r5_a_sb_r[23:20] = 4'he;
      4'h5: r5_a_sb_r[23:20] = 4'hb;
      4'h6: r5_a_sb_r[23:20] = 4'hf;
      4'h7: r5_a_sb_r[23:20] = 4'h7;
      4'h8: r5_a_sb_r[23:20] = 4'h8;
      4'h9: r5_a_sb_r[23:20] = 4'h9;
      4'ha: r5_a_sb_r[23:20] = 4'h1;
      4'hb: r5_a_sb_r[23:20] = 4'h5;
      4'hc: r5_a_sb_r[23:20] = 4'h0;
      4'hd: r5_a_sb_r[23:20] = 4'h2;
      4'he: r5_a_sb_r[23:20] = 4'h4;
      4'hf: r5_a_sb_r[23:20] = 4'h6;
    endcase
    case (st5[27:24])
      4'h0: r5_a_sb_r[27:24] = 4'hc;
      4'h1: r5_a_sb_r[27:24] = 4'ha;
      4'h2: r5_a_sb_r[27:24] = 4'hd;
      4'h3: r5_a_sb_r[27:24] = 4'h3;
      4'h4: r5_a_sb_r[27:24] = 4'he;
      4'h5: r5_a_sb_r[27:24] = 4'hb;
      4'h6: r5_a_sb_r[27:24] = 4'hf;
      4'h7: r5_a_sb_r[27:24] = 4'h7;
      4'h8: r5_a_sb_r[27:24] = 4'h8;
      4'h9: r5_a_sb_r[27:24] = 4'h9;
      4'ha: r5_a_sb_r[27:24] = 4'h1;
      4'hb: r5_a_sb_r[27:24] = 4'h5;
      4'hc: r5_a_sb_r[27:24] = 4'h0;
      4'hd: r5_a_sb_r[27:24] = 4'h2;
      4'he: r5_a_sb_r[27:24] = 4'h4;
      4'hf: r5_a_sb_r[27:24] = 4'h6;
    endcase
    case (st5[31:28])
      4'h0: r5_a_sb_r[31:28] = 4'hc;
      4'h1: r5_a_sb_r[31:28] = 4'ha;
      4'h2: r5_a_sb_r[31:28] = 4'hd;
      4'h3: r5_a_sb_r[31:28] = 4'h3;
      4'h4: r5_a_sb_r[31:28] = 4'he;
      4'h5: r5_a_sb_r[31:28] = 4'hb;
      4'h6: r5_a_sb_r[31:28] = 4'hf;
      4'h7: r5_a_sb_r[31:28] = 4'h7;
      4'h8: r5_a_sb_r[31:28] = 4'h8;
      4'h9: r5_a_sb_r[31:28] = 4'h9;
      4'ha: r5_a_sb_r[31:28] = 4'h1;
      4'hb: r5_a_sb_r[31:28] = 4'h5;
      4'hc: r5_a_sb_r[31:28] = 4'h0;
      4'hd: r5_a_sb_r[31:28] = 4'h2;
      4'he: r5_a_sb_r[31:28] = 4'h4;
      4'hf: r5_a_sb_r[31:28] = 4'h6;
    endcase
    case (st5[35:32])
      4'h0: r5_a_sb_r[35:32] = 4'hc;
      4'h1: r5_a_sb_r[35:32] = 4'ha;
      4'h2: r5_a_sb_r[35:32] = 4'hd;
      4'h3: r5_a_sb_r[35:32] = 4'h3;
      4'h4: r5_a_sb_r[35:32] = 4'he;
      4'h5: r5_a_sb_r[35:32] = 4'hb;
      4'h6: r5_a_sb_r[35:32] = 4'hf;
      4'h7: r5_a_sb_r[35:32] = 4'h7;
      4'h8: r5_a_sb_r[35:32] = 4'h8;
      4'h9: r5_a_sb_r[35:32] = 4'h9;
      4'ha: r5_a_sb_r[35:32] = 4'h1;
      4'hb: r5_a_sb_r[35:32] = 4'h5;
      4'hc: r5_a_sb_r[35:32] = 4'h0;
      4'hd: r5_a_sb_r[35:32] = 4'h2;
      4'he: r5_a_sb_r[35:32] = 4'h4;
      4'hf: r5_a_sb_r[35:32] = 4'h6;
    endcase
    case (st5[39:36])
      4'h0: r5_a_sb_r[39:36] = 4'hc;
      4'h1: r5_a_sb_r[39:36] = 4'ha;
      4'h2: r5_a_sb_r[39:36] = 4'hd;
      4'h3: r5_a_sb_r[39:36] = 4'h3;
      4'h4: r5_a_sb_r[39:36] = 4'he;
      4'h5: r5_a_sb_r[39:36] = 4'hb;
      4'h6: r5_a_sb_r[39:36] = 4'hf;
      4'h7: r5_a_sb_r[39:36] = 4'h7;
      4'h8: r5_a_sb_r[39:36] = 4'h8;
      4'h9: r5_a_sb_r[39:36] = 4'h9;
      4'ha: r5_a_sb_r[39:36] = 4'h1;
      4'hb: r5_a_sb_r[39:36] = 4'h5;
      4'hc: r5_a_sb_r[39:36] = 4'h0;
      4'hd: r5_a_sb_r[39:36] = 4'h2;
      4'he: r5_a_sb_r[39:36] = 4'h4;
      4'hf: r5_a_sb_r[39:36] = 4'h6;
    endcase
    case (st5[43:40])
      4'h0: r5_a_sb_r[43:40] = 4'hc;
      4'h1: r5_a_sb_r[43:40] = 4'ha;
      4'h2: r5_a_sb_r[43:40] = 4'hd;
      4'h3: r5_a_sb_r[43:40] = 4'h3;
      4'h4: r5_a_sb_r[43:40] = 4'he;
      4'h5: r5_a_sb_r[43:40] = 4'hb;
      4'h6: r5_a_sb_r[43:40] = 4'hf;
      4'h7: r5_a_sb_r[43:40] = 4'h7;
      4'h8: r5_a_sb_r[43:40] = 4'h8;
      4'h9: r5_a_sb_r[43:40] = 4'h9;
      4'ha: r5_a_sb_r[43:40] = 4'h1;
      4'hb: r5_a_sb_r[43:40] = 4'h5;
      4'hc: r5_a_sb_r[43:40] = 4'h0;
      4'hd: r5_a_sb_r[43:40] = 4'h2;
      4'he: r5_a_sb_r[43:40] = 4'h4;
      4'hf: r5_a_sb_r[43:40] = 4'h6;
    endcase
    case (st5[47:44])
      4'h0: r5_a_sb_r[47:44] = 4'hc;
      4'h1: r5_a_sb_r[47:44] = 4'ha;
      4'h2: r5_a_sb_r[47:44] = 4'hd;
      4'h3: r5_a_sb_r[47:44] = 4'h3;
      4'h4: r5_a_sb_r[47:44] = 4'he;
      4'h5: r5_a_sb_r[47:44] = 4'hb;
      4'h6: r5_a_sb_r[47:44] = 4'hf;
      4'h7: r5_a_sb_r[47:44] = 4'h7;
      4'h8: r5_a_sb_r[47:44] = 4'h8;
      4'h9: r5_a_sb_r[47:44] = 4'h9;
      4'ha: r5_a_sb_r[47:44] = 4'h1;
      4'hb: r5_a_sb_r[47:44] = 4'h5;
      4'hc: r5_a_sb_r[47:44] = 4'h0;
      4'hd: r5_a_sb_r[47:44] = 4'h2;
      4'he: r5_a_sb_r[47:44] = 4'h4;
      4'hf: r5_a_sb_r[47:44] = 4'h6;
    endcase
    case (st5[51:48])
      4'h0: r5_a_sb_r[51:48] = 4'hc;
      4'h1: r5_a_sb_r[51:48] = 4'ha;
      4'h2: r5_a_sb_r[51:48] = 4'hd;
      4'h3: r5_a_sb_r[51:48] = 4'h3;
      4'h4: r5_a_sb_r[51:48] = 4'he;
      4'h5: r5_a_sb_r[51:48] = 4'hb;
      4'h6: r5_a_sb_r[51:48] = 4'hf;
      4'h7: r5_a_sb_r[51:48] = 4'h7;
      4'h8: r5_a_sb_r[51:48] = 4'h8;
      4'h9: r5_a_sb_r[51:48] = 4'h9;
      4'ha: r5_a_sb_r[51:48] = 4'h1;
      4'hb: r5_a_sb_r[51:48] = 4'h5;
      4'hc: r5_a_sb_r[51:48] = 4'h0;
      4'hd: r5_a_sb_r[51:48] = 4'h2;
      4'he: r5_a_sb_r[51:48] = 4'h4;
      4'hf: r5_a_sb_r[51:48] = 4'h6;
    endcase
    case (st5[55:52])
      4'h0: r5_a_sb_r[55:52] = 4'hc;
      4'h1: r5_a_sb_r[55:52] = 4'ha;
      4'h2: r5_a_sb_r[55:52] = 4'hd;
      4'h3: r5_a_sb_r[55:52] = 4'h3;
      4'h4: r5_a_sb_r[55:52] = 4'he;
      4'h5: r5_a_sb_r[55:52] = 4'hb;
      4'h6: r5_a_sb_r[55:52] = 4'hf;
      4'h7: r5_a_sb_r[55:52] = 4'h7;
      4'h8: r5_a_sb_r[55:52] = 4'h8;
      4'h9: r5_a_sb_r[55:52] = 4'h9;
      4'ha: r5_a_sb_r[55:52] = 4'h1;
      4'hb: r5_a_sb_r[55:52] = 4'h5;
      4'hc: r5_a_sb_r[55:52] = 4'h0;
      4'hd: r5_a_sb_r[55:52] = 4'h2;
      4'he: r5_a_sb_r[55:52] = 4'h4;
      4'hf: r5_a_sb_r[55:52] = 4'h6;
    endcase
    case (st5[59:56])
      4'h0: r5_a_sb_r[59:56] = 4'hc;
      4'h1: r5_a_sb_r[59:56] = 4'ha;
      4'h2: r5_a_sb_r[59:56] = 4'hd;
      4'h3: r5_a_sb_r[59:56] = 4'h3;
      4'h4: r5_a_sb_r[59:56] = 4'he;
      4'h5: r5_a_sb_r[59:56] = 4'hb;
      4'h6: r5_a_sb_r[59:56] = 4'hf;
      4'h7: r5_a_sb_r[59:56] = 4'h7;
      4'h8: r5_a_sb_r[59:56] = 4'h8;
      4'h9: r5_a_sb_r[59:56] = 4'h9;
      4'ha: r5_a_sb_r[59:56] = 4'h1;
      4'hb: r5_a_sb_r[59:56] = 4'h5;
      4'hc: r5_a_sb_r[59:56] = 4'h0;
      4'hd: r5_a_sb_r[59:56] = 4'h2;
      4'he: r5_a_sb_r[59:56] = 4'h4;
      4'hf: r5_a_sb_r[59:56] = 4'h6;
    endcase
    case (st5[63:60])
      4'h0: r5_a_sb_r[63:60] = 4'hc;
      4'h1: r5_a_sb_r[63:60] = 4'ha;
      4'h2: r5_a_sb_r[63:60] = 4'hd;
      4'h3: r5_a_sb_r[63:60] = 4'h3;
      4'h4: r5_a_sb_r[63:60] = 4'he;
      4'h5: r5_a_sb_r[63:60] = 4'hb;
      4'h6: r5_a_sb_r[63:60] = 4'hf;
      4'h7: r5_a_sb_r[63:60] = 4'h7;
      4'h8: r5_a_sb_r[63:60] = 4'h8;
      4'h9: r5_a_sb_r[63:60] = 4'h9;
      4'ha: r5_a_sb_r[63:60] = 4'h1;
      4'hb: r5_a_sb_r[63:60] = 4'h5;
      4'hc: r5_a_sb_r[63:60] = 4'h0;
      4'hd: r5_a_sb_r[63:60] = 4'h2;
      4'he: r5_a_sb_r[63:60] = 4'h4;
      4'hf: r5_a_sb_r[63:60] = 4'h6;
    endcase
  end
  // Midori ShuffleCell
  wire [63:0] r5_b_sh = {r5_a_sb[35:32], r5_a_sb[11:8], r5_a_sb[55:52], r5_a_sb[31:28], r5_a_sb[27:24], r5_a_sb[51:48], r5_a_sb[15:12], r5_a_sb[39:36], r5_a_sb[7:4], r5_a_sb[47:44], r5_a_sb[19:16], r5_a_sb[59:56], r5_a_sb[63:60], r5_a_sb[23:20], r5_a_sb[43:40], r5_a_sb[3:0]};
  // Midori MixColumn
  wire [63:0] r5_c_mc;
  assign r5_c_mc[3:0] = r5_b_sh[19:16] ^ r5_b_sh[35:32] ^ r5_b_sh[51:48];
  assign r5_c_mc[19:16] = r5_b_sh[3:0] ^ r5_b_sh[35:32] ^ r5_b_sh[51:48];
  assign r5_c_mc[35:32] = r5_b_sh[3:0] ^ r5_b_sh[19:16] ^ r5_b_sh[51:48];
  assign r5_c_mc[51:48] = r5_b_sh[3:0] ^ r5_b_sh[19:16] ^ r5_b_sh[35:32];
  assign r5_c_mc[7:4] = r5_b_sh[23:20] ^ r5_b_sh[39:36] ^ r5_b_sh[55:52];
  assign r5_c_mc[23:20] = r5_b_sh[7:4] ^ r5_b_sh[39:36] ^ r5_b_sh[55:52];
  assign r5_c_mc[39:36] = r5_b_sh[7:4] ^ r5_b_sh[23:20] ^ r5_b_sh[55:52];
  assign r5_c_mc[55:52] = r5_b_sh[7:4] ^ r5_b_sh[23:20] ^ r5_b_sh[39:36];
  assign r5_c_mc[11:8] = r5_b_sh[27:24] ^ r5_b_sh[43:40] ^ r5_b_sh[59:56];
  assign r5_c_mc[27:24] = r5_b_sh[11:8] ^ r5_b_sh[43:40] ^ r5_b_sh[59:56];
  assign r5_c_mc[43:40] = r5_b_sh[11:8] ^ r5_b_sh[27:24] ^ r5_b_sh[59:56];
  assign r5_c_mc[59:56] = r5_b_sh[11:8] ^ r5_b_sh[27:24] ^ r5_b_sh[43:40];
  assign r5_c_mc[15:12] = r5_b_sh[31:28] ^ r5_b_sh[47:44] ^ r5_b_sh[63:60];
  assign r5_c_mc[31:28] = r5_b_sh[15:12] ^ r5_b_sh[47:44] ^ r5_b_sh[63:60];
  assign r5_c_mc[47:44] = r5_b_sh[15:12] ^ r5_b_sh[31:28] ^ r5_b_sh[63:60];
  assign r5_c_mc[63:60] = r5_b_sh[15:12] ^ r5_b_sh[31:28] ^ r5_b_sh[47:44];
  wire [63:0] st6 = r5_c_mc ^ 64'h9e3779b9a1e7c2fa ^ {key[49:0], key[63:50]};
  assign out = st6 ^ {32'h0, key[63:32]};
endmodule
