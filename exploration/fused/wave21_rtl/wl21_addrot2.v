// wl21_addrot2: fused wave-21 word-level op probe (gen_fused21.py)
module wl21_addrot2(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] o
);

    function [63:0] rotl;
        input [63:0] x;
        input integer r;
        begin
            r = r % 64;
            rotl = r ? ((x << r) | (x >> (64 - r))) : x;
        end
    endfunction
    wire [63:0] s1 = rotl(v + k, 17);
    assign o = rotl(s1 + {k[31:0], k[63:32]}, 31);
endmodule
