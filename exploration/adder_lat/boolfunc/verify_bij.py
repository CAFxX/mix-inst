#!/usr/bin/env python3
"""Brute-force bijectivity check for Design B at small n.

Implements Stage E then Stage O exactly as in boolfunc_b.v (parameterizable n,
odd offsets a,b), applies to ALL 2^n inputs, checks all outputs distinct.
Also cross-checks the 64-bit vectorized model against a scalar reference.
"""
import numpy as np


def design_b_scalar(x, n, a, b):
    """Scalar bit-array reference. x: int with n bits."""
    inp = [(x >> i) & 1 for i in range(n)]
    e = [0] * n
    for i in range(n // 2):
        e[2 * i] = inp[2 * i] ^ (inp[(2 * i + a) % n] & inp[(2 * i + b) % n])
        e[2 * i + 1] = inp[2 * i + 1]
    out = [0] * n
    for i in range(n // 2):
        out[2 * i] = e[2 * i]
        out[2 * i + 1] = e[2 * i + 1] ^ (e[(2 * i + 1 + a) % n] & e[(2 * i + 1 + b) % n])
    return sum(bit << i for i, bit in enumerate(out))


def design_b_vec(V, n, a, b):
    """Vectorized over numpy uint64 array V."""
    V = np.asarray(V, dtype=np.uint64)
    def bit(x, p):
        return ((x >> np.uint64(p)) & np.uint64(1))
    # Stage E
    e_bits = [None] * n
    for i in range(n // 2):
        e_bits[2 * i] = bit(V, 2 * i) ^ (bit(V, (2 * i + a) % n) & bit(V, (2 * i + b) % n))
        e_bits[2 * i + 1] = bit(V, 2 * i + 1)
    e = np.zeros(np.shape(V), dtype=np.uint64)
    for p in range(n):
        e |= (e_bits[p].astype(np.uint64) << np.uint64(p))
    # Stage O
    o_bits = [None] * n
    for i in range(n // 2):
        o_bits[2 * i] = bit(e, 2 * i)
        o_bits[2 * i + 1] = bit(e, 2 * i + 1) ^ (bit(e, (2 * i + 1 + a) % n) & bit(e, (2 * i + 1 + b) % n))
    out = np.zeros(np.shape(e), dtype=np.uint64)
    for p in range(n):
        out |= (o_bits[p].astype(np.uint64) << np.uint64(p))
    return out


if __name__ == "__main__":
    N = 8
    ok_all = True
    for a, b in [(1, 3), (1, 7), (3, 11)]:
        a8, b8 = a % N, b % N
        outs = [design_b_scalar(x, N, a8, b8) for x in range(1 << N)]
        distinct = len(set(outs)) == (1 << N)
        # scalar vs vectorized agreement on all inputs
        V = np.arange(1 << N, dtype=np.uint64)
        vec = design_b_vec(V, N, a8, b8)
        agree = all(int(vec[x]) == outs[x] for x in range(1 << N))
        # 64-bit vec model bijectivity sanity: sequential 2^18 outputs must be distinct
        V64 = np.arange(1 << 18, dtype=np.uint64)
        v64 = design_b_vec(V64, 64, a, b)
        seq_distinct = len(set(int(v) for v in v64)) == (1 << 18)
        print(f"offsets=({a},{b}) mod8=({a8},{b8}): n=8 bijective={distinct} "
              f"scalar==vec={agree} n64-seq-distinct={seq_distinct}")
        ok_all &= distinct and agree and seq_distinct
    print("BIJECTIVITY:", "PASS" if ok_all else "FAIL")
