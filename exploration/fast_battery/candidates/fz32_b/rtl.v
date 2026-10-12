// fz32_b: wave32 and3
module fz32_b(input [63:0] v, input [63:0] k, output [63:0] h);
function [63:0] rotl64(input [63:0] x, input [5:0] r);
  rotl64 = r == 0 ? x : ((x << r) | (x >> (6'd64 - r)));
endfunction
wire [63:0] x0 = v ^ k;
wire [63:0] x1 = x0 ^ (rotl64(x0,1) & rotl64(x0,7)) ^ rotl64(x0,13) ^ rotl64(x0,29);
wire [63:0] x2 = x1 ^ (rotl64(x1,3) & rotl64(x1,11)) ^ rotl64(x1,19) ^ rotl64(x1,37);
wire [63:0] x3 = x2 ^ (rotl64(x2,5) & rotl64(x2,15)) ^ rotl64(x2,21);
wire [63:0] x4 = x3 ^ (rotl64(x3,9) & rotl64(x3,23)) ^ rotl64(x3,43);
wire [63:0] x5 = x4 ^ (rotl64(x4,13) & rotl64(x4,27) & rotl64(x4,41)) ^ rotl64(x4,7);
assign h = x5 ^ rotl64(k, 13);
endmodule
