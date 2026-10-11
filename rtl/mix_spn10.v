// ============================================================================
// mix_spn10.v — combinational datapath for the RISC-V `mix` instruction.
//
//   mix rd, rs1(val), rs2(key)   ->   rd = MIX10(rs1, rs2)
//
// 10-round SPN: each round = xor round-key -> 16x 4-bit PRESENT S-box ->
// 64-bit pLayer (free wiring). All stages bijective => for a fixed key the
// function is a permutation of 2^64.
//
// Round keys: rk[i] = ROTL64(key, 13*(i+1) mod 64) ^ RC[i], i = 0..10
// (10 rounds + final whitening). RC[i] = (i+1) * 0x9E3779B97F4A7C15 mod 2^64.
//
// The S-box is written as minimized Boolean equations (QM-minimized SOP,
// formally verified against the PRESENT table) so synthesis infers plain
// combinational logic, not ROM.
// ============================================================================

// PRESENT 4-bit S-box, minimized SOP (verified vs table):
//   S = C 5 6 B 9 0 A D 3 E F 8 4 7 1 2
module sbox4 (
    input  wire [3:0] x,
    output wire [3:0] y
);
    assign y[0] = (~x[0] & ~x[2] & x[3]) | (~x[0] & x[1] & x[3]) |
                  (x[0] & ~x[2] & ~x[3]) | (~x[0] & ~x[1] & x[2] & ~x[3]) |
                  (x[0] & x[1] & ~x[3]) | (x[0] & ~x[1] & x[2] & x[3]);
    assign y[1] = (~x[0] & ~x[2] & x[3]) | (~x[1] & ~x[2] & x[3]) |
                  (x[0] & x[2] & x[3]) | (~x[0] & x[1] & ~x[3]) |
                  (x[1] & ~x[2] & ~x[3]);
    assign y[2] = (x[0] & ~x[1] & ~x[2]) | (x[0] & x[1] & x[2] & ~x[3]) |
                  (~x[0] & ~x[2] & ~x[3]) | (~x[0] & x[1] & ~x[2]) |
                  (~x[1] & x[2] & x[3]);
    assign y[3] = (~x[0] & x[2] & ~x[3]) | (~x[0] & ~x[1] & ~x[3]) |
                  (x[0] & x[1] & ~x[3]) | (x[1] & ~x[2] & x[3]) |
                  (x[0] & ~x[2] & x[3]);
endmodule

module mix_spn10 #(
    parameter ROUNDS = 10
) (
    input  wire [63:0] val,
    input  wire [63:0] key,
    output wire [63:0] out
);

    // (round constants computed by rc(i) below)

    // rotate left by constant amount (free wiring)
    function automatic [63:0] rotl64 (input [63:0] v, input [5:0] r);
        rotl64 = (r == 6'd0) ? v : ((v << r) | (v >> (64 - r)));
    endfunction

    // PRESENT pLayer for 64-bit block: bit i -> bit (16*i mod 63), bit 63 fixed
    function automatic [63:0] player (input [63:0] v);
        integer i;
        begin
            for (i = 0; i < 63; i = i + 1)
                player[(16*i)%63] = v[i];
            player[63] = v[63];
        end
    endfunction

    // round constant i: RC[i] = (i+1)*0x9E3779B97F4A7C15 mod 2^64
    function automatic [63:0] rc (input integer i);
        rc = (i + 1) * 64'h9e3779b97f4a7c15;
    endfunction

    // round key i (i = 0..ROUNDS-1 rounds, i = ROUNDS final whitening):
    //   rk[i] = ROTL64(key, 13*(i+1) mod 64) ^ RC[i]
    function automatic [63:0] rkey (input [63:0] k, input integer i);
        rkey = rotl64(k, ((13*(i+1)) % 64)) ^ rc(i);
    endfunction

    wire [63:0] s [0:ROUNDS];
    assign s[0] = val ^ key;

    genvar g, n;
    generate
        for (g = 0; g < ROUNDS; g = g + 1) begin : rounds
            wire [63:0] sx = s[g] ^ rkey(key, g);
            wire [63:0] sy;
            for (n = 0; n < 16; n = n + 1) begin : sb
                sbox4 u_sbox (.x(sx[4*n +: 4]), .y(sy[4*n +: 4]));
            end
            assign s[g+1] = player(sy);
        end
    endgenerate

    assign out = s[ROUNDS] ^ rkey(key, ROUNDS);

endmodule
