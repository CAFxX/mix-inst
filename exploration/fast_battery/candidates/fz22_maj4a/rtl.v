// fz22_maj4a
module fz22_maj4a(
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
    wire [63:0] x2 = x1 ^ maj(x1, rotl(x1,5), rotl(x1,15)) ^ rotl(x1,25);
    wire [63:0] x3 = x2 ^ maj(x2, rotl(x2,11), rotl(x2,23)) ^ rotl(x2,37);
    wire [63:0] x4 = x3 ^ maj(x3, rotl(x3,17), rotl(x3,31)) ^ rotl(x3,47);
    assign out = x4;
endmodule
