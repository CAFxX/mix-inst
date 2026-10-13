// Hybrid r4_h_laimassey: see r4_hybrid.py
module r4_h_laimassey
    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    // F(z) = ((z_lo*C1)^(z_hi*C2)) ^ ROTL32(z,9)
    function automatic [31:0] lmf(input [31:0] z);
        reg [31:0] p;
        begin
            p = ((z[15:0] * 16'h9E37) ^ (z[31:16] * 16'h7F4B));
            lmf = p ^ {z[22:0], z[31:23]};
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [31:0] L0 = x0[63:32];
    wire [31:0] R0 = x0[31:0];
    wire [63:0] rk0 = {key[50:0], key[63:51]} ^ 64'h9E3779B97F4A7C15;
    wire [63:0] rk1 = {key[37:0], key[63:38]} ^ 64'h3C6EF372FE94F82A;
    wire [63:0] rk2 = {key[24:0], key[63:25]} ^ 64'hDAA66D2C7DDF743F;
    wire [63:0] rk3 = {key[11:0], key[63:12]} ^ 64'h78DDE6E5FD29F054;
    wire [31:0] T0 = lmf((L0 ^ R0 ^ rk0[31:0]));
    wire [31:0] La0 = L0 ^ T0;
    wire [31:0] Ra0 = R0 ^ T0;
    wire [31:0] L1 = Ra0;
    wire [31:0] R1 = La0;
    wire [31:0] T1 = lmf((L1 ^ R1 ^ rk1[31:0]));
    wire [31:0] La1 = L1 ^ T1;
    wire [31:0] Ra1 = R1 ^ T1;
    wire [31:0] L2 = Ra1;
    wire [31:0] R2 = La1;
    wire [31:0] T2 = lmf((L2 ^ R2 ^ rk2[31:0]));
    wire [31:0] La2 = L2 ^ T2;
    wire [31:0] Ra2 = R2 ^ T2;
    wire [31:0] L3 = Ra2;
    wire [31:0] R3 = La2;
    assign out = {L3 ^ rk3[63:32], R3 ^ rk3[31:0]};
endmodule
