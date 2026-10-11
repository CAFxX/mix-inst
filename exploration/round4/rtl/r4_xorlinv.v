// Round 4, V1: SKINNY 4-bit S-box in the 4-round xorlin structure.
// 4 rounds of (xor rk, 16x SKINNY S-box, L(x)=x^ROTL(x,11)^ROTL(x,37)) + whitening.
// rk[i] = ROTL64(key,13*(i+1)) ^ (i+1)*0x9E3779B97F4A7C15.
// All rotations are constant part-select concatenations (no variable shifts).
// SKINNY S-box: C 6 9 0 1 A 2 B 3 8 5 D 4 E 7 F.
module r4_skinny_xorlin (
    input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    function automatic [3:0] sbox(input [3:0] x);
        begin
            sbox = (x == 4'h0) ? 4'hC :
                   (x == 4'h1) ? 4'h6 :
                   (x == 4'h2) ? 4'h9 :
                   (x == 4'h3) ? 4'h0 :
                   (x == 4'h4) ? 4'h1 :
                   (x == 4'h5) ? 4'hA :
                   (x == 4'h6) ? 4'h2 :
                   (x == 4'h7) ? 4'hB :
                   (x == 4'h8) ? 4'h3 :
                   (x == 4'h9) ? 4'h8 :
                   (x == 4'hA) ? 4'h5 :
                   (x == 4'hB) ? 4'hD :
                   (x == 4'hC) ? 4'h4 :
                   (x == 4'hD) ? 4'hE :
                   (x == 4'hE) ? 4'h7 :
                   (x == 4'hF) ? 4'hF :
                   4'h0;
        end
    endfunction
    function automatic [63:0] sbox16(input [63:0] x);
        begin
            sbox16 = {sbox(x[63:60]), sbox(x[59:56]), sbox(x[55:52]), sbox(x[51:48]),
                      sbox(x[47:44]), sbox(x[43:40]), sbox(x[39:36]), sbox(x[35:32]),
                      sbox(x[31:28]), sbox(x[27:24]), sbox(x[23:20]), sbox(x[19:16]),
                      sbox(x[15:12]), sbox(x[11:8]),  sbox(x[7:4]),   sbox(x[3:0])};
        end
    endfunction
    function automatic [63:0] L64(input [63:0] x);
        begin
            L64 = x ^ {x[52:0], x[63:53]} ^ {x[26:0], x[63:27]};
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [63:0] rk0 = {key[50:0], key[63:51]} ^ 64'h9E3779B97F4A7C15;
    wire [63:0] rk1 = {key[37:0], key[63:38]} ^ 64'h3C6EF372FE94F82A;
    wire [63:0] rk2 = {key[24:0], key[63:25]} ^ 64'hDAA66D2C7DDF743F;
    wire [63:0] rk3 = {key[11:0], key[63:12]} ^ 64'h78DDE6E5FD29F054;
    wire [63:0] rk4 = {key[62:0], key[63]}    ^ 64'h1715609F7C746C69;
    wire [63:0] r0 = L64(sbox16(x0 ^ rk0));
    wire [63:0] r1 = L64(sbox16(r0 ^ rk1));
    wire [63:0] r2 = L64(sbox16(r1 ^ rk2));
    wire [63:0] r3 = L64(sbox16(r2 ^ rk3));
    assign out = r3 ^ rk4;
endmodule
