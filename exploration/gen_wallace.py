"""Wallace-tree (carry-save) CSD constant multiplier generator.

A 64-bit multiply by an odd constant C, built as:
  1. CSD-encode C -> T signed partial products (a << shift), negated if sign<0.
  2. Reduce the T vectors with an explicit Wallace tree of 3:2 carry-save
     compressors (bitwise FA logic: s = x^y^z, cout = majority, carry << 1).
  3. One final 64-bit carry-propagate addition of the last two vectors.

Unlike the CPA-tree in gen_csd_mult.py (which ABC maps as full CPAs per tree
node -> 67.1 units), the carry-save tree keeps intermediate additions
carry-free; only the final CPA propagates. This is the structure a designer
would hand-instantiate, and the one the -fast flow prices most fairly.

Bijectivity: C must be ODD (asserted); then a -> a*C mod 2^64 is a permutation.
"""
import os
import numpy as np


def csd_encode(c):
    terms = []
    n, i = c, 0
    while n:
        if n & 1:
            if n & 3 == 3:
                terms.append((i, -1))
                n = (n + 1) // 2
            else:
                terms.append((i, +1))
                n = n // 2
        else:
            n = n // 2
        i += 1
    return terms


def gen_wallace_verilog(c, modname):
    assert c & 1, "constant must be odd for bijectivity"
    terms = csd_encode(c)
    assert sum(s * (1 << sh) for sh, s in terms) == c, "CSD wrong"
    L = [f"module {modname} (input wire [63:0] a, output wire [63:0] p);"]
    vecs = []
    for j, (sh, s) in enumerate(terms):
        w = f"pp{j}"
        if s > 0:
            L.append(f"  wire [63:0] {w} = (a << {sh});")
        else:
            L.append(f"  wire [63:0] {w} = -(a << {sh});")
        vecs.append(w)
    lvl = 0
    while len(vecs) > 2:
        nxt = []
        i = 0
        while i + 2 < len(vecs):
            x, y, z = vecs[i], vecs[i + 1], vecs[i + 2]
            s = f"ws{lvl}_{i//3}"
            co = f"wc{lvl}_{i//3}"
            L.append(f"  wire [63:0] {s} = {x} ^ {y} ^ {z};")
            L.append(f"  wire [63:0] {co} = (({x} & {y}) | ({y} & {z}) | ({x} & {z})) << 1;")
            nxt += [s, co]
            i += 3
        nxt += vecs[i:]
        vecs, lvl = nxt, lvl + 1
    assert len(vecs) == 2, vecs
    L.append(f"  assign p = {vecs[0]} + {vecs[1]};")
    L.append("endmodule")
    return "\n".join(L) + "\n", len(terms), lvl


def wallace_model(a, c):
    """Numpy model of the Wallace CSD multiply (== (a*c) mod 2^64)."""
    terms = csd_encode(c)
    M = np.uint64(0xFFFFFFFFFFFFFFFF)
    acc = np.zeros_like(np.asarray(a, dtype=np.uint64))
    A = np.asarray(a, dtype=np.uint64)
    for sh, s in terms:
        t = ((A << np.uint64(sh)) & M) if sh < 64 else np.zeros_like(A)
        acc = ((acc + t) & M) if s > 0 else ((acc - t) & M)
    return acc


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
    from run_synth import synth_one
    os.environ["PATH"] = "/home/hatch/workspace/mix/exploration/bin:" + os.environ["PATH"]

    consts = {
        # dense splitmix constant (23 CSD terms)
        "wmult_dense": 0xBF58476D1CE4E5B9,
        # sparse 4-term odd constants
        "wmult_sp4a": (1 << 40) + (1 << 23) - (1 << 11) + 1,
        "wmult_sp4b": (1 << 48) - (1 << 29) + (1 << 13) + 1,
        # sparse 6-term odd constants
        "wmult_sp6a": (1 << 55) + (1 << 41) - (1 << 27) + (1 << 13) - (1 << 5) + 1,
        "wmult_sp6b": (1 << 60) - (1 << 47) + (1 << 33) - (1 << 19) + (1 << 7) + 1,
    }
    # reference: remeasure the CPA-tree CSD mult and behavioral const mult
    print("=== reference: CPA-tree CSD mult (prim/csd_mult.v) ===")
    r = synth_one("prim/csd_mult.v", "p_mul64csd", "prim/w_csd_r2")
    print(f"CPA-tree CSD: crit={r['crit']:.1f} cells={r['cells']}")
    print("=== reference: behavioral 64-bit const mult ===")
    with open("/tmp/behav_mult.v", "w") as f:
        f.write("module behav_mult(input wire [63:0] a, output wire [63:0] p);\n"
                "  assign p = a * 64'hBF58476D1CE4E5B9;\nendmodule\n")
    r = synth_one("/tmp/behav_mult.v", "behav_mult", "prim/w_behav")
    print(f"behavioral const-mult: crit={r['crit']:.1f} cells={r['cells']}")
    for name, c in consts.items():
        v, nterms, lvls = gen_wallace_verilog(c, name)
        fn = f"prim/{name}.v"
        open(fn, "w").write(v)
        # model check vs behavioral
        rng = np.random.default_rng(5)
        A = rng.integers(0, 2**64, size=2000, dtype=np.uint64)
        ref = (A * np.uint64(c)) & np.uint64(0xFFFFFFFFFFFFFFFF)
        assert (wallace_model(A, c) == ref).all(), f"{name} model mismatch"
        r = synth_one(fn, name, f"prim/w_{name}")
        print(f"{name}: C={c:#x} terms={nterms} levels={lvls} "
              f"crit={r['crit']:.1f} cells={r['cells']} model=OK")
