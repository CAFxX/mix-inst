#!/usr/bin/env python3
"""Fused Wave-21: word-level op cost probes.

Track 8 direction: the 64-bit constant multiply was scoped-killed at 88.7u/stage
(wave-13 probe). This wave probes the remaining word-level ops the kill explicitly
left open: 32-bit multiply (narrower), word-level add, shift-add combinations.

All probes are S0-only cost measurements (no bundles). If any primitive is cheap
enough per stage (<~5u), a fused stage gets built; otherwise scoped kills.

Probes (all: module wl21_<name>(input [63:0] v, input [63:0] k, output [63:0] o)):
  A. primitives:
    mul32c  : 32-bit CONSTANT multiply:  t = v[31:0] * 32'h9e3779b9; o = {t,t}
    mul32v  : 32-bit VARIABLE multiply:  t = v[31:0] * k[31:0];       o = {t,t}
    add64v  : 64-bit variable add:        o = v + k
    add32v  : 32-bit variable add:        o = {v[63:32], v[31:0] + k[31:0]}
    shadd1  : shift-add (1 shift):        o = (v << 7) + v
    shadd2  : shift-add (2 shifts):       o = (v << 13) + (v << 7) + v
  B. full ARX-like stages (for the record; f8_nlcarry was never ledgered):
    addrot  : o = rotl(v + k, 17)
    addrot2 : two add-rot rounds: s = rotl(v+k,17); o = rotl(s + k2, 31)
"""
import os

EXP = "/home/hatch/workspace/mix/exploration"
OUT = os.path.join(EXP, "fused", "wave21_rtl")
os.makedirs(OUT, exist_ok=True)

HDR = """// {name}: fused wave-21 word-level op probe (gen_fused21.py)
module {name}(
    input  wire [63:0] v,
    input  wire [63:0] k,
    output wire [63:0] o
);
"""

ROTL = """
    function [63:0] rotl;
        input [63:0] x;
        input integer r;
        begin
            r = r % 64;
            rotl = r ? ((x << r) | (x >> (64 - r))) : x;
        end
    endfunction
"""

BODIES = {
    "wl21_mul32c": """    wire [31:0] t = v[31:0] * 32'h9e3779b9;
        wire [63:0] raw = {t ^ k[63:32], t};
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
""",
    "wl21_mul32v": """    wire [31:0] t = v[31:0] * k[31:0];
        wire [63:0] raw = {t ^ k[63:32], t};
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
""",
    "wl21_add64v": """    assign o = v + k;
endmodule
""",
    "wl21_add32v": """        wire [63:0] raw = {v[63:32], v[31:0] + k[31:0]};
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
""",
    "wl21_shadd1": """        wire [63:0] raw = (v << 7) + v;
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
""",
    "wl21_shadd2": """    wire [63:0] s1 = (v << 13) + (v << 7);
        wire [63:0] raw = s1 + v;
    assign o = raw ^ {raw[62:0], raw[63]};
endmodule
""",
    "wl21_addrot": ROTL + """    wire [63:0] s = v + k;
    assign o = rotl(s, 17);
endmodule
""",
    "wl21_addrot2": ROTL + """    wire [63:0] s1 = rotl(v + k, 17);
    assign o = rotl(s1 + {k[31:0], k[63:32]}, 31);
endmodule
""",
}

def main():
    for name, body in BODIES.items():
        src = HDR.format(name=name) + body
        p = os.path.join(OUT, name + ".v")
        open(p, "w").write(src)
        print(f"wrote {p}")

if __name__ == "__main__":
    main()
