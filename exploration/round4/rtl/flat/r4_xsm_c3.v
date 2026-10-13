// Flat single-module build of r4_xsm_c3 (from r4_xsm.v);
// parameters: {'C': "64'h100000000000003F", 'S1': '33', 'S2': '27', 'SL': '17', 'S3': '29'}
module r4_xsm_c3 (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    wire [63:0] x0 = val ^ key;
    wire [63:0] rk1 = {key[50:0], key[63:51]} ^ 64'h9E3779B97F4A7C15;
    wire [63:0] rk2 = {key[37:0], key[63:38]} ^ 64'h3C6EF372FE94F82A;
    wire [63:0] s1 = x0 ^ (x0 >> 33);
    wire [63:0] m1 = s1 * 64'h100000000000003F;
    wire [63:0] s2 = m1 ^ rk1;
    wire [63:0] s3 = s2 ^ (s2 >> 27);
    wire [63:0] s4 = s3 ^ (s3 << 17);
    wire [63:0] s5 = s4 ^ rk2;
    assign out = s5 ^ (s5 >> 29);
endmodule
