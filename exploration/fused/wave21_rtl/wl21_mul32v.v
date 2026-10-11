// wl21_mul32v: fused wave-21 word-level op probe (gen_fused21.py)
module wl21_mul32v(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] o
);
    wire [31:0] t = v[31:0] * k[31:0];
        wire [63:0] raw = {t ^ k[63:32], t};
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
