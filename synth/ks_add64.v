// 64-bit Kogge-Stone parallel-prefix adder — realistic fast-adder reference.
module ks_add64 (
    input  wire [63:0] a,
    input  wire [63:0] b,
    output wire [63:0] s
);
    wire [63:0] p0 = a ^ b;
    wire [63:0] g0 = a & b;

    // prefix node: (G,P) = (g2 | (p2 & g1), p2 & p1)
    // level k combines bit i with bit i - 2^k
    wire [63:0] g1, p1, g2, p2, g3, p3, g4, p4, g5, p5, g6, p6;

    genvar i;
    generate
        for (i = 0; i < 64; i = i + 1) begin : l1
            if (i >= 1) begin
                assign g1[i] = g0[i] | (p0[i] & g0[i-1]);
                assign p1[i] = p0[i] & p0[i-1];
            end else begin
                assign g1[i] = g0[i];
                assign p1[i] = p0[i];
            end
        end
        for (i = 0; i < 64; i = i + 1) begin : l2
            if (i >= 2) begin
                assign g2[i] = g1[i] | (p1[i] & g1[i-2]);
                assign p2[i] = p1[i] & p1[i-2];
            end else begin
                assign g2[i] = g1[i];
                assign p2[i] = p1[i];
            end
        end
        for (i = 0; i < 64; i = i + 1) begin : l3
            if (i >= 4) begin
                assign g3[i] = g2[i] | (p2[i] & g2[i-4]);
                assign p3[i] = p2[i] & p2[i-4];
            end else begin
                assign g3[i] = g2[i];
                assign p3[i] = p2[i];
            end
        end
        for (i = 0; i < 64; i = i + 1) begin : l4
            if (i >= 8) begin
                assign g4[i] = g3[i] | (p3[i] & g3[i-8]);
                assign p4[i] = p3[i] & p3[i-8];
            end else begin
                assign g4[i] = g3[i];
                assign p4[i] = p3[i];
            end
        end
        for (i = 0; i < 64; i = i + 1) begin : l5
            if (i >= 16) begin
                assign g5[i] = g4[i] | (p4[i] & g4[i-16]);
                assign p5[i] = p4[i] & p4[i-16];
            end else begin
                assign g5[i] = g4[i];
                assign p5[i] = p4[i];
            end
        end
        for (i = 0; i < 64; i = i + 1) begin : l6
            if (i >= 32) begin
                assign g6[i] = g5[i] | (p5[i] & g5[i-32]);
                assign p6[i] = p5[i] & p5[i-32];
            end else begin
                assign g6[i] = g5[i];
                assign p6[i] = p5[i];
            end
        end
    endgenerate

    // carry into bit i+1 is g6[i]; c[0] = 0
    wire [63:0] carry;
    assign carry[0] = 1'b0;
    generate
        for (i = 1; i < 64; i = i + 1) begin : cgen
            assign carry[i] = g6[i-1];
        end
    endgenerate

    assign s = p0 ^ carry;
endmodule
