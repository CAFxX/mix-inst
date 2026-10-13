// t6_qlowS4a: batch-50 qlowS4 schedule (triage z=3.13)
module t6_qlowS4a(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    // QLOW: probe-mined minimal-AND bijective quadratic 4-bit
    // S-box (batch-50). ANF derived from the LUT by Moebius,
    // bit-exact vs the LUT on all 16 inputs.
    function [63:0] qlow;
        input [63:0] x;
        reg [63:0] X0, X1, X2, X3;
        reg [63:0] A01;
        reg [63:0] A02;
        reg [63:0] A03;
        reg [63:0] Y0, Y1, Y2, Y3;
        begin
            X0 = x & 64'h1111111111111111;
            X1 = (x >> 1) & 64'h1111111111111111;
            X2 = (x >> 2) & 64'h1111111111111111;
            X3 = (x >> 3) & 64'h1111111111111111;
            A01 = X0 & X1;
            A02 = X0 & X2;
            A03 = X0 & X3;
            Y0 = X0;
            Y1 = 64'h1111111111111111 ^ X0 ^ A01 ^ X2 ^ X3 ^ A03;
            Y2 = X0 ^ X1 ^ A01 ^ A02 ^ A03;
            Y3 = 64'h1111111111111111 ^ X1 ^ A01 ^ X3;
            qlow = Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3);
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [63:0] c1 = qlow(x0);
    wire [63:0] x1 = c1 ^ {c1[45:0], c1[63:18]} ^ {c1[54:0], c1[63:9]};
    wire [63:0] c2 = qlow(x1);
    wire [63:0] x2 = c2 ^ {c2[28:0], c2[63:35]} ^ {c2[42:0], c2[63:21]};
    wire [63:0] c3 = qlow(x2);
    wire [63:0] x3 = c3 ^ {c3[11:0], c3[63:52]} ^ {c3[6:0], c3[63:57]};
    wire [63:0] c4 = qlow(x3);
    wire [63:0] x4 = c4 ^ {c4[9:0], c4[63:54]} ^ {c4[25:0], c4[63:38]};
    assign out = x4 ^ {key[12:0], key[63:51]};
endmodule
