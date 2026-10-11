// wl21_add32v: fused wave-21 word-level op probe (gen_fused21.py)
module wl21_add32v(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] o
);
        wire [63:0] raw = {v[63:32], v[31:0] + k[31:0]};
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
