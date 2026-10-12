module spn3_linonly(input [63:0] x, output [63:0] y);
    assign y = x ^ {x[56:0], x[63:57]} ^ {x[50:0], x[63:51]} ^ {x[34:0], x[63:35]} ^ {x[22:0], x[63:23]};
endmodule
