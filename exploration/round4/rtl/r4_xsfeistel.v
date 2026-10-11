// Round 4, family X: 64-bit Feistel with Simon/Simeck-like AND-rotation F.
// FTYPE: 0 = simeck (r1&r5)^r2, 1 = simon (r1&r8)^r2, 2 = dbland (two AND terms).
// (L,R) -> (R, L ^ F(R) ^ rk[i]); rk[i] = ROTL32(key_lo,7*(i+1)) ^ RC32[i].
// All rotations are constant part-select concatenations (no variable shifts).
module r4_xsfeistel #(parameter FTYPE = 0, parameter ROUNDS = 10)
    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    function automatic [31:0] F32(input [31:0] h, input integer t);
        reg [31:0] r1, r2, r5, r8, r7, r13, r11;
        begin
            r1  = {h[30:0], h[31]};
            r2  = {h[29:0], h[31:30]};
            r5  = {h[26:0], h[31:27]};
            r8  = {h[23:0], h[31:24]};
            r7  = {h[24:0], h[31:25]};
            r13 = {h[18:0], h[31:19]};
            r11 = {h[20:0], h[31:21]};
            if (t == 0)      F32 = (r1 & r5) ^ r2;
            else if (t == 1) F32 = (r1 & r8) ^ r2;
            else             F32 = ((r1 & r5) ^ r2) ^ ((r7 & r13) ^ r11);
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [31:0] klo = key[31:0];
    wire [31:0] L [0:ROUNDS];
    wire [31:0] R [0:ROUNDS];
    assign L[0] = x0[63:32];
    assign R[0] = x0[31:0];
    genvar i;
    generate
        for (i = 0; i < ROUNDS; i = i + 1) begin : rnd
            localparam integer RR = (7 * (i + 1)) % 32;
            wire [31:0] rk = {klo[31-RR:0], klo[31:32-RR]} ^ ((i + 1) * 32'h9E3779B9);
            assign L[i+1] = R[i];
            assign R[i+1] = L[i] ^ F32(R[i], FTYPE) ^ rk;
        end
    endgenerate
    assign out = {L[ROUNDS], R[ROUNDS]};
endmodule

// Thin wrappers (fixed tops for the check/synth flow)
module r4_simeck_f10 (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    r4_xsfeistel #(.FTYPE(0), .ROUNDS(10)) u (.val(val), .key(key), .out(out));
endmodule
module r4_simon_f10 (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    r4_xsfeistel #(.FTYPE(1), .ROUNDS(10)) u (.val(val), .key(key), .out(out));
endmodule
module r4_simeck_f12 (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    r4_xsfeistel #(.FTYPE(0), .ROUNDS(12)) u (.val(val), .key(key), .out(out));
endmodule
module r4_dbland_f8 (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    r4_xsfeistel #(.FTYPE(2), .ROUNDS(8)) u (.val(val), .key(key), .out(out));
endmodule
