// 64x64->64 truncated multiplier reference (low 64 bits of product).
// Matches the mixer's 64-bit output width for a fair latency comparison.
module mul64_64(input [63:0] a, b, output [63:0] y);
assign y = a * b;
endmodule
