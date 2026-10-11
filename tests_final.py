"""Comprehensive statistical validation: SPN-8 vs SPN-10 vs splitmix64 vs murmur3-fmix64.
Covers: SAC (val+key), BIC, sequential-input uniformity at multiple widths,
and the sequence battery (raw / Lemire / mask / mod-y) on adversarial configs.
All numbers MEASURED. Run: python3 tests_final.py  (takes ~1-2 min)
"""
import sys, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix")
from spn import mix_spn_np, U64

BIT = np.arange(64, dtype=np.uint64)


def splitmix_np(val, key):
    z = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    z = z + U64(0x9E3779B97F4A7C15)
    z ^= z >> U64(30); z = z * U64(0xBF58476D1CE4E5B9)
    z ^= z >> U64(27); z = z * U64(0x94D049BB133111EB)
    z ^= z >> U64(31)
    return z


def murmur_np(val, key):
    h = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    h ^= h >> U64(33); h = h * U64(0xFF51AFD7ED558CCD)
    h ^= h >> U64(33); h = h * U64(0xC4CEB9FE1A85EC53)
    h ^= h >> U64(33)
    return h


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
    rng = np.random.default_rng(seed)
    V = rng.integers(0, 2**64, size=trials, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=trials, dtype=np.uint64)
    B = (((fn(V, K) ^ fn(V ^ U64(1), K))[:, None] >> BIT) & U64(1)).astype(float)
    p = B.mean(axis=0)
    live = (p > 0.02) & (p < 0.98)
    C = np.corrcoef(B[:, live], rowvar=False)
    iu = np.triu_indices(live.sum(), 1)
    return float(np.abs(C[iu]).max())


def uniformity_chi2(fn, n=1 << 20, seed=99, bits=12):
    rng = np.random.default_rng(seed)
    K = np.full(n, rng.integers(0, 2**64, dtype=np.uint64), dtype=np.uint64)
    V = np.arange(n, dtype=np.uint64)
    S = fn(V, K)
    B = 1 << bits
    cnt = np.bincount((S & U64(B - 1)).astype(np.int64), minlength=B).astype(float)
    e = n / B
    chi2 = ((cnt - e) ** 2 / e).sum()
    df = B - 1
    return (chi2 - df) / np.sqrt(2 * df)


def lemire_np(S, X):
    X = np.asarray(X, dtype=np.uint64)
    hi = (S.astype(object) * X.astype(object)) >> 64
    return np.asarray(hi, dtype=np.uint64)


def chi2_z(counts, n):
    e = n / len(counts)
    chi2 = ((counts - e) ** 2 / e).sum()
    df = len(counts) - 1
    return (chi2 - df) / np.sqrt(2 * df)


def chi2_z_exact(counts, expected):
    """Pearson chi-square against exact (possibly non-uniform) expected counts."""
    c = np.asarray(counts, dtype=float)
    e = np.asarray(expected, dtype=float)
    chi2 = ((c - e) ** 2 / e).sum()
    df = len(c) - 1
    return (chi2 - df) / np.sqrt(2 * df)


W64 = 1 << 64


def lemire_preimg(lo, hi, X):
    """Exact # of s in [0,2^64) with ((s*X)>>64) in [lo,hi).
    (s*X)>>64 = r  <=>  r*2^64/X <= s < (r+1)*2^64/X, so the count is
    ceil(hi*2^64/X) - ceil(lo*2^64/X)."""
    return ((hi * W64 + X - 1) // X) - ((lo * W64 + X - 1) // X)


def mod_preimg(y):
    """Exact # of s in [0,2^64) with s mod y = r, for r = 0..y-1."""
    return [((W64 - 1 - r) // y) + 1 for r in range(y)]


def seq_battery(fn, key, I, j, N, label, V=None):
    """Sequence tests on I, I+j, ... (or precomputed V): raw monobit, low-bit chi2,
    serial pairs, Lemire reductions, masks, mod-y. Returns list of (test, z)."""
    K = np.full(N, U64(key), dtype=np.uint64)
    if V is None:
        V = (U64(I) + U64(j) * np.arange(N, dtype=np.uint64))
    S = fn(V, K)
    res = []
    # raw monobit
    ones = float(((S[:, None] >> BIT) & U64(1)).sum())
    nbits = N * 64
    res.append(("raw-monobit", (ones - nbits / 2) / np.sqrt(nbits / 4)))
    # per-bit monobit screen (catches single-bit biases the pooled test dilutes)
    bitcnt = ((S[:, None] >> BIT) & U64(1)).sum(axis=0).astype(float)
    res.append(("perbit-max|z|", float(np.abs((bitcnt - N / 2) / np.sqrt(N / 4)).max())))
    # low-bit chi2 for several widths
    for b in (4, 8, 12, 14):
        B = 1 << b
        cnt = np.bincount((S & U64(B - 1)).astype(np.int64), minlength=B).astype(float)
        res.append((f"low{b}-chi2", chi2_z(cnt, N)))
    # serial nibble pairs (16x16)
    p1 = (S & U64(15)).astype(np.int64)
    p2 = ((S >> U64(4)) & U64(15)).astype(np.int64)
    cnt = np.bincount(p1 * 16 + p2, minlength=256).astype(float)
    res.append(("nibble-pair", chi2_z(cnt, N)))
    # Lemire reductions: R = (S*X)>>64 takes values in [0,X) with EXACT null
    # distribution given by preimage counts (NOT uniform bins). For X <= 1024
    # use one bin per value; for large X use 1024 equal-width bins over [0,X)
    # with exact expected counts per bin.
    for X in (2, 3, 10, 1000, 1 << 32, (1 << 64) - 1):
        R = lemire_np(S, X)
        if X <= 1024:
            bounds = list(range(X + 1))
        else:
            B = 1024
            bounds = [(k * X) // B for k in range(B + 1)]
        nb = len(bounds) - 1
        E = np.array([lemire_preimg(bounds[k], bounds[k + 1], X) * N / W64
                      for k in range(nb)])
        if X <= 1024:
            cnt = np.bincount(R.astype(np.int64), minlength=X).astype(float)
        else:
            idx = np.digitize(R.astype(object), bounds[1:-1], right=False)
            cnt = np.bincount(np.asarray(idx, dtype=np.int64), minlength=nb).astype(float)
        assert len(cnt) == nb and (E > 0).all()
        res.append((f"lemire-X={X}", chi2_z_exact(cnt, E)))
    # masks
    for m in (1, 2, 4, 8, 12):
        B = 1 << m
        cnt = np.bincount((S & U64(B - 1)).astype(np.int64), minlength=B).astype(float)
        res.append((f"mask-m={m}", chi2_z(cnt, N)))
    # mod y: exact null expected counts (2^64 is not divisible by y)
    for y in (3, 7, 10, 100, 1000):
        R = (S % np.uint64(y)).astype(np.int64)
        E = np.array(mod_preimg(y), dtype=np.float64) * (N / W64)  # float64: no int64 overflow
        cnt = np.bincount(R, minlength=y).astype(float)
        res.append((f"mod-{y}", chi2_z_exact(cnt, E)))
    return res


CANDS = [
    ("splitmix64", splitmix_np),
    ("murmur3-fmix", murmur_np),
    ("SPN-8", lambda V, K: mix_spn_np(V, K, rounds=8)),
    ("SPN-10", lambda V, K: mix_spn_np(V, K, rounds=10)),
]

CONFIGS = [
    ("seq64", 0x123456789ABCDEF0, 0, 1, 1 << 18),
    ("seq64-oddkey", 0xDEADBEEFDEADBEEF, 0, 1, 1 << 18),
    ("stride-big", 0x0FEDCBA987654321, 12345, 0x9E3779B97F4A7C15, 1 << 18),
    ("stride-2", 0xAAAAAAAAAAAAAAAA, 0, 2, 1 << 18),
    ("high-only", 0x5555555555555555, 0xFFFFFFFF00000000, 0x100000000, 1 << 18),
    ("random", 0x0123456789ABCDEF, None, None, 1 << 18),  # random V
]


def main():
    t0 = time.time()
    print("=" * 78)
    print("PART A: avalanche / SAC  (trials=4096)")
    for name, fn in CANDS:
        r = avalanche(fn)
        for which in ("val", "key"):
            mean, mdev, xdev = r[which]
            print(f"  {name:14s} {which}: mean={mean:.5f} mean|dev|={mdev:.5f} max|dev|={xdev:.5f}")
    print(f"  ({time.time()-t0:.0f}s)")
    print("=" * 78)
    print("PART B: BIC max|corr| (trials=8192, flip val bit0)")
    t0 = time.time()
    for name, fn in CANDS:
        print(f"  {name:14s}: {bic(fn):.4f}")
    print(f"  ({time.time()-t0:.0f}s)")
    print("=" * 78)
    print("PART C: sequential-input uniformity chi2 z (n=2^20, fixed key)")
    t0 = time.time()
    for name, fn in CANDS:
        zs = [uniformity_chi2(fn, bits=b) for b in (4, 8, 12, 14)]
        print(f"  {name:14s}: " + " ".join(f"m{b}={z:+.2f}" for b, z in zip((4, 8, 12, 14), zs)))
    print(f"  ({time.time()-t0:.0f}s)")
    print("=" * 78)
    print("PART D: sequence battery (|z|>4 flagged)")
    t0 = time.time()
    nflag = 0
    for name, fn in CANDS:
        print(f"  --- {name} ---")
        for cname, key, I, j, N in CONFIGS:
            if I is None:  # random V: full battery on random inputs
                rng = np.random.default_rng(3)
                V = rng.integers(0, 2**64, size=N, dtype=np.uint64)
                res = seq_battery(fn, key, 0, 0, N, cname, V=V)
                flags = [(t, z) for t, z in res if abs(z) > 4]
                nflag += len(flags)
                worst = max(res, key=lambda tz: abs(tz[1]))
                print(f"    {cname:14s} {len(res)} tests, worst: {worst[0]} z={worst[1]:+.2f}" +
                      (f"  FLAGS: {flags}" if flags else ""))
                continue
            res = seq_battery(fn, key, I, j, N, cname)
            flags = [(t, z) for t, z in res if abs(z) > 4]
            nflag += len(flags)
            worst = max(res, key=lambda tz: abs(tz[1]))
            print(f"    {cname:14s} {len(res)} tests, worst: {worst[0]} z={worst[1]:+.2f}" +
                  (f"  FLAGS: {flags}" if flags else ""))
    print(f"  total flags: {nflag}  ({time.time()-t0:.0f}s)")
    print("=" * 78)
    print("DONE")


if __name__ == "__main__":
    main()
