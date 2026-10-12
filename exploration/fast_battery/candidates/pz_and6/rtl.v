// pz_and6: cheap primitive cost probe
module pz_and6(input [63:0] v, input [63:0] k, output [63:0] h);
function [63:0] rotl64(input [63:0] x, input [5:0] r);
  rotl64 = r == 0 ? x : ((x << r) | (x >> (6'd64 - r)));
endfunction
wire [63:0] x0 = v ^ k;
wire [63:0] x1 = x0 ^ (rotl64(x0,1) & rotl64(x0,2)) ^ rotl64(x0,13);
wire [63:0] x2 = x1 ^ (rotl64(x1,7) & rotl64(x1,19)) ^ rotl64(x1,5);
wire [63:0] x3 = x2 ^ (rotl64(x2,3) & rotl64(x2,11)) ^ rotl64(x2,29);
wire [63:0] x4 = x3 ^ (rotl64(x3,17) & rotl64(x3,31)) ^ rotl64(x3,7);
wire [63:0] x5 = x4 ^ (rotl64(x4,11) & rotl64(x4,23)) ^ rotl64(x4,37);
wire [63:0] x6 = x5 ^ (rotl64(x5,19) & rotl64(x5,41)) ^ rotl64(x5,23);
assign h = x6 ^ rotl64(k, 13);
endmodule