// Batch B candidate B4: m32_1stage_b
// a = val[31:0]^key[31:0]; b = val[63:32]^key[63:32]
// a1 = a * 32'h85EBCA77; b1 = b ^ a1
// a2 = a1 ^ ROTL32(b1,7); b2 = b1 ^ ROTL32(a2,19) ^ key[63:32]
// out = {b2, a2}
module m32_1stage_b(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
  wire [31:0] a = val[31:0] ^ key[31:0];
  wire [31:0] b = val[63:32] ^ key[63:32];
  wire [31:0] a1 = a * 32'h85EBCA77;
  wire [31:0] b1 = b ^ a1;
  wire [31:0] a2 = a1 ^ {b1[24:0], b1[31:25]};            // ROTL32(b1,7)
  wire [31:0] b2 = b1 ^ {a2[12:0], a2[31:13]} ^ key[63:32]; // ROTL32(a2,19)^keyhi
  assign out = {b2, a2};
endmodule
