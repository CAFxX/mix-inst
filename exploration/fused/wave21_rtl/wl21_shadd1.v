// wl21_shadd1: fused wave-21 word-level op probe (gen_fused21.py)
module wl21_shadd1(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] o
);
        wire [63:0] raw = (v << 7) + v;
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
