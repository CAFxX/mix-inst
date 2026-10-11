// wl21_add64v: fused wave-21 word-level op probe (gen_fused21.py)
module wl21_add64v(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] o
);
    assign o = v + k;
endmodule
