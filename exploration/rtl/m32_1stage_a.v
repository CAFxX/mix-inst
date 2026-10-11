// Batch B candidate B3: m32_1stage_a
// a = val[31:0]^key[31:0]; b = val[63:32]^key[63:32]
// a1 = a * 32'h9E3779B1; b1 = b ^ a1
// a2 = a1 ^ ROTL32(b1,11); b2 = b1 ^ ROTL32(a2,17) ^ key[31:0]
// out = {b2, a2}
module m32_1stage_a(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
  wire [31:0] a = val[31:0] ^ key[31:0];
  wire [31:0] b = val[63:32] ^ key[63:32];
  wire [31:0] a1 = a * 32'h9E3779B1;
  wire [31:0] b1 = b ^ a1;
  wire [31:0] a2 = a1 ^ {b1[20:0], b1[31:21]};            // ROTL32(b1,11)
  wire [31:0] b2 = b1 ^ {a2[14:0], a2[31:15]} ^ key[31:0]; // ROTL32(a2,17)^keylo
  assign out = {b2, a2};
endmodule
