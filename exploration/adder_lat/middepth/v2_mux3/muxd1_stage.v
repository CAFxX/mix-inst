// One MUXD stage (V2 fresh rotations; placeholder (7,41,23,59) for S0 stage cost).
// Rotation amounts are pure wiring, so S0 is rotation-independent.
module muxd1_stage(
    input  [63:0] x,
    output [63:0] y
);
    function [63:0] rotl64(input [63:0] v, input integer r);
        rotl64 = (v << r) | (v >> (64-r));
    endfunction
    wire [63:0] g = (rotl64(x,7) & rotl64(x,41)) | (~rotl64(x,7) & rotl64(x,23));
    assign y = x ^ g ^ rotl64(x,59);
endmodule
