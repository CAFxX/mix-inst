// Full 3-stage MUXD, COMPRESSED stage form (y = x ^ g, no d-term).
// Fresh rotations (NOT t6_b59_47's). Rotations are wiring; S0 is rotation-independent.
// Stage tuples (s,a,b): (7,41,23), (11,53,29), (3,47,61)
module muxd3_nod(
    input  [63:0] x,
    input  [63:0] k,
    output [63:0] y
);
    function [63:0] rotl64(input [63:0] v, input integer r);
        rotl64 = (v << r) | (v >> (64-r));
    endfunction
    wire [63:0] x0 = x ^ k;
    // Stage 0: (s,a,b) = (7,41,23)
    wire [63:0] g0 = (rotl64(x0,7) & rotl64(x0,41)) | (~rotl64(x0,7) & rotl64(x0,23));
    wire [63:0] x1 = x0 ^ g0;
    // Stage 1: (s,a,b) = (11,53,29)
    wire [63:0] g1 = (rotl64(x1,11) & rotl64(x1,53)) | (~rotl64(x1,11) & rotl64(x1,29));
    wire [63:0] x2 = x1 ^ g1;
    // Stage 2: (s,a,b) = (3,47,61)
    wire [63:0] g2 = (rotl64(x2,3) & rotl64(x2,47)) | (~rotl64(x2,3) & rotl64(x2,61));
    wire [63:0] x3 = x2 ^ g2;
    assign y = x3 ^ rotl64(k,13);
endmodule
