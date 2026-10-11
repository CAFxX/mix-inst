// Round 4, family M: keyed xorshift-multiply sandwich.
// x = val^key; x^=x>>S1; x*=C; x^=rk1; x^=x>>S2; x^=x<<SL; x^=rk2; x^=x>>S3.
// rk1 = ROTL64(key,13) ^ Cmult; rk2 = ROTL64(key,26) ^ 2*Cmult (Cmult=0x9E3779B97F4A7C15).
// All rotations are constant part-select concatenations (no variable shifts).
module r4_xsm #(
    parameter [63:0] C  = 64'h100000000000003F,
    parameter integer S1 = 33,
    parameter integer S2 = 27,
    parameter integer SL = 17,
    parameter integer S3 = 29
) (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    wire [63:0] x0 = val ^ key;
    wire [63:0] rk1 = {key[50:0], key[63:51]} ^ 64'h9E3779B97F4A7C15;
    wire [63:0] rk2 = {key[37:0], key[63:38]} ^ 64'h3C6EF372FE94F82A;
    wire [63:0] s1 = x0 ^ (x0 >> S1);
    wire [63:0] m1 = s1 * C;
    wire [63:0] s2 = m1 ^ rk1;
    wire [63:0] s3 = s2 ^ (s2 >> S2);
    wire [63:0] s4 = s3 ^ (s3 << SL);
    wire [63:0] s5 = s4 ^ rk2;
    assign out = s5 ^ (s5 >> S3);
endmodule

// M2: shift-ADD multiplies ((x<<13)+x, (x<<29)+x) instead of constant mult.
module r4_xsm_sa (
    input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    wire [63:0] x0 = val ^ key;
    wire [63:0] rk1 = {key[50:0], key[63:51]} ^ 64'h9E3779B97F4A7C15;
    wire [63:0] rk2 = {key[37:0], key[63:38]} ^ 64'h3C6EF372FE94F82A;
    wire [63:0] s1 = x0 ^ (x0 >> 33);
    wire [63:0] p1 = (s1 << 13) + s1;
    wire [63:0] s2 = p1 ^ rk1;
    wire [63:0] s3 = s2 ^ (s2 >> 27);
    wire [63:0] p2 = (s3 << 29) + s3;
    wire [63:0] s4 = p2 ^ rk2;
    assign out = s4 ^ (s4 >> 31);
endmodule

// Thin wrappers (fixed tops for the check/synth flow)
module r4_xsm_c3 (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    r4_xsm #(.C(64'h100000000000003F), .S1(33), .S2(27), .SL(17), .S3(29)) u (.val(val), .key(key), .out(out));
endmodule
module r4_xsm_c8 (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    r4_xsm #(.C(64'h8080808080808001), .S1(31), .S2(28), .SL(23), .S3(30)) u (.val(val), .key(key), .out(out));
endmodule
