// Fused candidate fz_ch_5: 5-stage Ch replacement: x = Ch(x,ra,rb)^Ch(rc,rd,re)^Ch(rf,rg,rh)
module mix(input [63:0] v, input [63:0] k, output [63:0] out);
function [63:0] rotl(input [63:0] x, input integer r);
    rotl = (x << r) | (x >> (64 - r));
endfunction
function [63:0] ch(input [63:0] x, y, z);
    ch = (x & y) | (~x & z);
endfunction
wire [63:0] w0 = v ^ k;
wire [63:0] w1 = ch(w0, rotl(w0,3), rotl(w0,11)) ^ ch(rotl(w0,23), rotl(w0,31), rotl(w0,43)) ^ ch(rotl(w0,53), rotl(w0,7), rotl(w0,17));
wire [63:0] w2 = ch(w1, rotl(w1,7), rotl(w1,17)) ^ ch(rotl(w1,29), rotl(w1,37), rotl(w1,47)) ^ ch(rotl(w1,59), rotl(w1,5), rotl(w1,13));
wire [63:0] w3 = ch(w2, rotl(w2,5), rotl(w2,13)) ^ ch(rotl(w2,27), rotl(w2,41), rotl(w2,49)) ^ ch(rotl(w2,61), rotl(w2,9), rotl(w2,19));
wire [63:0] w4 = ch(w3, rotl(w3,9), rotl(w3,19)) ^ ch(rotl(w3,33), rotl(w3,39), rotl(w3,51)) ^ ch(rotl(w3,57), rotl(w3,11), rotl(w3,23));
wire [63:0] w5 = ch(w4, rotl(w4,11), rotl(w4,23)) ^ ch(rotl(w4,35), rotl(w4,45), rotl(w4,55)) ^ ch(rotl(w4,63), rotl(w4,13), rotl(w4,25));
assign out = w5 ^ rotl(k, 13);
endmodule