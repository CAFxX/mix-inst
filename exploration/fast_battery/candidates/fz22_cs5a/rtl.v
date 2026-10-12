// fz22_cs5a: gen_fused22.py
module fz22_cs5a(
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
    wire [63:0] c0 = rotl(key, 13);
    wire [63:0] ra0 = rotl(s0, 1);
    wire [63:0] rb0 = rotl(c0, 11);
    wire [63:0] m0 = (s0 & c0) | (s0 & ra0) | (c0 & ra0);
    wire [63:0] s1 = s0 ^ c0 ^ ra0 ^ rb0;
    wire [63:0] c1 = rotl(m0, 1);
    wire [63:0] ra1 = rotl(s1, 7);
    wire [63:0] rb1 = rotl(c1, 19);
    wire [63:0] m1 = (s1 & c1) | (s1 & ra1) | (c1 & ra1);
    wire [63:0] s2 = s1 ^ c1 ^ ra1 ^ rb1;
    wire [63:0] c2 = rotl(m1, 1);
    wire [63:0] ra2 = rotl(s2, 13);
    wire [63:0] rb2 = rotl(c2, 29);
    wire [63:0] m2 = (s2 & c2) | (s2 & ra2) | (c2 & ra2);
    wire [63:0] s3 = s2 ^ c2 ^ ra2 ^ rb2;
    wire [63:0] c3 = rotl(m2, 1);
    wire [63:0] ra3 = rotl(s3, 17);
    wire [63:0] rb3 = rotl(c3, 37);
    wire [63:0] m3 = (s3 & c3) | (s3 & ra3) | (c3 & ra3);
    wire [63:0] s4 = s3 ^ c3 ^ ra3 ^ rb3;
    wire [63:0] c4 = rotl(m3, 1);
    wire [63:0] ra4 = rotl(s4, 23);
    wire [63:0] rb4 = rotl(c4, 43);
    wire [63:0] m4 = (s4 & c4) | (s4 & ra4) | (c4 & ra4);
    wire [63:0] s5 = s4 ^ c4 ^ ra4 ^ rb4;
    wire [63:0] c5 = rotl(m4, 1);
    wire [63:0] sc = s5 ^ c5;
    assign out = sc ^ rotl(sc, 17);
endmodule
