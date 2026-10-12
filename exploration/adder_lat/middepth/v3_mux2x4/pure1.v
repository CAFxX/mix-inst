`timescale 1ns/1ps
module pure1(input [63:0] x, output [63:0] y);
  genvar j;
  generate
    for (j=0; j<64; j=j+1) begin : b
      // stage (0,7,29): sel=x[j], a=x[j-7], b=x[j-29]
      assign y[j] = x[j] ? x[(j-7+64)%64] : x[(j-29+64)%64];
    end
  endgenerate
endmodule
