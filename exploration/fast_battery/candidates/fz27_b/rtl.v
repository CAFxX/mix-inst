// fz27_b: gen_fused24.py
module fz27_b(
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

    wire [63:0] s1 = s0 ^ (rotl(s0, 0) & rotl(s0, 6)) ^ rotl(s0, 12) ^ rotl(s0, 28);
    wire [63:0] s2 = s1 ^ (rotl(s1, 2) & rotl(s1, 10)) ^ rotl(s1, 18) ^ rotl(s1, 36);
    wire [63:0] s3 = s2 ^ (rotl(s2, 4) & rotl(s2, 14)) ^ rotl(s2, 20);
    wire [63:0] s4 = s3 ^ (rotl(s3, 8) & rotl(s3, 22)) ^ rotl(s3, 42);
    wire [63:0] s5 = s4 ^ (~rotl(s4,30) & rotl(s4,18)) ^ rotl(s4,34) ^ rotl(s4,52);
    assign out = s5 ^ rotl(key, 13);
endmodule
