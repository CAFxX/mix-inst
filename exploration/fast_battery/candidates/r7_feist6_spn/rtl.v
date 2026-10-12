// r7_feist6_spn: 6-round Feistel, F=2r SPN (s1)
// Initial whitening: L=val[63:32]^key[63:32], R=val[31:0]^key[31:0]
module r7_feist6_spn(
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

// F-function: 2-round SPN on 32 bits
function automatic [31:0] F(input [31:0] R, input [31:0] rk32);
    reg [31:0] t;
    integer j;
    begin
        // S-box layer 1
        for (j = 0; j < 8; j = j + 1)
            t[4*j+:4] = sbox_s1(R[4*j+:4]);
        // Diffusion: rotate-xor
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
    for (i = 0; i < 6; i = i + 1) begin
        rkv = rk(key, i+1);
        Lt = R;
        Rt = L ^ F(R, rkv[31:0]);
        L = Lt;
        R = Rt;
    end
end

assign out = {R, L};

endmodule
