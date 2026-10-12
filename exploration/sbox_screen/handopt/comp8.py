#!/usr/bin/env python3
"""Composite-field 8-bit S-box generator (track-2 hand-optimization lane).

Builds S'(x) = L2(AES(L1(x))) for the AFF8 pool boxes as:

    x --A_pre--> p --[delta]--> (ah,al) --tower-inv--> (oh,ol) --[delta^-1]--> q --A_post--> y

where A_pre = delta . m1  (+ delta(c1)) and A_post = m2 . Ma . delta^-1
(+ m2(0x63) ^ c2) fuse the pool's affine maps with the field isomorphism,
so the only nonlinear core is the GF(2^4)-tower inversion:

    d  = ah^2.lam ^ ah.al ^ al^2        (in GF(2^4), poly 0x13)
    A^-1 = (ah.d^-1).t + ((ah^al).d^-1)

Field setup (all derived computationally, nothing recalled):
  GF(2^4) = GF(2)[w]/(w^4+w+1).
  GF(2^8) = GF(2^4)[t]/(t^2+t+lam), lam in GF(2^4) with Tr(lam)=1.
  delta: GF(2^8)_AES (poly 0x11B) -> composite field, found by searching
  for beta with minimal polynomial 0x11B; the isomorphism
  delta(a.b) == cmul(delta(a),delta(b)) is VERIFIED for all 65536 pairs.

Usage:
  python3 comp8.py search
      list lam candidates (Tr=1) and best-beta heuristic scores
  python3 comp8.py emit-core --lam 0xC --beta 3 --out core.v
      8-bit composite inversion core (delta -> inv -> delta^-1), no affines
  python3 comp8.py emit-box --name AFF8_06 --lam 0xC --beta 3 --out box.v
      full pool box with fused affines; model-checked vs harvest table
  python3 comp8.py model --name AFF8_06 --lam 0xC --beta 3
      print model-vs-harvest check (256/256)
"""
import argparse
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_sbox8_pool_ref as G

HARVEST = os.path.expanduser(
    "~/workspace/mix/exploration/sbox_screen/ranked_sbox8_pool_20261012.json")
MAPS = os.path.join(HERE, "affine_maps.json")

# ---------------------------------------------------------------- GF(2^4)
P4 = 0x13  # x^4 + x + 1


def gf4_mul(a, b):
    p = 0
    while b:
        if b & 1:
            p ^= a
        a <<= 1
        if a & 0x10:
            a ^= P4
        b >>= 1
    return p & 0xF


def gf4_sq(a):
    return gf4_mul(a, a)


def gf4_pow(a, e):
    r = 1
    while e:
        if e & 1:
            r = gf4_mul(r, a)
        a = gf4_mul(a, a)
        e >>= 1
    return r


def gf4_inv(a):
    return 0 if a == 0 else gf4_pow(a, 14)


def gf4_trace(a):
    return a ^ gf4_sq(a) ^ gf4_pow(a, 4) ^ gf4_pow(a, 8)


# ------------------------------------------------------- composite GF(2^8)
# element = (hi, lo); byte = hi<<4 | lo. basis: lo in <1,w,w^2,w^3>,
# hi coeffs of t.<1,w,w^2,w^3>.


def c_mul(a, b, lam):
    ah, al = a
    bh, bl = b
    ahbh = gf4_mul(ah, bh)
    return (ahbh ^ gf4_mul(ah, bl) ^ gf4_mul(al, bh),
            gf4_mul(ahbh, lam) ^ gf4_mul(al, bl))


def c_sq(a, lam):
    return c_mul(a, a, lam)


def c_pow(a, e, lam):
    r = (0, 1)
    while e:
        if e & 1:
            r = c_mul(r, a, lam)
        a = c_sq(a, lam)
        e >>= 1
    return r


def c_inv(a, lam):
    ah, al = a
    if ah == 0 and al == 0:
        return (0, 0)
    d = gf4_mul(gf4_sq(ah), lam) ^ gf4_mul(ah, al) ^ gf4_sq(al)
    di = gf4_inv(d)
    return (gf4_mul(ah, di), gf4_mul(ah ^ al, di))


def to_byte(a):
    return ((a[0] & 0xF) << 4) | (a[1] & 0xF)


def from_byte(v):
    return ((v >> 4) & 0xF, v & 0xF)


# ------------------------------------------------- AES field GF(2^8)/0x11B
def gf8_mul(a, b):
    p = 0
    while b:
        if b & 1:
            p ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
        b >>= 1
    return p & 0xFF


# ------------------------------------------------- GF(2) matrix helpers
# matrix = list of 8 ints; row r bitmask over input bits (row r bit i = M[r][i])


def mat_vec(M, v):
    o = 0
    for r in range(8):
        if bin(M[r] & v).count("1") & 1:
            o |= 1 << r
    return o


def mat_mul(A, B):
    C = []
    for r in range(8):
        row, m = 0, A[r]
        i = 0
        while m:
            if m & 1:
                row ^= B[i]
            i += 1
            m >>= 1
        C.append(row)
    return C


def mat_inv(M):
    rows = [[M[r], 1 << r] for r in range(8)]
    for c in range(8):
        piv = next(r for r in range(c, 8) if (rows[r][0] >> c) & 1)
        rows[c], rows[piv] = rows[piv], rows[c]
        for r in range(8):
            if r != c and ((rows[r][0] >> c) & 1):
                rows[r][0] ^= rows[c][0]
                rows[r][1] ^= rows[c][1]
    return [rows[r][1] for r in range(8)]


def xor_depth_est(M):
    """max over rows of ceil(log2(popcount)) -- rough XOR-tree depth."""
    import math
    return max(0 if r == 0 else math.ceil(math.log2(bin(r).count("1")))
               for r in M)


def minpoly_composite(a, lam):
    """minimal polynomial of composite-field element a over GF(2), as int
    bitmask (bit i = coeff of x^i)."""
    vecs = []
    p = (0, 1)
    for _ in range(9):
        vecs.append(to_byte(p))
        p = c_mul(p, a, lam)
    # incremental basis insertion; first dependent vecs[d] gives the minpoly
    basis = {}  # lead-bit -> (vec, coeffmask over vecs indices)
    for d in range(9):
        v, c = vecs[d], (1 << d)
        while v:
            lb = v.bit_length() - 1
            if lb in basis:
                v ^= basis[lb][0]
                c ^= basis[lb][1]
            else:
                break
        if v == 0:
            # sum_i c_i vecs[i] = 0 with c_d = 1 -> polynomial = c
            assert (c >> d) & 1
            return c
        basis[v.bit_length() - 1] = (v, c)
    raise AssertionError("no minpoly found")


def find_isomorphisms(lam):
    """all beta in composite field with minpoly 0x11B.

    NOTE: 0x11B is irreducible but NOT primitive (roots have order 51),
    so no order pre-filtering -- the minpoly test alone is exact.
    """
    out = []
    for v in range(1, 256):
        a = from_byte(v)
        if minpoly_composite(a, lam) == 0x11B:
            out.append(a)
    return out


def delta_matrix(beta, lam):
    """8x8 matrix: column i = coords(beta^i). out[r] = XOR_i M[r][i].x[i]."""
    M = [0] * 8
    p = (0, 1)
    for i in range(8):
        v = to_byte(p)
        for r in range(8):
            if (v >> r) & 1:
                M[r] |= 1 << i
        p = c_mul(p, beta, lam)
    return M


def verify_isomorphism(M, lam):
    for a in range(256):
        da = mat_vec(M, a)
        for b in range(256):
            if mat_vec(M, gf8_mul(a, b)) != to_byte(
                    c_mul(from_byte(da), from_byte(mat_vec(M, b)), lam)):
                return False, (a, b)
    return True, None


# AES affine matrix Ma: y_i = x_i^x_{i+4}^x_{i+5}^x_{i+6}^x_{i+7}
def aes_affine_mat():
    M = []
    for r in range(8):
        row = 0
        for i in (r, (r + 4) % 8, (r + 5) % 8, (r + 6) % 8, (r + 7) % 8):
            row |= 1 << i
        M.append(row)
    return M


MA = aes_affine_mat()
C63 = 0x63


def build_box(name, lam, beta):
    """Return (verilog_str, model_fn). model_fn(x)->y verified vs harvest."""
    maps = json.load(open(MAPS))[name]
    harv = {}
    for rec in json.load(open(HARVEST))["records"]:
        harv[rec["name"]] = bytes.fromhex(rec["table"])
    table = harv[name]
    aes = G.aes_sbox()

    m1, c1, m2, c2 = maps["m1"], maps["c1"], maps["m2"], maps["c2"]
    D = delta_matrix(beta, lam)
    Di = mat_inv(D)

    A_pre = mat_mul(D, m1)
    c_pre = mat_vec(D, c1)
    A_post = mat_mul(m2, mat_mul(MA, Di))
    c_post = mat_vec(m2, C63) ^ c2

    def model(x):
        p = mat_vec(A_pre, x) ^ c_pre
        oh, ol = c_inv(from_byte(p), lam)
        q = (oh << 4) | ol
        return mat_vec(A_post, q) ^ c_post

    # full verification against the harvest table AND the pool definition
    for x in range(256):
        y = model(x)
        assert y == table[x], f"model!=harvest at x={x:#04x}"
        ref = G._apply_affine(aes[G._apply_affine(x, m1, c1)], m2, c2)
        assert y == ref, f"model!=pooldef at x={x:#04x}"
    return A_pre, c_pre, A_post, c_post, lam


def v_affine_assigns(lhs, M, c, rhs):
    lines = []
    for r in range(8):
        terms = f"({rhs} & 8'h{M[r]:02x})"
        inv = (c >> r) & 1
        lines.append(f"assign {lhs}[{r}] = ^({terms})"
                     + (f" ^ 1'b1;" if inv else ";"))
    return lines


def emit_box(name, lam, beta):
    A_pre, c_pre, A_post, c_post, lam = build_box(name, lam, beta)
    inv4 = [gf4_inv(d) for d in range(16)]
    L = []
    L.append(f"// {name}: composite-field S-box, lam=0x{lam:x}")
    L.append(f"// S'(x) = L2(AES(L1(x))); affines fused with field isomorphism.")
    L.append(f"// generated by comp8.py -- do not hand-edit")
    L.append(f"module {name.lower()} (input [7:0] x, output [7:0] y);")
    L.append("  wire [7:0] p;")
    L += ["  " + s for s in v_affine_assigns("p", A_pre, c_pre, "x")]
    L.append("  wire [3:0] ah = p[7:4];")
    L.append("  wire [3:0] al = p[3:0];")
    L.append("  wire [3:0] ah2 = gf4_mul(ah, ah);")
    L.append("  wire [3:0] al2 = gf4_mul(al, al);")
    L.append(f"  wire [3:0] d = gf4_mul(ah2, 4'h{lam:x}) ^ gf4_mul(ah, al) ^ al2;")
    L.append("  wire [3:0] di = gf4_inv4(d);")
    L.append("  wire [3:0] oh = gf4_mul(ah, di);")
    L.append("  wire [3:0] ol = gf4_mul(ah ^ al, di);")
    L.append("  wire [7:0] q = {oh, ol};")
    L += ["  " + s for s in v_affine_assigns("y", A_post, c_post, "q")]
    L.append("  function [3:0] gf4_mul(input [3:0] a, b);")
    L.append("    reg [6:0] pp; integer k;")
    L.append("    begin")
    L.append("      pp = 7'b0;")
    L.append("      for (k = 0; k < 4; k = k + 1)")
    L.append("        if (b[k]) pp = pp ^ ({3'b0, a} << k);")
    L.append("      gf4_mul[3] = pp[3] ^ pp[6];")
    L.append("      gf4_mul[2] = pp[2] ^ pp[6] ^ pp[5];")
    L.append("      gf4_mul[1] = pp[1] ^ pp[5] ^ pp[4];")
    L.append("      gf4_mul[0] = pp[0] ^ pp[4];")
    L.append("    end")
    L.append("  endfunction")
    L.append("  function [3:0] gf4_inv4(input [3:0] d);")
    L.append("    case (d)")
    for dd in range(16):
        L.append(f"      4'h{dd:x}: gf4_inv4 = 4'h{inv4[dd]:x};")
    L.append("    endcase")
    L.append("  endfunction")
    L.append("endmodule")
    return "\n".join(L) + "\n"


def emit_core(lam, beta):
    D = delta_matrix(beta, lam)
    Di = mat_inv(D)
    inv4 = [gf4_inv(d) for d in range(16)]
    L = []
    L.append(f"// composite inversion core: delta -> tower inv -> delta^-1")
    L.append(f"// lam=0x{lam:x}")
    L.append(f"module comp8_core (input [7:0] x, output [7:0] y);")
    L.append("  wire [7:0] p;")
    L += ["  " + s for s in v_affine_assigns("p", D, 0, "x")]
    L.append("  wire [3:0] ah = p[7:4];")
    L.append("  wire [3:0] al = p[3:0];")
    L.append("  wire [3:0] ah2 = gf4_mul(ah, ah);")
    L.append("  wire [3:0] al2 = gf4_mul(al, al);")
    L.append(f"  wire [3:0] d = gf4_mul(ah2, 4'h{lam:x}) ^ gf4_mul(ah, al) ^ al2;")
    L.append("  wire [3:0] di = gf4_inv4(d);")
    L.append("  wire [3:0] oh = gf4_mul(ah, di);")
    L.append("  wire [3:0] ol = gf4_mul(ah ^ al, di);")
    L.append("  wire [7:0] q = {oh, ol};")
    L += ["  " + s for s in v_affine_assigns("y", Di, 0, "q")]
    L.append("  function [3:0] gf4_mul(input [3:0] a, b);")
    L.append("    reg [6:0] pp; integer k;")
    L.append("    begin")
    L.append("      pp = 7'b0;")
    L.append("      for (k = 0; k < 4; k = k + 1)")
    L.append("        if (b[k]) pp = pp ^ ({3'b0, a} << k);")
    L.append("      gf4_mul[3] = pp[3] ^ pp[6];")
    L.append("      gf4_mul[2] = pp[2] ^ pp[6] ^ pp[5];")
    L.append("      gf4_mul[1] = pp[1] ^ pp[5] ^ pp[4];")
    L.append("      gf4_mul[0] = pp[0] ^ pp[4];")
    L.append("    end")
    L.append("  endfunction")
    L.append("  function [3:0] gf4_inv4(input [3:0] d);")
    L.append("    case (d)")
    for dd in range(16):
        L.append(f"      4'h{dd:x}: gf4_inv4 = 4'h{inv4[dd]:x};")
    L.append("    endcase")
    L.append("  endfunction")
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search")
    e = sub.add_parser("emit-core")
    e.add_argument("--lam", required=True)
    e.add_argument("--beta", type=int, default=0)
    e.add_argument("--out", required=True)
    e = sub.add_parser("emit-box")
    e.add_argument("--name", required=True)
    e.add_argument("--lam", required=True)
    e.add_argument("--beta", type=int, default=0)
    e.add_argument("--out", required=True)
    m = sub.add_parser("model")
    m.add_argument("--name", required=True)
    m.add_argument("--lam", required=True)
    m.add_argument("--beta", type=int, default=0)

    a = ap.parse_args()

    def parse_lam(s):
        return int(s, 0)

    if a.cmd == "search":
        print("lam candidates (Tr(lam)=1):")
        for lam in range(16):
            if gf4_trace(lam) != 1:
                continue
            isos = find_isomorphisms(lam)
            ok, bad = None, None
            scored = []
            for bi, beta in enumerate(isos):
                D = delta_matrix(beta, lam)
                ok, bad = verify_isomorphism(D, lam)
                assert ok, f"isomorphism failed lam={lam:#x} beta={bi}"
                Di = mat_inv(D)
                scored.append((max(xor_depth_est(D), xor_depth_est(Di)),
                              sum(bin(r).count("1") for r in D + Di), bi))
            scored.sort()
            print(f"  lam=0x{lam:x}: {len(isos)} isomorphisms; "
                  f"best beta idx {scored[0][2]} "
                  f"(xordepth~{scored[0][0]}, weight {scored[0][1]})")
    elif a.cmd == "emit-core":
        lam = parse_lam(a.lam)
        isos = find_isomorphisms(lam)
        beta = isos[a.beta]
        D = delta_matrix(beta, lam)
        ok, _ = verify_isomorphism(D, lam)
        assert ok
        open(a.out, "w").write(emit_core(lam, beta))
        print(f"wrote {a.out} (lam=0x{lam:x}, beta idx {a.beta})")
    elif a.cmd == "emit-box":
        lam = parse_lam(a.lam)
        isos = find_isomorphisms(lam)
        beta = isos[a.beta]
        v = emit_box(a.name, lam, beta)
        open(a.out, "w").write(v)
        print(f"wrote {a.out} ({a.name}, lam=0x{lam:x}, beta idx {a.beta}); "
              f"model==harvest 256/256")
    elif a.cmd == "model":
        lam = parse_lam(a.lam)
        isos = find_isomorphisms(lam)
        build_box(a.name, lam, isos[a.beta])
        print(f"{a.name}: model == harvest table 256/256, "
              f"== pool definition 256/256")


if __name__ == "__main__":
    main()
