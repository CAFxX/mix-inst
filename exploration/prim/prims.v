// Primitive delay survey: each module measured standalone with the -fast flow.
module p_mul64c  (input  wire [63:0] a, output wire [63:0] p); assign p = a * 64'hBF58476D1CE4E5B9; endmodule
module p_mul64c2 (input  wire [63:0] a, output wire [63:0] p); assign p = a * 64'h94D049BB133111EB; endmodule
module p_mul32   (input  wire [31:0] a, input wire [31:0] b, output wire [31:0] p); assign p = a * b; endmodule
module p_mul32c  (input  wire [31:0] a, output wire [31:0] p); assign p = a * 32'h9E3779B1; endmodule
module p_mul16   (input  wire [15:0] a, input wire [15:0] b, output wire [15:0] p); assign p = a * b; endmodule
module p_mul16c  (input  wire [15:0] a, output wire [15:0] p); assign p = a * 16'h9E37; endmodule
module p_add32   (input  wire [31:0] a, input wire [31:0] b, output wire [31:0] s); assign s = a + b; endmodule
module p_xorshift64 (input wire [63:0] a, output wire [63:0] p); assign p = a ^ (a >> 30); endmodule
module p_arxstep (input wire [63:0] a, input wire [63:0] k, output wire [63:0] p); assign p = (a + k) ^ ((a + k) >> 30); endmodule
