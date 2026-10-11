"""Statistical verification battery for MIX64. All numbers printed are MEASURED."""
import math, random, sys, time
import numpy as np
from mix64 import mix64, mix16, mix_n, baseline_splitmix, baseline_murmur, M64, M32

U64 = np.uint64
MASK64 = U64(0xFFFFFFFFFFFFFFFF)
MASK32 = U64(0xFFFFFFFF)

C1 = U64(0x85EBCA6B)
C2 = U64(0xC2B2AE35)


def rotl32_np(v, r):
    v = v & MASK32
    r = r & U64(31)
    sh = np.where(r == 0, v,
                  (((v << r) | (v >> (U64(32) - r)))) & MASK32)
    return sh


def rotl64_np(v, r):
    r = r & U64(63)
    return np.where(r == 0, v,
                    (((v << r) | (v >> (U64(64) - r)))) & MASK64)


def mix64_np(val, key):
    val = np.asarray(val, dtype=np.uint64); key = np.asarray(key, dtype=np.uint64)
    x = val + key
    x ^= x >> U64(30)
    x ^= (x << U64(27))
    lo = x & MASK32
    hi = x >> U64(32)
    a = lo * C1
    b = hi * C2
    r1 = key & U64(31)
    r2 = (key >> U64(5)) & U64(31)
    a1 = (a + b) & MASK32
    b1 = (b ^ rotl32_np(a1, r1)) & MASK32
    b2 = (b1 + a1) & MASK32
    a2 = (a1 ^ rotl32_np(b2, r2)) & MASK32
    x = ((b2 << U64(32)) | a2)
    x ^= key
    x = rotl64_np(x, key & U64(63))
    x ^= x >> U64(31)
    x ^= (x << U64(17))
    return x


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


# sanity: numpy model == scalar model
_rng = random.Random(42)
for _ in range(2000):
    v = _rng.getrandbits(64); k = _rng.getrandbits(64)
    assert int(mix64_np(U64(v), U64(k))) == mix64(v, k), "model mismatch"
print("model check: numpy vector model == scalar model (2000 random vectors) OK")


# ---------------------------------------------------------------- avalanche
def avalanche(fn_np, trials=4096, seed=1):
    rng = np.random.default_rng(seed)
    V = rng.integers(0, 2**64, size=trials, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=trials, dtype=np.uint64)
    base = fn_np(V, K)
    bit = np.arange(64, dtype=np.uint64)
    res = {}
    for name, flip in (("val", 0), ("key", 1)):
        P = np.empty((64, 64))
        for i in range(64):
            if flip == 0:
                F = fn_np(V ^ (U64(1) << U64(i)), K)
            else:
                F = fn_np(V, K ^ (U64(1) << U64(i)))
            D = base ^ F
            P[i] = (((D[:, None] >> bit) & U64(1)).mean(axis=0))
        dev = np.abs(P - 0.5)
        res[name] = dict(mean=float(P.mean()), maxdev=float(dev.max()),
                         meandev=float(dev.mean()), P=P)
    return res


def bic_maxcorr(P_trials_bits, seed_in=0):
    # max |correlation| between distinct output-bit flip indicators,
    # for input bit seed_in, over trials
    return None  # computed inline below


def avalanche_report(name, fn_np):
    t0 = time.time()
    r = avalanche(fn_np, trials=4096)
    # BIC: for input bit 0 of val, correlation matrix of the 64 output flip bits
    rng = np.random.default_rng(7)
    T = 4096
    V = rng.integers(0, 2**64, size=T, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=T, dtype=np.uint64)
    base = fn_np(V, K)
    F = fn_np(V ^ U64(1), K)
    D = base ^ F
    B = ((D[:, None] >> np.arange(64, dtype=np.uint64)) & U64(1)).astype(float)
    C = np.corrcoef(B, rowvar=False)
    iu = np.triu_indices(64, 1)
    maxcorr = float(np.abs(C[iu]).max())
    print(f"--- avalanche {name} ({time.time()-t0:.1f}s) ---")
    for src in ("val", "key"):
        d = r[src]
        print(f"  flip {src:3s} bit: mean p={d['mean']:.5f}  "
              f"mean|p-.5|={d['meandev']:.5f}  max|p-.5|={d['maxdev']:.5f}")
    print(f"  BIC: max |corr| between output-bit flips = {maxcorr:.4f} (ideal 0)")
    return r, maxcorr


def _run_battery():
    print("=" * 70)
    av_mix, bic_mix = avalanche_report("MIX64", mix64_np)
    av_sm, bic_sm = avalanche_report("splitmix64-final", splitmix_np)
    av_mm, bic_mm = avalanche_report("murmur3-fmix64", murmur_np)


if __name__ == "__main__":
    _run_battery()
