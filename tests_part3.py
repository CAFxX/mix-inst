"""Sequence battery for SPN-10: raw / Lemire / mask / mod-y uniformity.
All numbers MEASURED. Pass flag: |z| < 4 (chi2 z-score vs df)."""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spn import mix_spn_np, U64, MASK64
MASK32 = U64(0xFFFFFFFF)

R = 10


def mix(V, K):
    return mix_spn_np(V, K, rounds=R)


def chi2_z(counts):
    counts = np.asarray(counts, dtype=float)
    B = len(counts)
    e = counts.sum() / B
    chi2 = ((counts - e) ** 2 / e).sum()
    df = B - 1
    return (chi2 - df) / np.sqrt(2 * df), chi2, df


def monobit_z(bits01):
    n = len(bits01)
    ones = np.asarray(bits01).sum()
    return (ones - n / 2) / np.sqrt(n / 4)


def lemire_high64(x, X):
    """(x * X) >> 64 for uint64 arrays x and scalar X, via 32-bit limbs."""
    X1 = U64((X >> 32) & 0xFFFFFFFF)
    X0 = U64(X & 0xFFFFFFFF)
    x1 = x >> U64(32)
    x0 = x & MASK32
    p0 = x0 * X0
    p1 = x1 * X0
    p2 = x0 * X1
    p3 = x1 * X1
    s = p1 + p2
    c = (s < p1).astype(np.uint64)
    t = ((s & MASK32) << U64(32)) + p0
    carry2 = (t < ((s & MASK32) << U64(32))).astype(np.uint64)
    return p3 + (s >> U64(32)) + (c << U64(32)) + carry2


# verify lemire formula vs big-int Python on random data
_rng = np.random.default_rng(0)
_xv = _rng.integers(0, 2**64, size=4096, dtype=np.uint64)
for _X in (2, 3, 10, 1000, 2**32, 2**64 - 1, 0x9E3779B97F4A7C15):
    got = lemire_high64(_xv, _X)
    exp = np.array([((int(v) * _X) >> 64) for v in _xv], dtype=np.uint64)
    assert np.array_equal(got, exp), f"lemire formula wrong for X={_X}"
print("lemire (x*X)>>64 vector formula verified vs big-int: OK")

CONFIGS = [
    ("key=0,I=0,j=1", 0x0, 0x0, 0x1, 1 << 18),
    ("key=0,I=mid,j=2", 0x0, 0x123456789ABCDEF0, 0x2, 1 << 18),
    ("key=gold,I=0,j=1", 0x9E3779B97F4A7C15, 0x0, 0x1, 1 << 18),
    ("key=dead,I=mid,j=gold", 0xDEADBEEFCAFEBABE, 0x123456789ABCDEF0, 0x9E3779B97F4A7C15, 1 << 18),
    ("key=all1,I=aa,j=3", 0xFFFFFFFFFFFFFFFF, 0xAAAAAAAAAAAAAAAA, 0x3, 1 << 18),
    ("key=0123,I=fedc,j=2^32", 0x0123456789ABCDEF, 0xFEDCBA9876543210, 0x100000000, 1 << 18),
    ("key=aa,I=55,j=-2", 0xAAAAAAAAAAAAAAAA, 0x5555555555555555, 0xFFFFFFFFFFFFFFFE, 1 << 18),
    ("key=rnd,I=rnd,j=rnd-odd,N=2^20", 0x243F6A8885A308D3, 0x452821E638D01377, 0xB5297A4D68EFEED, 1 << 20),
]

MASKS = [1, 2, 4, 8, 12]
MODS = [3, 7, 10, 100, 1000]
LEMIRE_X = [2, 3, 10, 1000, 2**32, 2**64 - 1]

fails = []
ntests = 0


def check(tag, z):
    global ntests
    ntests += 1
    flag = "" if abs(z) < 4 else "  <-- FLAG"
    if abs(z) >= 4:
        fails.append((tag, z))
    print(f"  {tag:34s} z={z:+7.2f}{flag}")


t0 = time.time()
if __name__ == "__main__":
    for cname, key, I, j, N in CONFIGS:
        print(f"== {cname} (N={N}) ==")
        K = np.full(N, U64(key), dtype=np.uint64)
        V = (U64(I) + U64(j) * np.arange(N, dtype=np.uint64))
        S = mix(V, K)
    
        # raw: monobit over all 64 bit-planes (worst), chi2 low14, serial nibble pairs
        zb = max(abs(monobit_z(((S >> U64(b)) & U64(1))) ) for b in range(64))
        check("raw monobit worst-of-64", zb)
        z, _, _ = chi2_z(np.bincount((S & U64(0x3FFF)).astype(np.int64), minlength=16384))
        check("raw chi2 low14", z)
        lo = (S & U64(0xF)).astype(np.int64)
        pairs = lo[:-1] * 16 + lo[1:]
        z, _, _ = chi2_z(np.bincount(pairs, minlength=256))
        check("raw serial nibble-pairs", z)
    
        # Lemire reduction
        for X in LEMIRE_X:
            Y = lemire_high64(S, X)
            if X <= 2048:
                z, _, _ = chi2_z(np.bincount(Y.astype(np.int64), minlength=X))
            else:
                z, _, _ = chi2_z(np.bincount(((Y >> U64(53)).astype(np.int64)), minlength=2048))
            check(f"lemire X={X}", z)
    
        # mask 2^m - 1
        for m in MASKS:
            z, _, _ = chi2_z(np.bincount((S & U64((1 << m) - 1)).astype(np.int64), minlength=1 << m))
            check(f"mask 2^{m}-1", z)
    
        # mod y
        for y in MODS:
            z, _, _ = chi2_z(np.bincount((S % U64(y)).astype(np.int64), minlength=y))
            check(f"mod {y}", z)
    
    print(f"\n{ntests} checks, {len(fails)} flags, {time.time()-t0:.1f}s")
    for tag, z in fails:
        print(f"  FLAG: {tag} z={z:+.2f}")
