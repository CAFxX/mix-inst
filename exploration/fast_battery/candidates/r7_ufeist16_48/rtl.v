// r7_ufeist16_48: unbalanced Feistel, L=16 / R=48, 8 rounds.
// Bit-exact vs round7/models/r7d.py (r7_ufeist16_48_np) and candidates/.../impl.c.
// Round: newL = (R>>32)&0xFFFF,
//        newR = (((R&0xFFFFFFFF)<<16) | ((L ^ F(R))&0xFFFF)) & 48'hFFFFFFFFFFFF.
// F: 48->16: S1 on 12 nibbles -> xor-fold 48->16 -> x^rotl16(x,3)^rotl16(x,7)
//   -> ^rk16 (low 16 bits of rk64).
module r7_ufeist16_48(
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

// Round key: rotl(k, 13*(i+1)) XOR ((i+1)*0x9E3779B97F4A7C15)
function automatic [63:0] rk(input [63:0] k, input integer i);
    integer r;
    reg [63:0] rc;
    begin
        r = (13 * (i + 1)) % 64;
        rc = (i + 1) * 64'h9E3779B97F4A7C15;
        if (r == 0)
            rk = k ^ rc;
        else
            rk = ((k << r) | (k >> (64 - r))) ^ rc;
    end
endfunction

// F-function: 48 -> 16 bits
function automatic [15:0] F(input [47:0] R, input [15:0] rk16);
    reg [47:0] s;
    reg [15:0] f;
    integer j;
    begin
        // S1 on 12 nibbles
        for (j = 0; j < 12; j = j + 1)
            s[4*j+:4] = sbox_s1(R[4*j+:4]);
        // xor-fold 48 -> 16
        f = s[47:32] ^ s[31:16] ^ s[15:0];
        // linear: f ^ rotl16(f,3) ^ rotl16(f,7)
        f = f ^ {f[12:0], f[15:13]} ^ {f[8:0], f[15:9]};
        F = f ^ rk16;
    end
endfunction

reg [15:0] L;
reg [47:0] R;
reg [15:0] Lt;
reg [47:0] Rt;
reg [63:0] rkv;
integer i;
always @(*) begin
    // Initial whitening: val ^ key, L = high 16, R = low 48
    L = val[63:48] ^ key[63:48];
    R = val[47:0]  ^ key[47:0];
    // Unbalanced Feistel rounds
    for (i = 0; i < 8; i = i + 1) begin
        rkv = rk(key, i+1);
        Lt = R[47:32];
        Rt = {R[31:0], L ^ F(R, rkv[15:0])};
        L = Lt;
        R = Rt;
    end
end

assign out = {L, R};

endmodule
