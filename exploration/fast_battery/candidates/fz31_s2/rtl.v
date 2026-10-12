// fz31_s2: wave31 axis C (S-box layer probe)
module fz31_s2(input [63:0] v, input [63:0] k, output [63:0] h);
function [63:0] rotl64(input [63:0] x, input [5:0] r);
  rotl64 = (x << r) | (x >> (6'd64 - r));
endfunction
function [3:0] sbox4(input [3:0] b);
  case (b)
    4'h0: sbox4 = 4'hC; 4'h1: sbox4 = 4'h5;
    4'h2: sbox4 = 4'h6; 4'h3: sbox4 = 4'hB;
    4'h4: sbox4 = 4'h9; 4'h5: sbox4 = 4'h0;
    4'h6: sbox4 = 4'hA; 4'h7: sbox4 = 4'hD;
    4'h8: sbox4 = 4'h3; 4'h9: sbox4 = 4'hE;
    4'hA: sbox4 = 4'hF; 4'hB: sbox4 = 4'h8;
    4'hC: sbox4 = 4'h4; 4'hD: sbox4 = 4'h7;
    4'hE: sbox4 = 4'h1; 4'hF: sbox4 = 4'h2;
  endcase
endfunction
function [63:0] psbox(input [63:0] x);
  integer n;
  begin
    for (n = 0; n < 16; n = n + 1)
      psbox[4*n +: 4] = sbox4(x[4*n +: 4]);
  end
endfunction
wire [63:0] x0 = v ^ k;
wire [63:0] x1 = x0 ^ psbox(x0) ^ rotl64(x0, 13);
wire [63:0] x2 = x1 ^ (rotl64(x1,1) & rotl64(x1,7)) ^ rotl64(x1,13) ^ rotl64(x1,29);
wire [63:0] x3 = x2 ^ (rotl64(x2,5) & rotl64(x2,15)) ^ rotl64(x2,21);
assign h = x3 ^ rotl64(k, 13);
endmodule
