#!/usr/bin/env python3
"""Composite-field S-box emitter v2: pure AND2/XOR2 equations (no muxes).

v1 emitted behavioral Verilog (functions with if/case); yosys inferred
mux networks that ABC could not fully clean (core measured 23.0u vs the
10.4u case-form box). v2 builds the whole circuit as an explicitly
shared AND-XOR netlist (hash-consed SSA) and emits flat assigns:

  x --A_pre--> p --delta--> (ah,al) --tower--> (oh,ol) --delta^-1--> q --A_post--> y

GF(2^4) multiply = partial-product ANDs + XOR reduction (reduction matrix
from poly 0x13 derived in Python); squaring/const-mult = linear XOR maps;
4-bit inversion = ANF (Moebius) -> AND-XOR with sharing. Affines/delta =
XOR trees.

Usage:
  python3 comp8_v2.py emit-core --lam 0xc --beta 6 --out core2.v
  python3 comp8_v2.py emit-box --name AFF8_06 --lam 0xc --beta 6 --out box2.v
  python3 comp8_v2.py stats --name AFF8_06 --lam 0xc --beta 6
      (prints AND/XOR counts and estimated XOR depth)
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import comp8 as C


class Net:
    def __init__(self):
        self.wires = []   # (name, op, args)
        self.cache = {}
        self.n = 0
        self.n_and = 0
        self.n_xor = 0
        self.n_not = 0

    def const(self, v):
        return "1'b1" if v else "1'b0"

    def _new(self, op, args):
        key = (op, args)
        if key in self.cache:
            return self.cache[key]
        self.n += 1
        name = "w%d" % self.n
        self.wires.append((name, op, args))
        self.cache[key] = name
        if op == "and":
            self.n_and += 1
        elif op == "xor":
            self.n_xor += 1
        elif op == "not":
            self.n_not += 1
        return name

    def inv(self, a):
        if a == "1'b0":
            return self.const(1)
        if a == "1'b1":
            return self.const(0)
        return self._new("not", (a,))

    def xor2(self, a, b):
        if a == b:
            return self.const(0)
        if a == "1'b0":
            return b
        if b == "1'b0":
            return a
        if a == "1'b1":
            return self.inv(b)
        if b == "1'b1":
            return self.inv(a)
        if a > b:
            a, b = b, a
        return self._new("xor", (a, b))

    def and2(self, a, b):
        if a == "1'b0" or b == "1'b0":
            return self.const(0)
        if a == "1'b1":
            return b
        if b == "1'b1":
            return a
        if a == b:
            return a
        if a > b:
            a, b = b, a
        return self._new("and", (a, b))

    def xor_tree(self, terms):
        ones = 0
        ts = []
        for t in terms:
            if t == "1'b0":
                continue
            elif t == "1'b1":
                ones ^= 1
            else:
                ts.append(t)
        while len(ts) > 1:
            nxt = []
            for i in range(0, len(ts) - 1, 2):
                nxt.append(self.xor2(ts[i], ts[i + 1]))
            if len(ts) % 2:
                nxt.append(ts[-1])
            ts = nxt
        r = ts[0] if ts else self.const(0)
        if ones:
            r = self.xor2(r, self.const(1))
        return r

    def emit(self):
        lines = []
        for name, op, args in self.wires:
            if op == "xor":
                lines.append(f"  assign {name} = {args[0]} ^ {args[1]};")
            elif op == "and":
                lines.append(f"  assign {name} = {args[0]} & {args[1]};")
            elif op == "not":
                lines.append(f"  assign {name} = ~{args[0]};")
        return lines


# ------------------------------------------------------- GF(2^4) on nets
def gf4_mul_net(N, a, b):
    pp = [[N.and2(a[i], b[j]) for j in range(4)] for i in range(4)]
    p = []
    for k in range(7):
        terms = [pp[i][j] for i in range(4) for j in range(4) if i + j == k]
        p.append(N.xor_tree(terms))
    return [N.xor_tree([p[0], p[4]]),
            N.xor_tree([p[1], p[5], p[4]]),
            N.xor_tree([p[2], p[6], p[5]]),
            N.xor_tree([p[3], p[6]])]


def gf4_sq_net(N, a):
    out = []
    for i in range(4):
        terms = [a[j] for j in range(4) if (C.gf4_sq(1 << j) >> i) & 1]
        out.append(N.xor_tree(terms))
    return out


def gf4_cmul_net(N, a, c):
    out = []
    for i in range(4):
        terms = [a[j] for j in range(4) if (C.gf4_mul(1 << j, c) >> i) & 1]
        out.append(N.xor_tree(terms))
    return out


def gf4_inv_net(N, d):
    tt = [C.gf4_inv(x) for x in range(16)]
    out = []
    for o in range(4):
        col = [(tt[x] >> o) & 1 for x in range(16)]
        anf = col[:]
        for i in range(4):
            for mask in range(16):
                if mask & (1 << i):
                    anf[mask] ^= anf[mask ^ (1 << i)]
        terms = []
        for mask in range(16):
            if anf[mask]:
                mvars = [d[i] for i in range(4) if mask & (1 << i)]
                t = mvars[0]
                for v in mvars[1:]:
                    t = N.and2(t, v)
                terms.append(t)
        # mask==0 with anf[0]==1 -> constant 1 term
        if anf[0]:
            terms.append(N.const(1))
        out.append(N.xor_tree(terms))
    return out


def affine_net(N, x8, M, c):
    out = []
    for r in range(8):
        terms = [x8[i] for i in range(8) if (M[r] >> i) & 1]
        if (c >> r) & 1:
            terms.append(N.const(1))
        out.append(N.xor_tree(terms))
    return out


def build_core_net(lam, beta, with_affines=None):
    """with_affines=None -> bare core (delta/inv/delta^-1).
    with_affines=(A_pre,c_pre,A_post,c_post) -> full box."""
    N = Net()
    x = ["x[%d]" % i for i in range(8)]
    if with_affines:
        A_pre, c_pre, A_post, c_post = with_affines
        p = affine_net(N, x, A_pre, c_pre)
    else:
        D = C.delta_matrix(beta, lam)
        p = affine_net(N, x, D, 0)
    ah, al = p[4:8], p[0:4]
    ah2 = gf4_sq_net(N, ah)
    al2 = gf4_sq_net(N, al)
    t1 = gf4_cmul_net(N, ah2, lam)
    t2 = gf4_mul_net(N, ah, al)
    d = [N.xor_tree([t1[i], t2[i], al2[i]]) for i in range(4)]
    di = gf4_inv_net(N, d)
    oh = gf4_mul_net(N, ah, di)
    apl = [N.xor2(ah[i], al[i]) for i in range(4)]
    ol = gf4_mul_net(N, apl, di)
    q = ol + oh
    if with_affines:
        y = affine_net(N, q, A_post, c_post)
    else:
        Di = C.mat_inv(C.delta_matrix(beta, lam))
        y = affine_net(N, q, Di, 0)
    return N, y


def emit_verilog(modname, N, y):
    L = [f"// {modname}: composite-field S-box, pure AND/XOR netlist (comp8_v2.py)",
         f"// AND2={N.n_and} XOR2={N.n_xor} INV={N.n_not}",
         f"module {modname} (input [7:0] x, output [7:0] y);"]
    L += N.emit()
    for i in range(8):
        L.append(f"  assign y[{i}] = {y[i]};")
    L.append("endmodule")
    return "\n".join(L) + "\n"


def get_affines(name, lam, beta):
    maps = __import__("json").load(open(C.MAPS))[name]
    m1, c1, m2, c2 = maps["m1"], maps["c1"], maps["m2"], maps["c2"]
    D = C.delta_matrix(beta, lam)
    Di = C.mat_inv(D)
    A_pre = C.mat_mul(D, m1)
    c_pre = C.mat_vec(D, c1)
    A_post = C.mat_mul(m2, C.mat_mul(C.MA, Di))
    c_post = C.mat_vec(m2, C.C63) ^ c2
    # verify against harvest (same check as comp8.build_box)
    harv = {}
    for rec in __import__("json").load(open(C.HARVEST))["records"]:
        harv[rec["name"]] = bytes.fromhex(rec["table"])
    table = harv[name]
    for xx in range(256):
        p = C.mat_vec(A_pre, xx) ^ c_pre
        oh, ol = C.c_inv(C.from_byte(p), lam)
        q = (oh << 4) | ol
        yy = C.mat_vec(A_post, q) ^ c_post
        assert yy == table[xx], f"affine verify fail at {xx:#x}"
    return A_pre, c_pre, A_post, c_post


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("emit-core")
    e.add_argument("--lam", required=True)
    e.add_argument("--beta", type=int, default=0)
    e.add_argument("--out", required=True)
    e = sub.add_parser("emit-box")
    e.add_argument("--name", required=True)
    e.add_argument("--lam", required=True)
    e.add_argument("--beta", type=int, default=0)
    e.add_argument("--out", required=True)
    s = sub.add_parser("stats")
    s.add_argument("--name", required=True)
    s.add_argument("--lam", required=True)
    s.add_argument("--beta", type=int, default=0)
    a = ap.parse_args()
    lam = int(a.lam, 0)
    beta = C.find_isomorphisms(lam)[a.beta]
    if a.cmd == "emit-core":
        N, y = build_core_net(lam, beta)
        open(a.out, "w").write(emit_verilog("comp8_core2", N, y))
        print(f"wrote {a.out}: AND2={N.n_and} XOR2={N.n_xor} INV={N.n_not}")
    elif a.cmd == "emit-box":
        aff = get_affines(a.name, lam, beta)
        N, y = build_core_net(lam, beta, with_affines=aff)
        open(a.out, "w").write(emit_verilog(a.name.lower(), N, y))
        print(f"wrote {a.out}: AND2={N.n_and} XOR2={N.n_xor} INV={N.n_not}; "
              f"model==harvest 256/256")
    elif a.cmd == "stats":
        aff = get_affines(a.name, lam, beta)
        N, y = build_core_net(lam, beta, with_affines=aff)
        print(f"{a.name} lam=0x{lam:x}: AND2={N.n_and} XOR2={N.n_xor} "
              f"INV={N.n_not} wires={N.n}")


if __name__ == "__main__":
    main()
