#!/usr/bin/env python3
"""Concentrated-nonlinearity XIG design: f_i(x) = x_i XOR g_i(x).

g_i: 8-input, degree-5, NL=112 (from degree-5 search).
Wiring: concentrated — group 0 sees all of block 0 (Fisher's 6 varying bits);
other groups take 4 from own block + 4 from block 0.
g_i excludes x_i (bijectivity safety for XIG form).
"""
import numpy as np
import random, sys

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Degree-5 NL=112 base ANF. For diversity, each g_i uses a random subset.
BASE_TERMS = [
    (7,), (6,), (2,),
    (1,2,3,5,6),
    (3,4), (0,5), (1,7), (1,6),
    (1,4,7), (1,5,6), (1,2,4), (0,2,4),
    (0,1,4,5), (4,5,6,7),
]

def get_terms(i):
    """Deterministic per-i subset of BASE_TERMS (10-14 terms) for diversity."""
    rng = random.Random(1000 + i)
    # Always keep the degree-5 term and linears for degree/balance
    keep = [(7,), (6,), (2,), (1,2,3,5,6)]
    rest = [t for t in BASE_TERMS if t not in keep]
    rng.shuffle(rest)
    # Keep 6-10 of the remaining 10
    keep.extend(rest[:rng.randint(6, 10)])
    return keep

TERMS = BASE_TERMS  # default; eval_g uses get_terms(i)

def build_wiring():
    """wiring[i] = list of 8 input indices for g_i, excluding i.
    Balance: each g_i sees 3-4 of bits 0-5 (for LIN) + 4-5 of bits 6-17 (for DIFF).
    All 18 bits (0-17) get uniform coverage across the 64 g_i's."""
    wiring = []
    for i in range(64):
        # 3-4 from low 6 (bits 0-5), excluding i
        low = [b for b in range(6) if b != i]
        random.shuffle(low)
        n_low = 4 if len(low) >= 4 else len(low)
        cand = low[:n_low]
        # 4-5 from bits 6-17, excluding i
        high = [b for b in range(6, 18) if b != i and b not in cand]
        random.shuffle(high)
        cand.extend(high[:8-len(cand)])
        # Fill remaining from anywhere (excluding i)
        if len(cand) < 8:
            rest = [b for b in range(64) if b != i and b not in cand]
            random.shuffle(rest)
            cand.extend(rest[:8-len(cand)])
        random.shuffle(cand)
        assert len(cand) == 8 and i not in cand, (i, cand)
        wiring.append(cand)
    return wiring

WIRING = build_wiring()

def eval_g(w, x, gi):
    """w: (8,) input indices. x: (N,64) bits. gi: g index for term diversity.
    Returns (N,) g output."""
    inp = x[:, w]
    terms = get_terms(gi)
    out = np.zeros(x.shape[0], dtype=np.uint8)
    for t in terms:
        prod = np.ones(x.shape[0], dtype=np.uint8)
        for li in t:
            prod &= inp[:, li]
        out ^= prod
    return out

def eval_f(x):
    """x: (N,64) -> (N,64) f output."""
    N = x.shape[0]
    y = x.copy()
    for i in range(64):
        g = eval_g(WIRING[i], x, i)
        y[:, i] ^= g
    return y

def test_bijectivity(n_pairs=10_000_000, batch=1_000_000):
    """0 collisions in n_pairs random pairs."""
    seen = set()
    # Use Python ints as 64-bit hashes
    for b in range(0, n_pairs, batch):
        n = min(batch, n_pairs - b)
        x = np.random.randint(0, 2, size=(n, 64), dtype=np.uint8)
        y = eval_f(x)
        # Pack to 64-bit ints
        y_int = np.zeros(n, dtype=np.uint64)
        for i in range(64):
            y_int |= y[:, i].astype(np.uint64) << np.uint64(i)
        for v in y_int:
            v = int(v)
            if v in seen:
                return False, v
            seen.add(v)
        print(f"  biject: batch {b//batch+1}, {len(seen)} unique", flush=True)
    return True, None

def gen_fisher_inputs(N=1<<18):
    """Sequential inputs for Fisher (varying low bits)."""
    # Two keys: use key=0 and key=all-ones as the fixed high bits
    x0 = np.zeros((N, 64), dtype=np.uint8)
    x1 = np.zeros((N, 64), dtype=np.uint8)
    for i in range(N):
        for b in range(18):
            bit = (i >> b) & 1
            x0[i, b] = bit
            x1[i, b] = bit
    # Key 1: high bits all 1
    x1[:, 18:] = 1
    return x0, x1

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "biject"
    if mode == "biject":
        ok, coll = test_bijectivity()
        print("BIJECTIVITY:", "PASS" if ok else f"FAIL collision={coll}")
    elif mode == "fisher_gen":
        # Generate outputs and save for lin_diff
        import os
        os.makedirs("fisher_data", exist_ok=True)
        x0, x1 = gen_fisher_inputs()
        print("Evaluating f on 2^18 inputs x2 keys...", flush=True)
        y0 = eval_f(x0)
        y1 = eval_f(x1)
        # Save as bits for lin_diff (it expects a function or outputs?)
        # We'll save and use lin_diff.screen_lin_diff via import
        np.save("fisher_data/y0.npy", y0)
        np.save("fisher_data/y1.npy", y1)
        print("Saved.")
    elif mode == "wiring_info":
        # Report: how many g_i see bits 0-5?
        cnt = sum(1 for i in range(64)
                  if any(b in WIRING[i] for b in range(6)))
        print(f"g_i seeing >=1 of bits 0-5: {cnt}/64")
        cnt_all = sum(1 for i in range(64)
                      if all(b in WIRING[i] for b in range(6)))
        print(f"g_i seeing all of bits 0-5: {cnt_all}/64")
        for i in range(8):
            print(f"  g_{i}: {sorted(WIRING[i])}")
