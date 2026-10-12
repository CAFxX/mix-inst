// 2-stage MUXD (t6_b59_47 stages 0-1)
module muxd2(
    input  [63:0] x,
    input  [63:0] k,
    output [63:0] y
);
    function [63:0] rotl64(input [63:0] v, input integer r);
        rotl64 = (v << r) | (v >> (64-r));
    endfunction
    wire [63:0] x0 = x ^ k;
    // Stage 0: (17,22,10,55)
    wire [63:0] g0 = (rotl64(x0,17) & rotl64(x0,22)) | (~rotl64(x0,17) & rotl64(x0,10));
    wire [63:0] x1 = x0 ^ g0 ^ rotl64(x0,55);
    // Stage 1: (63,62,49,57)
    wire [63:0] g1 = (rotl64(x1,63) & rotl64(x1,62)) | (~rotl64(x1,63) & rotl64(x1,49));
    wire [63:0] x2 = x1 ^ g1 ^ rotl64(x1,57);
    assign y = x2 ^ rotl64(k,13);
endmodule
