// fz20_a: gen_fused20.py
module fz20_a(
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
    wire [63:0] x0 = val ^ key;
    wire [63:0] ra0 = rotl(x0, 1);
    wire [63:0] rb0 = rotl(x0, 7);
    wire [63:0] rc0 = rotl(x0, 13);
    wire [63:0] and0 = ra0 & rb0;
    wire [63:0] t0a = x0 ^ ra0;
    wire [63:0] t0b = and0 ^ rc0;
    wire [63:0] x1 = t0a ^ t0b;
    wire [63:0] ra1 = rotl(x1, 3);
    wire [63:0] rb1 = rotl(x1, 11);
    wire [63:0] rc1 = rotl(x1, 19);
    wire [63:0] and1 = ra1 & rb1;
    wire [63:0] t1a = x1 ^ ra1;
    wire [63:0] t1b = and1 ^ rc1;
    wire [63:0] x2 = t1a ^ t1b;
    wire [63:0] ra2 = rotl(x2, 5);
    wire [63:0] rb2 = rotl(x2, 15);
    wire [63:0] rc2 = rotl(x2, 25);
    wire [63:0] and2 = ra2 & rb2;
    wire [63:0] t2a = x2 ^ ra2;
    wire [63:0] t2b = and2 ^ rc2;
    wire [63:0] x3 = t2a ^ t2b;
    wire [63:0] ra3 = rotl(x3, 9);
    wire [63:0] rb3 = rotl(x3, 21);
    wire [63:0] rc3 = rotl(x3, 31);
    wire [63:0] and3 = ra3 & rb3;
    wire [63:0] t3a = x3 ^ ra3;
    wire [63:0] t3b = and3 ^ rc3;
    wire [63:0] x4 = t3a ^ t3b;
    wire [63:0] ra4 = rotl(x4, 13);
    wire [63:0] rb4 = rotl(x4, 27);
    wire [63:0] rc4 = rotl(x4, 37);
    wire [63:0] and4 = ra4 & rb4;
    wire [63:0] t4a = x4 ^ ra4;
    wire [63:0] t4b = and4 ^ rc4;
    wire [63:0] x5 = t4a ^ t4b;
    wire [63:0] k13 = rotl(key, 13);
    assign out = x5 ^ k13;
endmodule
