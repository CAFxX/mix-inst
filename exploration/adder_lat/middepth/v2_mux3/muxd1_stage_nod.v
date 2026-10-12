// V2a compressed stage: drop the final ^ rotl(x,d). y = x ^ g.
module muxd1_stage_nod(
    input  [63:0] x,
    output [63:0] y
);
    function [63:0] rotl64(input [63:0] v, input integer r);
        rotl64 = (v << r) | (v >> (64-r));
    endfunction
    wire [63:0] g = (rotl64(x,7) & rotl64(x,41)) | (~rotl64(x,7) & rotl64(x,23));
    assign y = x ^ g;
endmodule
