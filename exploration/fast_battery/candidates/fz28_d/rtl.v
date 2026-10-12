// fz28_d: gen_fused24.py
module fz28_d(
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

    wire [63:0] s1 = s0 ^ (rotl(s0, 1) & rotl(s0, 7)) ^ rotl(s0, 13) ^ rotl(s0, 29);
    wire [63:0] s2 = s1 ^ (rotl(s1, 3) & rotl(s1, 11)) ^ rotl(s1, 19) ^ rotl(s1, 37);
    wire [63:0] s3 = s2 ^ (rotl(s2, 5) & rotl(s2, 15)) ^ rotl(s2, 21);
    wire [63:0] s4 = s3 ^ (rotl(s3, 9) & rotl(s3, 23)) ^ rotl(s3, 43);
    wire [63:0] s5 = s4 ^ (~rotl(s4,44) & rotl(s4,5)) ^ rotl(s4,26) ^ rotl(s4,58);
    assign out = s5 ^ rotl(key, 13);
endmodule
