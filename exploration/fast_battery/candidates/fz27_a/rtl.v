// fz27_a: gen_fused24.py
module fz27_a(
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
    function [63:0] nibchi;
        input [63:0] x;
        integer n;
        reg b0, b1, b2, b3;
        begin
            for (n = 0; n < 16; n = n + 1) begin
                b0 = x[4*n]; b1 = x[4*n+1]; b2 = x[4*n+2]; b3 = x[4*n+3];
                nibchi[4*n]   = b0 ^ (~b1 & b2);
                nibchi[4*n+1] = b1 ^ (~b2 & b3);
                nibchi[4*n+2] = b2 ^ (~b3 & b0);
                nibchi[4*n+3] = b3 ^ (~b0 & b1);
            end
        end
    endfunction
    wire [63:0] s0 = val ^ key;

    wire [63:0] s1 = s0 ^ (rotl(s0, 2) & rotl(s0, 8)) ^ rotl(s0, 14) ^ rotl(s0, 30);
    wire [63:0] s2 = s1 ^ (rotl(s1, 4) & rotl(s1, 12)) ^ rotl(s1, 20) ^ rotl(s1, 38);
    wire [63:0] s3 = s2 ^ (rotl(s2, 6) & rotl(s2, 16)) ^ rotl(s2, 22);
    wire [63:0] s4 = s3 ^ (rotl(s3, 10) & rotl(s3, 24)) ^ rotl(s3, 44);
    wire [63:0] s5 = s4 ^ (~rotl(s4,32) & rotl(s4,20)) ^ rotl(s4,36) ^ rotl(s4,54);
    assign out = s5 ^ rotl(key, 13);
endmodule
