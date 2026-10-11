// Reference 64x64->64 unsigned multiplier for relative comparison.
module mul64 (
    input  wire [63:0] a,
    input  wire [63:0] b,
    output wire [63:0] p
);
    assign p = a * b;
endmodule
