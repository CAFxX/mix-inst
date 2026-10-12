// fz25_c: gen_fused25.py
module fz25_c(
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
    wire [63:0] p = rotl(s0, 19) ^ rotl(s0, 37);
    wire [63:0] s1 = s0 ^ (rotl(s0, 1) & rotl(s0, 11)) ^ rotl(p, 0);
    wire [63:0] s2 = s1 ^ (rotl(s1, 5) & rotl(s1, 19)) ^ rotl(p, 23);
    wire [63:0] s3 = s2 ^ (rotl(s2, 9) & rotl(s2, 25)) ^ rotl(p, 5);
    wire [63:0] s4 = s3 ^ (rotl(s3, 13) & rotl(s3, 31)) ^ rotl(p, 39);
    wire [63:0] s5 = s4 ^ (rotl(s4, 17) & rotl(s4, 35)) ^ rotl(p, 15);
    assign out = s5 ^ rotl(key, 13);
endmodule
