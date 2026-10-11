// Round 5 candidate r5_feistspn4: 4-round Feistel, F = 32-bit mini-SPN
module r5_feistspn4
    (input wire [63:0] val, input wire [63:0] key,
     output wire [63:0] out);
    function automatic [3:0] sbox_s1(input [3:0] x);
        reg y0, y1, y2, y3;
        begin
            y0 = (x[0]&~x[1]&~x[2]) | (~x[0]&x[2]) | (~x[0]&x[3]);
            y1 = (~x[1]&x[2]&x[3]) | (~x[0]&x[2]&~x[3]) | (~x[0]&x[1]&~x[2]) | (x[0]&x[1]&x[3]);
            y2 = (~x[1]&x[2]&x[3]) | (x[0]&x[1]&~x[3]) | (x[0]&~x[2]&x[3]) | (~x[0]&x[1]&x[2]);
            y3 = (x[0]&x[2]) | (x[1]&x[2]) | (~x[0]&~x[2]&x[3]);
            sbox_s1 = {y3, y2, y1, y0};
        end
    endfunction
    function automatic [31:0] sbox8_s1(input [31:0] x);
        begin
            sbox8_s1 = {sbox_s1(x[31:28]), sbox_s1(x[27:24]), sbox_s1(x[23:20]), sbox_s1(x[19:16]), sbox_s1(x[15:12]), sbox_s1(x[11:8]), sbox_s1(x[7:4]), sbox_s1(x[3:0])};
        end
    endfunction
    function automatic [31:0] midori32(input [31:0] x);
        reg [3:0] n0,n1,n2,n3;
        reg [31:0] y;
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
            midori32 = y;
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [31:0] L0 = x0[63:32];
    wire [31:0] R0 = x0[31:0];
    wire [63:0] rk0 = {key[50:0], key[63:51]} ^ 64'h9E3779B97F4A7C15;
    wire [63:0] rk1 = {key[37:0], key[63:38]} ^ 64'h3C6EF372FE94F82A;
    wire [63:0] rk2 = {key[24:0], key[63:25]} ^ 64'hDAA66D2C7DDF743F;
    wire [63:0] rk3 = {key[11:0], key[63:12]} ^ 64'h78DDE6E5FD29F054;
    wire [63:0] rk4 = {key[62:0], key[63:63]} ^ 64'h1715609F7C746C69;
    wire [31:0] F0 = midori32(sbox8_s1(R0 ^ rk0[31:0])) ^ rk0[31:0];
    wire [31:0] L1 = R0;
    wire [31:0] R1 = L0 ^ F0;
    wire [31:0] F1 = midori32(sbox8_s1(R1 ^ rk1[31:0])) ^ rk1[31:0];
    wire [31:0] L2 = R1;
    wire [31:0] R2 = L1 ^ F1;
    wire [31:0] F2 = midori32(sbox8_s1(R2 ^ rk2[31:0])) ^ rk2[31:0];
    wire [31:0] L3 = R2;
    wire [31:0] R3 = L2 ^ F2;
    wire [31:0] F3 = midori32(sbox8_s1(R3 ^ rk3[31:0])) ^ rk3[31:0];
    wire [31:0] L4 = R3;
    wire [31:0] R4 = L3 ^ F3;
    assign out = {L4 ^ rk4[63:32], R4 ^ rk4[31:0]};
endmodule
