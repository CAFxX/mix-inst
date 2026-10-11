// wl22_cs1stage_maj3: isolated MAJ3 cost
module wl22_cs1stage_maj3(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] o
);
    wire [63:0] ra = {v[62:0], v[63]};
    wire [63:0] m = (v & k) | (v & ra) | (k & ra);
    wire [63:0] raw = {m[62:0], m[63]};
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
