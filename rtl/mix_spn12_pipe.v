// ============================================================================
// mix_spn12_pipe.v — pipelined datapath for the RISC-V `mix` instruction.
//
//   mix rd, rs1(val), rs2(key)   ->   rd = MIX12(rs1, rs2)
//
// Same 12-round SPN as mix_spn12 (xor round-key -> 16x PRESENT S-box ->
// pLayer per round, final whitening), but with one pipeline register per
// round boundary:
//
//   latency    = 12 cycles (input sampled -> result registered)
//   throughput = 1 result per cycle (fully feed-forward, no stalls)
//
// The round functions (rotl64/player/rc/rkey) are duplicated here verbatim
// from mix_spn12.v so that file stays untouched; the S-box module `sbox4`
// is shared (compile both files together). Equivalence pipe-vs-combinational
// is checked by tb_pipe.v.
// ============================================================================

module mix_spn12_pipe #(
    parameter ROUNDS = 12
) (
    input  wire        clk,
    input  wire        rst_n,      // synchronous, active-low
    input  wire        valid_in,   // 1 = val/key are a new request this cycle
    input  wire [63:0] val,
    input  wire [63:0] key,
    output reg  [63:0] out,        // result, valid when valid_out = 1
    output wire        valid_out   // 1 = out holds a result this cycle
);

    // ---- round functions (identical to mix_spn12.v) -------------------------
    function automatic [63:0] rotl64 (input [63:0] v, input [5:0] r);
        rotl64 = (r == 6'd0) ? v : ((v << r) | (v >> (64 - r)));
    endfunction

    function automatic [63:0] player (input [63:0] v);
        integer i;
        begin
            for (i = 0; i < 63; i = i + 1)
                player[(16*i)%63] = v[i];
            player[63] = v[63];
        end
    endfunction

    function automatic [63:0] rc (input integer i);
        rc = (i + 1) * 64'h9e3779b97f4a7c15;
    endfunction

    function automatic [63:0] rkey (input [63:0] k, input integer i);
        rkey = rotl64(k, ((13*(i+1)) % 64)) ^ rc(i);
    endfunction

    // ---- pipeline registers ------------------------------------------------
    // d[g]/k[g]: data/key entering round g (g = 0..ROUNDS-1). d[ROUNDS-1]
    // feeds the last round whose whitened result is registered into `out`.
    reg [63:0] d [0:ROUNDS-1];
    reg [63:0] k [0:ROUNDS-1];
    reg [ROUNDS:0] v;   // valid shift register; valid_out = v[ROUNDS]

    assign valid_out = v[ROUNDS];

    // ---- one round of combinational logic per stage ------------------------
    // s_next_arr[g] = output of round g (before its pipeline register)
    wire [63:0] s_next_arr [0:ROUNDS-1];
    genvar g, n;
    generate
        for (g = 0; g < ROUNDS; g = g + 1) begin : stage
            wire [63:0] sx = d[g] ^ rkey(k[g], g);
            wire [63:0] sy;
            for (n = 0; n < 16; n = n + 1) begin : sb
                sbox4 u_sbox (.x(sx[4*n +: 4]), .y(sy[4*n +: 4]));
            end
            wire [63:0] s_next = player(sy);
            assign s_next_arr[g] = s_next;
        end
    endgenerate

    integer i;
    always @(posedge clk) begin
        if (!rst_n) begin
            v   <= {(ROUNDS+1){1'b0}};
            out <= 64'h0;
            for (i = 0; i < ROUNDS; i = i + 1) begin
                d[i] <= 64'h0;
                k[i] <= 64'h0;
            end
        end else begin
            // stage 0 captures a new request every cycle: no stalls, no
            // back-pressure -> sustained throughput of 1/cycle.
            // NOTE: d[0] = val ^ key, mirroring s[0] in mix_spn12.
            d[0] <= val ^ key;
            k[0] <= key;
            for (i = 1; i < ROUNDS; i = i + 1) begin
                d[i] <= s_next_arr[i-1];
                k[i] <= k[i-1];
            end
            // last round + final whitening registered into `out`
            out <= s_next_arr[ROUNDS-1] ^ rkey(k[ROUNDS-1], ROUNDS);
            // valid bit rides the pipeline with the data
            v <= {v[ROUNDS-1:0], valid_in};
        end
    end

endmodule
