module t6_sboxrot6(input [63:0] val, input [63:0] key, output [63:0] out);
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
  wire [63:0] st1 = {sx0[56:0], sx0[63:57]};
  wire [63:0] kx1 = st1 ^ rk1;
  wire [63:0] sx1;
  genvar g1;
  generate for (g1=0; g1<16; g1=g1+1) begin : sbl1
    assign sx1[4*g1+3:4*g1] = sb0(kx1[4*g1+3:4*g1]);
  end endgenerate
  wire [63:0] st2 = {sx1[40:0], sx1[63:41]};
  wire [63:0] kx2 = st2 ^ rk2;
  wire [63:0] sx2;
  genvar g2;
  generate for (g2=0; g2<16; g2=g2+1) begin : sbl2
    assign sx2[4*g2+3:4*g2] = sb0(kx2[4*g2+3:4*g2]);
  end endgenerate
  wire [63:0] st3 = {sx2[22:0], sx2[63:23]};
  wire [63:0] kx3 = st3 ^ rk3;
  wire [63:0] sx3;
  genvar g3;
  generate for (g3=0; g3<16; g3=g3+1) begin : sbl3
    assign sx3[4*g3+3:4*g3] = sb0(kx3[4*g3+3:4*g3]);
  end endgenerate
  wire [63:0] st4 = {sx3[52:0], sx3[63:53]};
  wire [63:0] kx4 = st4 ^ rk4;
  wire [63:0] sx4;
  genvar g4;
  generate for (g4=0; g4<16; g4=g4+1) begin : sbl4
    assign sx4[4*g4+3:4*g4] = sb0(kx4[4*g4+3:4*g4]);
  end endgenerate
  wire [63:0] st5 = {sx4[34:0], sx4[63:35]};
  wire [63:0] kx5 = st5 ^ rk5;
  wire [63:0] sx5;
  genvar g5;
  generate for (g5=0; g5<16; g5=g5+1) begin : sbl5
    assign sx5[4*g5+3:4*g5] = sb0(kx5[4*g5+3:4*g5]);
  end endgenerate
  wire [63:0] st6 = {sx5[10:0], sx5[63:11]};
  wire [63:0] key_r13 = {key[50:0], key[63:51]};
  assign out = st6 ^ {32'h0, key_r13[63:32]};
endmodule
