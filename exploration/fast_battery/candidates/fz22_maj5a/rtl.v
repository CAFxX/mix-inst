// fz22_maj5a: gen_fused22.py
module fz22_maj5a(
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
    function [63:0] maj;
        input [63:0] a; input [63:0] b; input [63:0] c;
        begin
            maj = (a & b) | (a & c) | (b & c);
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [63:0] x1 = x0 ^ maj(x0, rotl(x0,1), rotl(x0,7)) ^ rotl(x0,13);
    wire [63:0] x2 = x1 ^ maj(x1, rotl(x1,3), rotl(x1,11)) ^ rotl(x1,19);
    wire [63:0] x3 = x2 ^ maj(x2, rotl(x2,5), rotl(x2,15)) ^ rotl(x2,25);
    wire [63:0] x4 = x3 ^ maj(x3, rotl(x3,9), rotl(x3,21)) ^ rotl(x3,31);
    wire [63:0] x5 = x4 ^ maj(x4, rotl(x4,13), rotl(x4,27)) ^ rotl(x4,37);
    assign out = x5 ^ rotl(key, 13);
endmodule
