"""Avalanche / SAC / BIC / uniformity for SPN rounds vs splitmix & murmur."""
import sys, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix")
from spn import mix_spn_np, U64
from tests_part1 import splitmix_np, murmur_np

BIT = np.arange(64, dtype=np.uint64)


def avalanche(fn, trials=4096, seed=1):
    rng = np.random.default_rng(seed)
    V = rng.integers(0, 2**64, size=trials, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=trials, dtype=np.uint64)
    base = fn(V, K)
    out = {}
    for name, which in (("val", 0), ("key", 1)):
        P = np.empty((64, 64))
        for i in range(64):
            F = fn(V ^ (U64(1) << U64(i)), K) if which == 0 else fn(V, K ^ (U64(1) << U64(i)))
            D = base ^ F
            P[i] = (((D[:, None] >> BIT) & U64(1)).mean(axis=0))
        dev = np.abs(P - 0.5)
        out[name] = (float(P.mean()), float(dev.mean()), float(dev.max()))
    return out


def bic(fn, seed=7, trials=8192):
    """Max |correlation| between distinct output-bit flip indicators when
    flipping input bit 0 of val. Robust: skip near-constant columns."""
    rng = np.random.default_rng(seed)
    V = rng.integers(0, 2**64, size=trials, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=trials, dtype=np.uint64)
    B = (((fn(V, K) ^ fn(V ^ U64(1), K))[:, None] >> BIT) & U64(1)).astype(float)
    p = B.mean(axis=0)
    live = (p > 0.02) & (p < 0.98)
    C = np.corrcoef(B[:, live], rowvar=False)
    iu = np.triu_indices(live.sum(), 1)
    worst = np.unravel_index(np.argmax(np.abs(C[iu])), (live.sum(), live.sum()))
    cols = np.where(live)[0]
    return float(np.abs(C[iu]).max()), int(cols[worst[0]]), int(cols[worst[1]]), float(p.min()), float(p.max())


def uniformity_chi2(fn, n=1 << 20, seed=99, bits=12):
    """Chi-square of low `bits` of output over sequential inputs (key fixed)."""
    rng = np.random.default_rng(seed)
    K = np.full(n, rng.integers(0, 2**64, dtype=np.uint64), dtype=np.uint64)
    V = np.arange(n, dtype=np.uint64)
    S = fn(V, K)
    B = 1 << bits
    cnt = np.bincount((S & U64(B - 1)).astype(np.int64), minlength=B).astype(float)
    e = n / B
    chi2 = ((cnt - e) ** 2 / e).sum()
    df = B - 1
    z = (chi2 - df) / np.sqrt(2 * df)
    return chi2, df, z


if __name__ == "__main__":
    cands = [("splitmix64", splitmix_np), ("murmur3-fmix", murmur_np)]
    for r in (4, 6, 8, 10):
        cands.append((f"SPN-{r}", lambda V, K, r=r: mix_spn_np(V, K, rounds=r)))
    for name, fn in cands:
        t0 = time.time()
        av = avalanche(fn)
        mc, c1, c2, pmin, pmax = bic(fn)
        chi2, df, z = uniformity_chi2(fn)
        dt = time.time() - t0
        print(f"--- {name} ({dt:.1f}s) ---")
        for src in ("val", "key"):
            m, md, xd = av[src]
            print(f"  SAC flip {src}: mean={m:.5f} mean|d|={md:.5f} max|d|={xd:.5f}")
        print(f"  BIC max|corr|={mc:.4f} (bits {c1},{c2}; per-bit flip p in [{pmin:.3f},{pmax:.3f}])")
        print(f"  uniformity low12 chi2={chi2:.0f} df={df} z={z:+.2f}")
