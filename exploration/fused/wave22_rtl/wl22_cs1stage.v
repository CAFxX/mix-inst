// wl22_cs1stage: single carry-save stage cost probe
module wl22_cs1stage(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] o
);
    wire [63:0] s = v ^ k;
    wire [63:0] c = {k[50:0], k[63:51]};
    wire [63:0] ra = {s[62:0], s[63]};
    wire [63:0] rb = {c[52:0], c[63:53]};
    wire [63:0] m = (s & c) | (s & ra) | (c & ra);
    wire [63:0] sp = s ^ c ^ ra ^ rb;
    wire [63:0] cp = {m[62:0], m[63]};
    wire [63:0] raw = sp ^ cp;
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
