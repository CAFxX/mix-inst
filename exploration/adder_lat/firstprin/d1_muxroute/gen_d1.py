#!/usr/bin/env python3
"""Generate Direction-1 MUX-routing stage Verilog (see DESIGN.md).

Variants (single stage unless noted):
  A : 4:1 MUX, s0=(a&b)^c^k0, s1=(d&e)^f^k1   (task's literal design)
  B : 2:1 MUX, s=a^b^(c&k)                     (task's fallback)
  C : 2:1 MUX, s=(a&b)^c
  D : 2:1 MUX, s=a&b                            (<4u candidate)
  E : 2:1 MUX, s=(a&b)|(c&d) via NAND-NAND
  F : 2:1 MUX, s=a^b  (linear control)
  G : 2:1 MUX, s=a|b
  2stage : two cascaded D stages, distinct taps
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

HDR = "`timescale 1ns/1ps\n"


def taps(j, *shifts):
    return ["x[(%d)%%64]" % ((j + s) % 64) for s in shifts]


def gen_A():
    # 4:1 MUX; data taps (5,23,37,51); s0 taps (11,53,29); s1 taps (7,43,17)
    L = [HDR + "module d1_A(input [63:0] x, input [63:0] k0, input [63:0] k1, output [63:0] y);"]
    for j in range(64):
        d = taps(j, 5, 23, 37, 51)
        a, b, c = taps(j, 11, 53, 29)
        e, f, g = taps(j, 7, 43, 17)
        L.append(f"  wire s0_{j} = (({a} & {b}) ^ {c} ^ k0[{j}]);")
        L.append(f"  wire s1_{j} = (({e} & {f}) ^ {g} ^ k1[{j}]);")
        L.append(f"  assign y[{j}] = s1_{j} ? (s0_{j} ? {d[3]} : {d[2]}) : (s0_{j} ? {d[1]} : {d[0]});")
    L.append("endmodule\n")
    return "\n".join(L)


SEL = {
    # (verilog expr template with a,b,c,d,k[j], taps tuple)
    "B": ("(({a} ^ {b}) ^ ({c} & k[{j}]))", (13, 51, 29, 0)),
    "C": ("(({a} & {b}) ^ {c})", (13, 51, 29, 0)),
    "D": ("({a} & {b})", (13, 51, 0, 0)),
    "E": ("(~((~({a} & {b})) & (~({c} & {d}))))", (13, 51, 29, 7)),
    "F": ("({a} ^ {b})", (13, 51, 0, 0)),
    "G": ("({a} | {b})", (13, 51, 0, 0)),
    "H": ("(~(({a} & {b}) | {c}))", (13, 51, 29, 0)),
}


def gen_2to1(vid, top, keyed, dtaps=(5, 37), stage_prefix=""):
    expr, st = SEL[vid]
    L = [HDR + f"module {top}(input [63:0] x, " +
         ("input [63:0] k, " if keyed else "") + "output [63:0] y);"]
    for j in range(64):
        d0, d1 = taps(j, *dtaps)
        a, b, c, d = taps(j, *st)
        s = expr.format(a=a, b=b, c=c, d=d, j=j)
        L.append(f"  wire {stage_prefix}s_{j} = {s};")
        L.append(f"  assign y[{j}] = {stage_prefix}s_{j} ? {d0} : {d1};")
    L.append("endmodule\n")
    return "\n".join(L)


def gen_2stage(vid="D", top="d1_2stage"):
    # two cascaded 2:1 stages; D: taps (5,37)/(13,51) then (11,29)/(3,43)
    # H: AOI21 select ~((a&b)|c), taps (5,37)/(13,51,29) then (11,29)/(3,43,7)
    cfg = {"D": dict(s1=(5, 37, 13, 51, 0), s2=(11, 29, 3, 43, 0)),
           "H": dict(s1=(5, 37, 13, 51, 29), s2=(11, 29, 3, 43, 7))}[vid]
    L = [HDR + f"module {top}(input [63:0] x, output [63:0] y);",
         "  wire [63:0] m;"]
    body1, body2 = [], []
    d0s, d1s, sa, sb, sc = cfg["s1"]
    for j in range(64):
        d0 = f"x[{(j+d0s)%64}]"; d1 = f"x[{(j+d1s)%64}]"
        a = f"x[{(j+sa)%64}]"; b = f"x[{(j+sb)%64}]"
        if vid == "D":
            body1.append(f"  assign m[{j}] = (({a} & {b}) ? {d0} : {d1});")
        else:
            c = f"x[{(j+sc)%64}]"
            body1.append(f"  assign m[{j}] = ((~(({a} & {b}) | {c})) ? {d0} : {d1});")
    d0s, d1s, sa, sb, sc = cfg["s2"]
    for j in range(64):
        d0 = f"m[{(j+d0s)%64}]"; d1 = f"m[{(j+d1s)%64}]"
        a = f"m[{(j+sa)%64}]"; b = f"m[{(j+sb)%64}]"
        if vid == "D":
            body2.append(f"  assign y[{j}] = (({a} & {b}) ? {d0} : {d1});")
        else:
            c = f"m[{(j+sc)%64}]"
            body2.append(f"  assign y[{j}] = ((~(({a} & {b}) | {c})) ? {d0} : {d1});")
    L += body1 + body2 + ["endmodule\n"]
    return "\n".join(L)


def main():
    files = {}
    files["d1_A.v"] = gen_A()
    for vid in "BCDEFGH":
        files[f"d1_{vid}.v"] = gen_2to1(vid, f"d1_{vid}", keyed=(vid == "B"))
    files["d1_2stage.v"] = gen_2stage("D", "d1_2stage")
    files["d1_2stage_H.v"] = gen_2stage("H", "d1_2stage_H")
    for name, src in files.items():
        p = os.path.join(HERE, name)
        open(p, "w").write(src)
        print("wrote", p)


if __name__ == "__main__":
    main()
