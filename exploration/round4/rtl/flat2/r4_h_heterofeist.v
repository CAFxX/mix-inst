// Hybrid r4_h_heterofeist: see r4_hybrid.py
module r4_h_heterofeist
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
    function automatic [31:0] sbox8(input [31:0] x);
        begin
            sbox8 = {sbox(x[31:28]), sbox(x[27:24]), sbox(x[23:20]), sbox(x[19:16]), sbox(x[15:12]), sbox(x[11:8]), sbox(x[7:4]), sbox(x[3:0])};
        end
    endfunction
    function automatic [31:0] cchi32(input [31:0] x);
        reg [31:0] r1, r2;
        begin
            r1 = {x[30:0], x[31]};
            r2 = {x[29:0], x[31:30]};
            cchi32 = x ^ ((~r1) & r2);
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
    wire [63:0] rk5 = {key[49:0], key[63:50]} ^ 64'hB54CDA58FBBEE87E;
    wire [63:0] rk6 = {key[36:0], key[63:37]} ^ 64'h538454127B096493;
    wire [31:0] F0 = sbox8(R0 ^ rk0[31:0]);
    wire [31:0] L1 = R0;
    wire [31:0] R1 = L0 ^ F0;
    wire [31:0] F1 = cchi32(R1 ^ rk1[31:0]);
    wire [31:0] L2 = R1;
    wire [31:0] R2 = L1 ^ F1;
    wire [31:0] F2 = sbox8(R2 ^ rk2[31:0]);
    wire [31:0] L3 = R2;
    wire [31:0] R3 = L2 ^ F2;
    wire [31:0] F3 = cchi32(R3 ^ rk3[31:0]);
    wire [31:0] L4 = R3;
    wire [31:0] R4 = L3 ^ F3;
    wire [31:0] F4 = sbox8(R4 ^ rk4[31:0]);
    wire [31:0] L5 = R4;
    wire [31:0] R5 = L4 ^ F4;
    wire [31:0] F5 = cchi32(R5 ^ rk5[31:0]);
    wire [31:0] L6 = R5;
    wire [31:0] R6 = L5 ^ F5;
    assign out = {L6 ^ rk6[63:32], R6 ^ rk6[31:0]};
endmodule
