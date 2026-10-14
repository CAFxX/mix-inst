// composite inversion core: delta -> tower inv -> delta^-1
// lam=0xa
module comp8_core (input [7:0] x, output [7:0] y);
  wire [7:0] p;
  assign p[0] = ^((x & 8'ha5));
  assign p[1] = ^((x & 8'he4));
  assign p[2] = ^((x & 8'h04));
  assign p[3] = ^((x & 8'h18));
  assign p[4] = ^((x & 8'ha2));
  assign p[5] = ^((x & 8'h0c));
  assign p[6] = ^((x & 8'hd2));
  assign p[7] = ^((x & 8'ha0));
  wire [3:0] ah = p[7:4];
  wire [3:0] al = p[3:0];
  wire [3:0] ah2 = gf4_mul(ah, ah);
  wire [3:0] al2 = gf4_mul(al, al);
  wire [3:0] d = gf4_mul(ah2, 4'ha) ^ gf4_mul(ah, al) ^ al2;
  wire [3:0] di = gf4_inv4(d);
  wire [3:0] oh = gf4_mul(ah, di);
  wire [3:0] ol = gf4_mul(ah ^ al, di);
  wire [7:0] q = {oh, ol};
  assign y[0] = ^((q & 8'h85));
  assign y[1] = ^((q & 8'h90));
  assign y[2] = ^((q & 8'h04));
  assign y[3] = ^((q & 8'h24));
  assign y[4] = ^((q & 8'h2c));
  assign y[5] = ^((q & 8'hfa));
  assign y[6] = ^((q & 8'h86));
  assign y[7] = ^((q & 8'h7a));
  function [3:0] gf4_mul(input [3:0] a, b);
    reg [6:0] pp; integer k;
    begin
      pp = 7'b0;
      for (k = 0; k < 4; k = k + 1)
        if (b[k]) pp = pp ^ ({3'b0, a} << k);
      gf4_mul[3] = pp[3] ^ pp[6];
      gf4_mul[2] = pp[2] ^ pp[6] ^ pp[5];
      gf4_mul[1] = pp[1] ^ pp[5] ^ pp[4];
      gf4_mul[0] = pp[0] ^ pp[4];
    end
  endfunction
  function [3:0] gf4_inv4(input [3:0] d);
    case (d)
      4'h0: gf4_inv4 = 4'h0;
      4'h1: gf4_inv4 = 4'h1;
      4'h2: gf4_inv4 = 4'h9;
      4'h3: gf4_inv4 = 4'he;
      4'h4: gf4_inv4 = 4'hd;
      4'h5: gf4_inv4 = 4'hb;
      4'h6: gf4_inv4 = 4'h7;
      4'h7: gf4_inv4 = 4'h6;
      4'h8: gf4_inv4 = 4'hf;
      4'h9: gf4_inv4 = 4'h2;
      4'ha: gf4_inv4 = 4'hc;
      4'hb: gf4_inv4 = 4'h5;
      4'hc: gf4_inv4 = 4'ha;
      4'hd: gf4_inv4 = 4'h4;
      4'he: gf4_inv4 = 4'h3;
      4'hf: gf4_inv4 = 4'h8;
    endcase
  endfunction
endmodule
