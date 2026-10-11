// Round 5 candidate r5_skinny
module r5_skinny
    (input wire [63:0] val, input wire [63:0] key,
     output wire [63:0] out);
    function automatic [3:0] sbox_skinny(input [3:0] x);
        reg y0, y1, y2, y3;
        begin
            y0 = (~x[0]&x[1]&~x[2]) | (~x[0]&~x[1]&x[2]&~x[3]) | (x[0]&x[1]&x[2]) | (~x[0]&~x[2]&x[3]) | (x[1]&x[3]);
            y1 = (x[0]&~x[1]&~x[3]) | (x[1]&x[2]) | (~x[0]&~x[1]&~x[2]&x[3]) | (x[0]&x[2]);
            y2 = (~x[1]&~x[2]&~x[3]) | (x[1]&x[3]) | (x[2]&x[3]);
            y3 = (~x[0]&~x[2]&~x[3]) | (x[0]&x[2]) | (x[0]&x[3]);
            sbox_skinny = {y3, y2, y1, y0};
        end
    endfunction
    function automatic [63:0] sbox16_skinny(input [63:0] x);
        begin
            sbox16_skinny = {sbox_skinny(x[63:60]), sbox_skinny(x[59:56]), sbox_skinny(x[55:52]), sbox_skinny(x[51:48]), sbox_skinny(x[47:44]), sbox_skinny(x[43:40]), sbox_skinny(x[39:36]), sbox_skinny(x[35:32]), sbox_skinny(x[31:28]), sbox_skinny(x[27:24]), sbox_skinny(x[23:20]), sbox_skinny(x[19:16]), sbox_skinny(x[15:12]), sbox_skinny(x[11:8]), sbox_skinny(x[7:4]), sbox_skinny(x[3:0])};
        end
    endfunction
    function automatic [63:0] midori_M(input [63:0] x);
        reg [3:0] n0,n1,n2,n3;
        reg [63:0] y;
        begin
            n0 = x[3:0]; n1 = x[7:4];
            n2 = x[11:8]; n3 = x[15:12];
            y[3:0]    = n1^n2^n3;
            y[7:4]   = n0^n2^n3;
            y[11:8]  = n0^n1^n3;
            y[15:12] = n0^n1^n2;
            n0 = x[19:16]; n1 = x[23:20];
            n2 = x[27:24]; n3 = x[31:28];
            y[19:16]    = n1^n2^n3;
            y[23:20]   = n0^n2^n3;
            y[27:24]  = n0^n1^n3;
            y[31:28] = n0^n1^n2;
            n0 = x[35:32]; n1 = x[39:36];
            n2 = x[43:40]; n3 = x[47:44];
            y[35:32]    = n1^n2^n3;
            y[39:36]   = n0^n2^n3;
            y[43:40]  = n0^n1^n3;
            y[47:44] = n0^n1^n2;
            n0 = x[51:48]; n1 = x[55:52];
            n2 = x[59:56]; n3 = x[63:60];
            y[51:48]    = n1^n2^n3;
            y[55:52]   = n0^n2^n3;
            y[59:56]  = n0^n1^n3;
            y[63:60] = n0^n1^n2;
            midori_M = y;
        end
    endfunction
    function automatic [63:0] shuffle(input [63:0] x);
        begin
            shuffle = {x[35:32], x[11:8], x[55:52], x[31:28], x[27:24], x[51:48], x[15:12], x[39:36], x[7:4], x[47:44], x[19:16], x[59:56], x[63:60], x[23:20], x[43:40], x[3:0]};
        end
    endfunction
    wire [63:0] xp_s1 = (val ^ key) ^ ((val ^ key) >> 12);
    wire [63:0] xp_s2 = xp_s1 ^ ((xp_s1 << 25) & 64'hFFFFFFFFFFFFFFFF);
    wire [63:0] xp = xp_s2 ^ (xp_s2 >> 27);
    wire [63:0] x0 = xp;
    wire [63:0] rk0 = {key[50:0], key[63:51]} ^ 64'h9E3779B97F4A7C15;
    wire [63:0] s0 = shuffle(midori_M(sbox16_skinny(x0 ^ rk0)));
    wire [63:0] rk1 = {key[37:0], key[63:38]} ^ 64'h3C6EF372FE94F82A;
    wire [63:0] s1 = shuffle(midori_M(sbox16_skinny(s0 ^ rk1)));
    wire [63:0] rk2 = {key[24:0], key[63:25]} ^ 64'hDAA66D2C7DDF743F;
    wire [63:0] s2 = shuffle(midori_M(sbox16_skinny(s1 ^ rk2)));
    wire [63:0] rk3 = {key[11:0], key[63:12]} ^ 64'h78DDE6E5FD29F054;
    assign out = s2 ^ rk3;
endmodule
