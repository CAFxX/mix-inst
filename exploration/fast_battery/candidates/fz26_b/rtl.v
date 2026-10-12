// fz26_b: gen_fused26.py
module fz26_b(
    input  wire [63:0] val, input  wire [63:0] key,
    output wire [63:0] out );
    function [63:0] rotl;
        input [63:0] x;
        input integer r;
        begin
            r = r % 64;
            rotl = r ? ((x << r) | (x >> (64 - r))) : x;
        end
    endfunction
    wire [63:0] s0 = val ^ key;
    wire [63:0] s1 = s0 ^ (rotl(s0, 1) & rotl(s0, 7)) ^ rotl(s0, 13) ^ rotl(s0, 29);
    wire [63:0] s2 = s1 ^ (rotl(s1, 3) & rotl(s1, 11)) ^ rotl(s1, 19) ^ rotl(s1, 37);
    wire [63:0] s3 = s2 ^ (rotl(s2, 5) & rotl(s2, 15)) ^ rotl(s2, 21);
    wire [63:0] s4 = s3 ^ (rotl(s3,3) & rotl(s3,11)) ^ (~rotl(s3,17) & rotl(s3,29)) ^ rotl(s3,43) ^ rotl(s3,55);
    assign out = s4 ^ rotl(key, 13);
endmodule
