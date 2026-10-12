// al_linchi3: 3 rounds of (lin + chi)
// lin: x ^= rotl(x,a) ^ rotl(x,b)
// chi: x ^= ((~ra) & rb) ^ rc
module al_linchi3(input [63:0] v, input [63:0] k, output [63:0] o);
function [63:0] rotl64(input [63:0] x, input [5:0] r);
    rotl64 = r ? (x << r) | (x >> (64 - r)) : x;
endfunction
wire [63:0] x0 = v ^ k;
// Round 1: lin(5,13) then chi(1,2,13)
wire [63:0] l1 = x0 ^ rotl64(x0, 5) ^ rotl64(x0, 13);
wire [63:0] c1 = l1 ^ ((~rotl64(l1, 1)) & rotl64(l1, 2)) ^ rotl64(l1, 13);
// Round 2: lin(11,29) then chi(7,19,5)
wire [63:0] l2 = c1 ^ rotl64(c1, 11) ^ rotl64(c1, 29);
wire [63:0] c2 = l2 ^ ((~rotl64(l2, 7)) & rotl64(l2, 19)) ^ rotl64(l2, 5);
// Round 3: lin(7,23) then chi(3,11,29)
wire [63:0] l3 = c2 ^ rotl64(c2, 7) ^ rotl64(c2, 23);
wire [63:0] c3 = l3 ^ ((~rotl64(l3, 3)) & rotl64(l3, 11)) ^ rotl64(l3, 29);
assign o = c3 ^ rotl64(k, 13);
endmodule
