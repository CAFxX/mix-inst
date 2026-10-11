// 64-bit Kogge-Stone parallel-prefix adder (fast reference).
module add64_ks(input [63:0] a, b, output [63:0] y);
  wire [63:0] p = a ^ b;
  wire [63:0] g = a & b;
  wire [63:0] G [0:6];
  wire [63:0] P [0:6];
  assign G[0] = g;
  assign P[0] = p;
  genvar l, i;
  generate
    for (l = 1; l <= 6; l = l + 1) begin : lvl
      for (i = 0; i < 64; i = i + 1) begin : bit
        if (i < (1 << (l-1))) begin : passthru
          assign G[l][i] = G[l-1][i];
          assign P[l][i] = P[l-1][i];
        end else begin : combine
          assign G[l][i] = G[l-1][i] | (P[l-1][i] & G[l-1][i - (1<<(l-1))]);
          assign P[l][i] = P[l-1][i] & P[l-1][i - (1<<(l-1))];
        end
      end
    end
    for (i = 1; i < 64; i = i + 1) begin : carry
      // c[i] = group generate of bits [i-1:0]
    end
  endgenerate
  wire [63:0] c;
  assign c[0] = 1'b0;
  genvar j;
  generate
    for (j = 1; j < 64; j = j + 1) begin : carry2
      assign c[j] = G[6][j-1];
    end
  endgenerate
  assign y = p ^ c;
endmodule
