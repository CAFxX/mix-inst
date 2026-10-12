// r7_feist8_rksimple: 8-round Feistel, rk = rotl64(k,13(i+1)) (no constant)
module r7_feist8_rksimple(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);

function automatic [3:0] sbox_s1(input [3:0] x);
    begin
        case (x)
            4'h0: sbox_s1 = 4'h0;
            4'h1: sbox_s1 = 4'h1;
            4'h2: sbox_s1 = 4'h2;
            4'h3: sbox_s1 = 4'h4;
            4'h4: sbox_s1 = 4'h3;
            4'h5: sbox_s1 = 4'h8;
            4'h6: sbox_s1 = 4'hF;
            4'h7: sbox_s1 = 4'hC;
            4'h8: sbox_s1 = 4'h9;
            4'h9: sbox_s1 = 4'h5;
            4'hA: sbox_s1 = 4'hB;
            4'hB: sbox_s1 = 4'h6;
            4'hC: sbox_s1 = 4'h7;
            4'hD: sbox_s1 = 4'hE;
            4'hE: sbox_s1 = 4'hD;
            4'hF: sbox_s1 = 4'hA;
            default: sbox_s1 = 4'h0;
        endcase
    end
endfunction

// 32-bit Midori M: two 4-nibble columns (one per 16-bit half),
// y[i] = XOR of the other 3 nibbles in the column
function automatic [31:0] midori32(input [31:0] t);
    integer h;
    reg [3:0] nn0, nn1, nn2, nn3, p;
    begin
        midori32 = 32'h0;
        for (h = 0; h < 2; h = h + 1) begin
            nn0 = t[h*16+0 +: 4];
            nn1 = t[h*16+4 +: 4];
            nn2 = t[h*16+8 +: 4];
            nn3 = t[h*16+12 +: 4];
            p = nn0 ^ nn1 ^ nn2 ^ nn3;
            midori32[h*16+0 +: 4]  = p ^ nn0;
            midori32[h*16+4 +: 4]  = p ^ nn1;
            midori32[h*16+8 +: 4]  = p ^ nn2;
            midori32[h*16+12 +: 4] = p ^ nn3;
        end
    end
endfunction

// Round key schedule
function automatic [63:0] rk(input [63:0] k, input integer i);
    integer r;
    reg [63:0] rc;
    begin
        r = (13 * (i + 1)) % 64;
        if (r == 0)
            rk = k;
        else
            rk = ((k << r) | (k >> (64 - r)));
    end
endfunction

// F-function: 2-round SPN on 32 bits
function automatic [31:0] F(input [31:0] R, input [31:0] rk32);
    reg [31:0] t;
    integer j;
    begin
        // S-box layer 1
        for (j = 0; j < 8; j = j + 1)
            t[4*j+:4] = sbox_s1(R[4*j+:4]);
        // Linear layer
        // Diffusion: x ^ rotl32(x,7) ^ rotl32(x,13)
        t = t ^ {t[24:0], t[31:25]} ^ {t[18:0], t[31:19]};
        // S-box layer 2
        for (j = 0; j < 8; j = j + 1)
            t[4*j+:4] = sbox_s1(t[4*j+:4]);
        F = t ^ rk32;
    end
endfunction

reg [31:0] L, R;
reg [31:0] Lt, Rt;
reg [63:0] rkv;
integer i;
always @(*) begin
    // Initial whitening
    L = val[63:32] ^ key[63:32];
    R = val[31:0]  ^ key[31:0];
    // Feistel rounds
    for (i = 0; i < 8; i = i + 1) begin
        rkv = rk(key, i+1);
        Lt = R;
        Rt = L ^ F(R, rkv[31:0]);
        L = Lt;
        R = Rt;
    end
end

assign out = {R, L};

endmodule
