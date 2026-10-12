"""
Fast numpy-based SAC/BIC/bijectivity verification.
"""

import pickle
import numpy as np
import sys


def load_funcs(pkl):
    with open(pkl, "rb") as f:
        return pickle.load(f)


def eval_F_batch(funcs, xs):
    """xs: (N,) uint64 array. Returns (N,) uint64 outputs."""
    N = len(xs)
    # Extract bits: bits[n, i] = bit i of xs[n]
    # Use vectorized operations
    out = np.zeros(N, dtype=np.uint64)
    # For each j, compute f_j for all n
    # f_j = x_j ^ XOR_k (x_a & x_b)
    # We'll do it bit by bit using numpy
    for j in range(64):
        # x_j for all n
        v = (xs >> np.uint64(j)) & np.uint64(1)
        for (a, b) in funcs[j]:
            va = (xs >> np.uint64(a)) & np.uint64(1)
            vb = (xs >> np.uint64(b)) & np.uint64(1)
            v ^= va & vb
        out |= v.astype(np.uint64) << np.uint64(j)
    return out


def test_bijectivity_fast(funcs, n=1000000, seed=1):
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    ys = eval_F_batch(funcs, xs)
    # Check for duplicates in ys
    uniq = np.unique(ys)
    if len(uniq) < n:
        return False, f"collision: {n - len(uniq)} duplicates"
    return True, f"0 collisions in {n} outputs"


def test_sac_fast(funcs, n_per_i=50000, seed=2):
    """Vectorized SAC test. Returns max |P-0.5|."""
    rng = np.random.default_rng(seed)
    max_dev = 0.0
    worst = None
    for i in range(64):
        xs = rng.integers(0, 2**64, size=n_per_i, dtype=np.uint64)
        y1 = eval_F_batch(funcs, xs)
        y2 = eval_F_batch(funcs, xs ^ (np.uint64(1) << np.uint64(i)))
        d = y1 ^ y2
        # For each j, P = mean of bit j
        for j in range(64):
            p = np.mean((d >> np.uint64(j)) & np.uint64(1))
            dev = abs(p - 0.5)
            if dev > max_dev:
                max_dev = dev
                worst = (i, j, p)
        if i % 16 == 0:
            print(f"  SAC i={i}: max_dev={max_dev:.4f}", flush=True)
    return max_dev, worst


if __name__ == "__main__":
    pkl = sys.argv[1]
    funcs = load_funcs(pkl)
    print(f"Loaded {len(funcs)} funcs")

    print("Bijectivity (fast)...")
    ok, msg = test_bijectivity_fast(funcs, n=200000)
    print(f"  {ok}: {msg}")

    print("SAC (fast, vectorized)...")
    max_dev, worst = test_sac_fast(funcs, n_per_i=20000)
    print(f"  max |P-0.5| = {max_dev:.4f}, worst={worst}")
