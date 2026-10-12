#!/usr/bin/env python3
"""Generate bit-exact Verilog for a V3 MUX2 network from a stage list.

Fully unrolled: every mux input bit-select is a literal index computed in
Python as (j - r) % 64, matching v3_model.rotl (rotl(x,r)[j] = x[(j-r)%64]).

Usage: gen_v3.py <stages.json> <out.v> <top>
  stages.json: [[s,p1,p2], ...]  (one entry per stage)
"""
import json
import sys


def emit(stages, top):
    L = []
    L.append("`timescale 1ns/1ps")
    L.append(f"module {top}(input [63:0] x, input [63:0] k, output [63:0] y);")
    L.append("  wire [63:0] xk = x ^ k;")
    n = len(stages)
    for i in range(n - 1):
        L.append(f"  wire [63:0] w{i};")
    L.append("  wire [63:0] ypre;")
    prev = "xk"
    for i, (s, p1, p2) in enumerate(stages):
        out = f"w{i}" if i < n - 1 else "ypre"
        L.append(f"  // stage {i}: s={s} p1={p1} p2={p2}")
        for j in range(64):
            si = (j - s) % 64
            ai = (j - p1) % 64
            bi = (j - p2) % 64
            L.append(f"  assign {out}[{j}] = {prev}[{si}] ? {prev}[{ai}] : {prev}[{bi}];")
        prev = out
    L.append("  assign y = ypre ^ ((k << 13) | (k >> 51));")
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    stages = [tuple(st) for st in json.load(open(sys.argv[1]))]
    top = sys.argv[3]
    with open(sys.argv[2], "w") as f:
        f.write(emit(stages, top))
    print(f"wrote {sys.argv[2]}: {len(stages)} stages, top={top}")


if __name__ == "__main__":
    main()
