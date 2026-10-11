// wl22_cs1stage_xor4: isolated XOR4 cost
module wl22_cs1stage_xor4(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] o
);
    wire [63:0] ra = {v[62:0], v[63]};
    wire [63:0] rb = {k[52:0], k[63:53]};
    wire [63:0] raw = v ^ k ^ ra ^ rb;
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
