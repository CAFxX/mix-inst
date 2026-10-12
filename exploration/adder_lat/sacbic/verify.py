"""
Verify SAC/BIC via direct simulation (independent of mask method).
Also tests bijectivity.

F(x)_j = x_j XOR (XOR_k (x_{a_{j,k}} & x_{b_{j,k}}))
"""

import random
import pickle
import sys


def eval_F(funcs, x):
    """x: int (64-bit). Returns 64-bit int output."""
    out = 0
    for j, pairs in enumerate(funcs):
        v = (x >> j) & 1
        for (a, b) in pairs:
            v ^= ((x >> a) & 1) & ((x >> b) & 1)
        out |= (v << j)
    return out


def test_bijectivity(funcs, n=1000000, seed=1):
    rng = random.Random(seed)
    seen = set()
    for _ in range(n):
        x = rng.getrandbits(64)
        y = eval_F(funcs, x)
        if y in seen:
            return False, "collision found"
        seen.add(y)
    # Also check random pairs for collisions (birthday)
    return True, f"0 collisions in {n} random outputs (not a proof)"


def test_sac(funcs, n_samples=200000, seed=2):
    """For each (i,j), estimate P(D_i f_j = 1). SAC holds if ~0.5.
    Returns max deviation from 0.5."""
    rng = random.Random(seed)
    # We'll do it efficiently: for each i, generate samples, compute all j at once
    max_dev = 0.0
    worst = None
    for i in range(64):
        # counts[j] = number of times D_i f_j = 1
        counts = [0] * 64
        for _ in range(n_samples):
            x = rng.getrandbits(64)
            y1 = eval_F(funcs, x)
            y2 = eval_F(funcs, x ^ (1 << i))
            d = y1 ^ y2
            for j in range(64):
                counts[j] += (d >> j) & 1
        for j in range(64):
            p = counts[j] / n_samples
            dev = abs(p - 0.5)
            if dev > max_dev:
                max_dev = dev
                worst = (i, j, p)
    return max_dev, worst


def test_bic(funcs, n_samples=200000, seed=3):
    """For each i, j<k: correlation of D_i f_j and D_i f_k.
    Returns max |correlation|."""
    rng = random.Random(seed)
    max_corr = 0.0
    worst = None
    for i in range(64):
        # For efficiency, accumulate joint counts for all (j,k) pairs
        # This is 64*63/2 = 2016 pairs per i, 64 i's = 129k pairs. Each needs 4 counters.
        # Instead, do it in a smarter way: for each i, collect the 64-bit derivative vectors,
        # then compute correlations.
        # Simpler: for each i, gather N samples of the 64-bit D vector, then compute pairwise corr.
        N = n_samples
        # Store as list of ints
        ds = []
        for _ in range(N):
            x = rng.getrandbits(64)
            y1 = eval_F(funcs, x)
            y2 = eval_F(funcs, x ^ (1 << i))
            ds.append(y1 ^ y2)
        # Now compute correlation for each (j,k)
        # corr = |P(both 1) - P(j1)P(k1)| / sqrt(...) but for binary, use |4*P11 - ...|
        # Simpler: correlation coefficient
        for j in range(64):
            for k in range(j + 1, 64):
                n11 = n10 = n01 = n00 = 0
                for d in ds:
                    bj = (d >> j) & 1
                    bk = (d >> k) & 1
                    if bj and bk:
                        n11 += 1
                    elif bj:
                        n10 += 1
                    elif bk:
                        n01 += 1
                    else:
                        n00 += 1
                # Pearson correlation for binary
                # mean_j = (n11+n10)/N, mean_k = (n11+n01)/N
                # cov = n11/N - mean_j*mean_k
                # var_j = mean_j*(1-mean_j), var_k similarly
                mj = (n11 + n10) / N
                mk = (n11 + n01) / N
                if mj == 0 or mj == 1 or mk == 0 or mk == 1:
                    corr = 1.0 if (mj == mk) else 0.0  # degenerate
                else:
                    cov = n11 / N - mj * mk
                    corr = abs(cov / ((mj * (1 - mj) * mk * (1 - mk)) ** 0.5))
                if corr > max_corr:
                    max_corr = corr
                    worst = (i, j, k, corr)
        print(f"  i={i}: max_corr so far={max_corr:.4f}", flush=True)
    return max_corr, worst


if __name__ == "__main__":
    pkl = sys.argv[1]
    with open(pkl, "rb") as f:
        funcs = pickle.load(f)
    print(f"Loaded {len(funcs)} functions from {pkl}")

    print("Bijectivity...")
    ok, msg = test_bijectivity(funcs, n=200000)
    print(f"  {ok}: {msg}")

    print("SAC (sampling)...")
    # Use fewer samples for speed in this check
    max_dev, worst = test_sac(funcs, n_samples=20000)
    print(f"  max |P-0.5| = {max_dev:.4f}, worst={worst}")
