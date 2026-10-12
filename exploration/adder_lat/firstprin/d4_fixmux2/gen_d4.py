#!/usr/bin/env python3
"""Emit Verilog for D4 variants. Usage: gen_d4.py {A|C} <p1> <p2> <out.v> <top>
A: 3xMUX2 + out[i] = m[i]^m[(i-p1)]^m[(i-p2)]   (p1=r1, p2=r2)
C: 3xMUX2 + out[i] = m[i]^(m[(i-p1)]&m[(i-p2)]) (p1=a, p2=b)
Bit-index convention matches v3_model/gen_v3: rotl(x,r)[j] = x[(j-r)%64].
"""
import sys

STAGES = [(0, 7, 29), (13, 31, 53), (5, 19, 43)]

def emit(kind, p1, p2, top):
    L = []
    L.append("`timescale 1ns/1ps")
    L.append(f"module {top}(input [63:0] x, input [63:0] k, output [63:0] y);")
    L.append("  wire [63:0] xk = x ^ k;")
    L.append("  wire [63:0] w0, w1, m;")
    L.append("  wire [63:0] ypre;")
    prev = "xk"
    for i, (s, a_, b_) in enumerate(STAGES):
        out = ["w0", "w1", "m"][i]
        L.append(f"  // mux stage {i}: s={s} p1={a_} p2={b_}")
        for j in range(64):
            si = (j - s) % 64; ai = (j - a_) % 64; bi = (j - b_) % 64
            L.append(f"  assign {out}[{j}] = {prev}[{si}] ? {prev}[{ai}] : {prev}[{bi}];")
        prev = out
    L.append(f"  // diffusion stage kind={kind} p1={p1} p2={p2}")
    for j in range(64):
        j1 = (j - p1) % 64; j2 = (j - p2) % 64
        if kind == "A":
            L.append(f"  assign ypre[{j}] = m[{j}] ^ m[{j1}] ^ m[{j2}];")
        else:
            L.append(f"  assign ypre[{j}] = m[{j}] ^ (m[{j1}] & m[{j2}]);")
    L.append("  assign y = ypre ^ ((k << 13) | (k >> 51));")
    L.append("endmodule")
    return "\n".join(L) + "\n"

if __name__ == "__main__":
    kind, p1, p2, outv, top = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
    open(outv, "w").write(emit(kind, p1, p2, top))
    print(f"wrote {outv}: kind={kind} p1={p1} p2={p2} top={top}")
