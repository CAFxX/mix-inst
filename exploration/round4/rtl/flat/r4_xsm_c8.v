// Flat single-module build of r4_xsm_c8 (from r4_xsm.v);
// parameters: {'C': "64'h8080808080808001", 'S1': '31', 'S2': '28', 'SL': '23', 'S3': '30'}
module r4_xsm_c8 (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    wire [63:0] x0 = val ^ key;
    wire [63:0] rk1 = {key[50:0], key[63:51]} ^ 64'h9E3779B97F4A7C15;
    wire [63:0] rk2 = {key[37:0], key[63:38]} ^ 64'h3C6EF372FE94F82A;
    wire [63:0] s1 = x0 ^ (x0 >> 31);
    wire [63:0] m1 = s1 * 64'h8080808080808001;
    wire [63:0] s2 = m1 ^ rk1;
    wire [63:0] s3 = s2 ^ (s2 >> 28);
    wire [63:0] s4 = s3 ^ (s3 << 23);
    wire [63:0] s5 = s4 ^ rk2;
    assign out = s5 ^ (s5 >> 30);
endmodule
