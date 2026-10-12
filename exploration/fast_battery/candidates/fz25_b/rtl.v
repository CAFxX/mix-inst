// fz25_b: gen_fused25.py
module fz25_b(
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
    wire [63:0] p = rotl(s0, 7) ^ rotl(s0, 41);
    wire [63:0] s1 = s0 ^ (rotl(s0, 2) & rotl(s0, 9)) ^ rotl(p, 0);
    wire [63:0] s2 = s1 ^ (rotl(s1, 4) & rotl(s1, 13)) ^ rotl(p, 17);
    wire [63:0] s3 = s2 ^ (rotl(s2, 6) & rotl(s2, 17)) ^ rotl(p, 33);
    wire [63:0] s4 = s3 ^ (rotl(s3, 11) & rotl(s3, 23)) ^ rotl(p, 11);
    wire [63:0] s5 = s4 ^ (rotl(s4, 15) & rotl(s4, 27)) ^ rotl(p, 47);
    assign out = s5 ^ rotl(key, 13);
endmodule
