module f8_nlcarry(input [63:0] v, input [63:0] k, output [63:0] o);
wire [63:0] x0 = v ^ k;
wire [63:0] x1 = x0 + 64'h9e3779b97f4a7c15;
wire [63:0] x2 = x1 ^ {x1[31:0], x1[63:32]} ^ {x1[46:0], x1[63:47]};
wire [63:0] x3 = x2 + 64'h3c6ef372fe94f82a;
assign o = x3 ^ {x3[34:0], x3[63:35]} ^ {k[52:0], k[63:53]};
endmodule
