// Flat unrolled r4_simon_f10: AND-Feistel ftype=1, rounds=10.
// No arrays/generate/hierarchy: plain net names for analyze2.py.
module r4_simon_f10
    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    function automatic [31:0] F32(input [31:0] h);
        reg [31:0] r1, r8, r2;
        begin
            r1 = {h[30:0], h[31]};
            r8 = {h[23:0], h[31:24]};
            r2 = {h[29:0], h[31:30]};
            F32 = (r1 & r8) ^ r2;
        end
    endfunction
    wire [31:0] klo = key[31:0];
    wire [31:0] rk0 = {klo[24:0], klo[31:25]} ^ 32'h9E3779B9;
    wire [31:0] rk1 = {klo[17:0], klo[31:18]} ^ 32'h3C6EF372;
    wire [31:0] rk2 = {klo[10:0], klo[31:11]} ^ 32'hDAA66D2B;
    wire [31:0] rk3 = {klo[3:0], klo[31:4]} ^ 32'h78DDE6E4;
    wire [31:0] rk4 = {klo[28:0], klo[31:29]} ^ 32'h1715609D;
    wire [31:0] rk5 = {klo[21:0], klo[31:22]} ^ 32'hB54CDA56;
    wire [31:0] rk6 = {klo[14:0], klo[31:15]} ^ 32'h5384540F;
    wire [31:0] rk7 = {klo[7:0], klo[31:8]} ^ 32'hF1BBCDC8;
    wire [31:0] rk8 = {klo[0:0], klo[31:1]} ^ 32'h8FF34781;
    wire [31:0] rk9 = {klo[25:0], klo[31:26]} ^ 32'h2E2AC13A;
    wire [63:0] s0 = val ^ key;
    wire [63:0] s1 = {s0[31:0], s0[63:32] ^ F32(s0[31:0]) ^ rk0};
    wire [63:0] s2 = {s1[31:0], s1[63:32] ^ F32(s1[31:0]) ^ rk1};
    wire [63:0] s3 = {s2[31:0], s2[63:32] ^ F32(s2[31:0]) ^ rk2};
    wire [63:0] s4 = {s3[31:0], s3[63:32] ^ F32(s3[31:0]) ^ rk3};
    wire [63:0] s5 = {s4[31:0], s4[63:32] ^ F32(s4[31:0]) ^ rk4};
    wire [63:0] s6 = {s5[31:0], s5[63:32] ^ F32(s5[31:0]) ^ rk5};
    wire [63:0] s7 = {s6[31:0], s6[63:32] ^ F32(s6[31:0]) ^ rk6};
    wire [63:0] s8 = {s7[31:0], s7[63:32] ^ F32(s7[31:0]) ^ rk7};
    wire [63:0] s9 = {s8[31:0], s8[63:32] ^ F32(s8[31:0]) ^ rk8};
    wire [63:0] s10 = {s9[31:0], s9[63:32] ^ F32(s9[31:0]) ^ rk9};
    assign out = s10;
endmodule
