// t6_q4S4a: batch-49 q4bS4 schedule (triage z=2.61)
module t6_q4S4a(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    // Q4: mined bijective quadratic 4-bit S-box (batch-49).
    // ANF bit-exact vs the mined LUT [3,4,15,5,0,6,1,10,14,13,2,12,9,11,8,7].
    function [63:0] q4;
        input [63:0] x;
        reg [63:0] X0, X1, X2, X3, A01, A02, A12, A03, A23;
        reg [63:0] Y0, Y1, Y2, Y3;
        begin
            X0 = x & 64'h1111111111111111;
            X1 = (x >> 1) & 64'h1111111111111111;
            X2 = (x >> 2) & 64'h1111111111111111;
            X3 = (x >> 3) & 64'h1111111111111111;
            A01 = X0 & X1; A02 = X0 & X2; A12 = X1 & X2;
            A03 = X0 & X3; A23 = X2 & X3;
            Y0 = 64'h1111111111111111 ^ X0 ^ X2 ^ X3 ^ A01 ^ A02 ^ A12;
            Y1 = 64'h1111111111111111 ^ X0 ^ X2;
            Y2 = X0 ^ X1 ^ X3 ^ A01 ^ A12 ^ A03 ^ A23;
            Y3 = X1 ^ X3 ^ A01 ^ A12;
            q4 = Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3);
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [63:0] c1 = q4(x0);
    wire [63:0] x1 = c1 ^ {c1[20:0], c1[63:43]} ^ {c1[36:0], c1[63:27]};
    wire [63:0] c2 = q4(x1);
    wire [63:0] x2 = c2 ^ {c2[54:0], c2[63:9]} ^ {c2[59:0], c2[63:4]};
    wire [63:0] c3 = q4(x2);
    wire [63:0] x3 = c3 ^ {c3[11:0], c3[63:52]} ^ {c3[18:0], c3[63:45]};
    wire [63:0] c4 = q4(x3);
    wire [63:0] x4 = c4 ^ {c4[40:0], c4[63:23]} ^ {c4[14:0], c4[63:49]};
    assign out = x4 ^ {key[12:0], key[63:51]};
endmodule
