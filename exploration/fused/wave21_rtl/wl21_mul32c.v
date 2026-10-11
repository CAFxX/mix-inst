// wl21_mul32c: fused wave-21 word-level op probe (gen_fused21.py)
module wl21_mul32c(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] o
);
    wire [31:0] t = v[31:0] * 32'h9e3779b9;
        wire [63:0] raw = {t ^ k[63:32], t};
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
