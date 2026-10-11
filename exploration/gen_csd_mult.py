"""Probe: hand-built CSD (canonical signed digit) constant multiplier.

The -fast flow maps behavioral `a * C` (C dense 64-bit) to ~46 units (0.94x)
because ABC -fast does no Booth/CSD recoding. This probe builds the multiply
as an explicit balanced adder tree over CSD partial products, i.e. the RTL a
designer would write, and measures what the SAME flow gives it.

CSD: C = sum sign_i * 2^shift_i  =>  a*C = sum sign_i * (a << shift_i) (mod 2^64).
"""
import subprocess, sys, os

C = 0xBF58476D1CE4E5B9


def csd_encode(c):
    terms = []  # (shift, sign)
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


def gen_verilog(c, modname):
    terms = csd_encode(c)
    assert sum(s * (1 << sh) for sh, s in terms) == c, "CSD wrong"
    L = []
    L.append(f"module {modname} (input wire [63:0] a, output wire [63:0] p);")
    for j, (sh, s) in enumerate(terms):
        expr = f"(a << {sh})" if s > 0 else f"-(a << {sh})"
        L.append(f"  wire [63:0] t{j} = {expr};")
    level, cur = 0, [f"t{j}" for j in range(len(terms))]
    while len(cur) > 1:
        nxt = []
        for j in range(0, len(cur) - 1, 2):
            w = f"s{level}_{j//2}"
            L.append(f"  wire [63:0] {w} = {cur[j]} + {cur[j+1]};")
            nxt.append(w)
        if len(cur) % 2:
            nxt.append(cur[-1])
        cur, level = nxt, level + 1
    L.append(f"  assign p = {cur[0]};")
    L.append("endmodule")
    return "\n".join(L) + "\n", len(terms)


if __name__ == "__main__":
    v, nterms = gen_verilog(C, "p_mul64csd")
    print(f"CSD terms for {C:#x}: {nterms}")
    os.makedirs("prim", exist_ok=True)
    open("prim/csd_mult.v", "w").write(v)
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
    from run_synth import synth_one
    r = synth_one("prim/csd_mult.v", "p_mul64csd", "prim/w_csd")
    print(f"CSD mult: crit={r['crit']:.1f} ratio={r['crit']/49.2:.3f} cells={r['cells']}")
    # equivalence vs behavioral (model check)
    import numpy as np
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
    terms = csd_encode(C)
    rng = np.random.default_rng(5)
    A = rng.integers(0, 2**64, size=1000, dtype=np.uint64)
    M = np.uint64(0xFFFFFFFFFFFFFFFF)
    acc = np.zeros(1000, dtype=np.uint64)
    for sh, s in terms:
        t = ((A << np.uint64(sh)) & M) if sh < 64 else np.zeros(1000, dtype=np.uint64)
        acc = (acc + t) & M if s > 0 else (acc - t) & M
    ref = (A * np.uint64(C)) & M
    assert (acc == ref).all(), "CSD model != behavioral mult"
    print("CSD model == behavioral a*C on 1000 values: OK")
