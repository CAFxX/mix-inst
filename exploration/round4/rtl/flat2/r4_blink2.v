// Flat unrolled r4_blink2: Blink/Midori SPN, sb=0, 2 rounds.
module r4_blink2
    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    function automatic [3:0] sbox(input [3:0] x);
        reg y0, y1, y2, y3;
        begin
            y0 = ( x[2] & ~x[0]) | (x[3] & ~x[0]) | (~x[2] & ~x[1] & x[0]);
            y1 = (x[3] & x[2] & ~x[1]) | (~x[3] & x[2] & ~x[0]) | (x[3] & ~x[2] & x[1]) | (~x[3] & x[1] & ~x[0]) | (x[3] & x[2] & x[0]);
            y2 = (x[3] & x[2] & ~x[1]) | (~x[3] & x[1] & x[0]) | (x[3] & ~x[2] & x[0]) | (x[2] & x[1] & ~x[0]);
            y3 = (x[2] & x[1]) | (x[2] & x[0]) | (x[3] & ~x[2] & ~x[0]);
            sbox = {y3, y2, y1, y0};
        end
    endfunction
    function automatic [63:0] sbox16(input [63:0] x);
        begin
            sbox16 = {sbox(x[63:60]), sbox(x[59:56]), sbox(x[55:52]), sbox(x[51:48]), sbox(x[47:44]), sbox(x[43:40]), sbox(x[39:36]), sbox(x[35:32]), sbox(x[31:28]), sbox(x[27:24]), sbox(x[23:20]), sbox(x[19:16]), sbox(x[15:12]), sbox(x[11:8]), sbox(x[7:4]), sbox(x[3:0])};
        end
    endfunction
    function automatic [15:0] mixcol(input [15:0] c);
        reg [3:0] n0, n1, n2, n3;
        begin
            n0 = c[3:0]; n1 = c[7:4]; n2 = c[11:8]; n3 = c[15:12];
            mixcol = {(n0^n1^n2), (n0^n1^n3), (n0^n2^n3), (n1^n2^n3)};
        end
    endfunction
    function automatic [63:0] midori_M(input [63:0] x);
        begin
            midori_M = {mixcol(x[63:48]), mixcol(x[47:32]),
                        mixcol(x[31:16]), mixcol(x[15:0])};
        end
    endfunction
    function automatic [63:0] shuffle(input [63:0] x);
        begin
            shuffle = {x[35:32], x[11:8], x[55:52], x[31:28], x[27:24], x[51:48], x[15:12], x[39:36], x[7:4], x[47:44], x[19:16], x[59:56], x[63:60], x[23:20], x[43:40], x[3:0]};
        end
    endfunction
    wire [63:0] rk0 = {key[50:0], key[63:51]} ^ 64'h9E3779B97F4A7C15;
    wire [63:0] rk1 = {key[37:0], key[63:38]} ^ 64'h3C6EF372FE94F82A;
    wire [63:0] rk2 = {key[24:0], key[63:25]} ^ 64'hDAA66D2C7DDF743F;
    wire [63:0] s0 = val ^ key;
    wire [63:0] s1 = shuffle(midori_M(sbox16(s0 ^ rk0)));
    wire [63:0] s2 = shuffle(midori_M(sbox16(s1 ^ rk1)));
    assign out = s2 ^ rk2;
endmodule
