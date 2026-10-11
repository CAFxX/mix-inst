// smoke: trivial 2-gate design (AND2 -> XOR2) for S0 infra verification
module smoke2(input [63:0] a, input [63:0] b, output [63:0] y);
  wire [63:0] t = a & b;
  assign y = t ^ a;
endmodule
