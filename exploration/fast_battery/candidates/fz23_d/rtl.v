// fz23_d: gen_fused23.py
module fz23_d(
    input  wire [63:0] val,
    input  wire [63:0] key,
    output wire [63:0] out
);
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
    wire [63:0] s2 = s1 ^ (rotl(s1, 3) & rotl(s1, 11)) ^ rotl(s1, 17);
    wire [63:0] s3 = s2 ^ (rotl(s2, 5) & rotl(s2, 15)) ^ rotl(s2, 25) ^ rotl(s2, 41);
    wire [63:0] s4 = s3 ^ (rotl(s3, 9) & rotl(s3, 21)) ^ rotl(s3, 43);
    wire [63:0] s5 = s4 ^ (rotl(s4, 13) & rotl(s4, 27)) ^ rotl(s4, 37) ^ rotl(s4, 55);
    assign out = s5 ^ rotl(key, 13);
endmodule
