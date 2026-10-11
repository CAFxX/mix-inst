"""Track 6, batch 12: Feistel with AND-cascade F (new skeleton).

All previous batches were CASCADES (sequential x ^= F). Batch 12 uses a
FEISTEL network — a genuinely different structure.

Design: 4-round Feistel on 32-bit halves.
  (L,R) = split64(x ^ k)
  For i in 0..3:
    F = 2-stage 32-bit AND-cascade on R: R ^= (ra&rb)^rc (32-bit rots)
    (L,R) = (R, L ^ F ^ rk_i)
  out = concat(R, L) ^ k  (final swap + key)

F is cheap (2 stages, 32-bit). 4 Feistel rounds give diffusion via swaps.
Target: 4 x ~5u = ~20u.

Candidates:
  t6_feist4a: 4-round, F=2-stage, schedule A
  t6_feist4b: 4-round, F=2-stage, schedule B
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint64(0xFFFFFFFF)
RC32 = [np.uint64(0x9E3779B9), np.uint64(0x3C6EF372),
        np.uint64(0xDAA66D2C), np.uint64(0x78DDE6E5)]


def _rotl32(x, r):
    r %= 32
    if r == 0:
        return x & M32
    return (((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & M32)


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _F_and2(R, rk, sched):
    # 2-stage 32-bit AND-cascade: R ^= (ra&rb)^rc
    x = np.uint64(R) & M32
    for (a, b, c) in sched:
        x = (x ^ (_rotl32(x, a) & _rotl32(x, b)) ^ _rotl32(x, c)) & M32
    return (x ^ np.uint64(rk)) & M32


SCHED_FA = [(5, 13, 29), (11, 23, 7)]
SCHED_FB = [(7, 19, 3), (13, 29, 11)]


def _feistel4(v, k, fsched):
    x = (np.uint64(v) ^ np.uint64(k)) & M64
    L = (x >> np.uint64(32)) & M32
    R = x & M32
    kh = (np.uint64(k) >> np.uint64(32)) & M32
    kl = np.uint64(k) & M32
    for i in range(4):
        rk = (_rotl32(kl, 7 * (i + 1)) ^ RC32[i % 4]) & M32
        F = _F_and2(R, rk, fsched)
        L, R = R, (L ^ F) & M32
    out = ((np.uint64(R) << np.uint64(32)) | np.uint64(L)) & M64
    return (out ^ np.uint64(k)) & M64


def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f


def _mk_feist(fsched, fname):
    def f(v, k):
        return _feistel4(v, k, fsched)
    f.__name__ = fname
    return f


CANDIDATES_B12 = {
    "t6_feist4a": (_mk_feist(SCHED_FA, "feist_feist4a"),
                   "4-round Feistel, F=2-stage 32-bit AND-cascade"),
    "t6_feist4b": (_mk_feist(SCHED_FB, "feist_feist4b"),
                   "4-round Feistel, F=2-stage, alt schedule"),
}

MIX_NP_B12 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B12.items()}

if __name__ == "__main__":
    for name, (fn, desc) in CANDIDATES_B12.items():
        a = fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))
        b = fn(np.uint64(1), np.uint64(0x123456789ABCDEF0))
        assert a != b, name
        v0 = np.uint64(0x123456789ABCDEF0)
        k0 = np.uint64(0xFEDCBA9876543210)
        o0 = fn(v0, k0)
        flips = []
        for i in range(64):
            v1 = v0 ^ (np.uint64(1) << np.uint64(i))
            o1 = fn(v1, k0)
            flips.append(bin(int(o0 ^ o1)).count('1'))
        avg = sum(flips) / len(flips)
        dev = (sum((f - 32) ** 2 for f in flips) / len(flips)) ** 0.5
        print(f"{name}: ok; avalanche avg={avg:.1f} dev={dev:.2f}")
