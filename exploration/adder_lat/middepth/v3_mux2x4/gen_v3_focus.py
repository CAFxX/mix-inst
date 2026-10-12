#!/usr/bin/env python3
"""Generate bit-exact Verilog for a V3 focused MUX2 network.

Input: wiring.json = {"stages": [[(s,a,b) x64], ...]} (from v3_focus.gen_wiring).
Each stage: 64 parallel `assign w[j] = x[s] ? x[a] : x[b]` with literal indices.
Key pre/post xor included (muxd2.v convention).

Usage: gen_v3_focus.py <wiring.json> <out.v> <top>
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
    for i, triples in enumerate(stages):
        assert len(triples) == 64, f"stage {i}: {len(triples)} triples"
        out = f"w{i}" if i < n - 1 else "ypre"
        L.append(f"  // stage {i}: focused wiring")
        for j, (s, a, b) in enumerate(triples):
            L.append(f"  assign {out}[{j}] = {prev}[{s}] ? {prev}[{a}] : {prev}[{b}];")
        prev = out
    L.append("  assign y = ypre ^ ((k << 13) | (k >> 51));")
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    spec = json.load(open(sys.argv[1]))
    stages = [[tuple(t) for t in st] for st in spec["stages"]]
    top = sys.argv[3]
    with open(sys.argv[2], "w") as f:
        f.write(emit(stages, top))
    print(f"wrote {sys.argv[2]}: {len(stages)} focused stages, top={top}")


if __name__ == "__main__":
    main()
