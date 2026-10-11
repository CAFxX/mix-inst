"""Track 6, batch 11: WIDE AND-cascade (fewer stages, more per stage).

Hypothesis: wider per-stage (5 rotations: 2 ANDs + linear) compensates for
fewer stages. 4 stages x ~4u = ~16u target.

Structure:
  x = v ^ k
  4 stages: x ^= (ra&rb) ^ (rc&rd) ^ re
  x ^= rotl(k,13)

Candidates:
  t6_wide4a: schedule A
  t6_wide4b: schedule B (alternate)
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


SCHED_WA = [(11, 29, 47, 5, 23), (23, 41, 7, 19, 37),
            (7, 37, 19, 53, 13), (17, 43, 31, 11, 29)]
SCHED_WB = [(5, 17, 35, 53, 11), (29, 47, 13, 31, 7),
            (19, 37, 55, 23, 41), (11, 33, 51, 17, 43)]


def _wide4_cascade(v, k, sched):
    x = (np.uint64(v) ^ np.uint64(k)) & M64
    for (a, b, c, d, e) in sched:
        ra, rb, rc, rd, re = [_rotl64(x, t) for t in (a, b, c, d, e)]
        x = (x ^ (ra & rb) ^ (rc & rd) ^ re) & M64
    x = (x ^ _rotl64(np.uint64(k), 13)) & M64
    return x


def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f


def _mk_wide(sched, fname):
    def f(v, k):
        return _wide4_cascade(v, k, sched)
    f.__name__ = fname
    return f


CANDIDATES_B11 = {
    "t6_wide4a": (_mk_wide(SCHED_WA, "wide_wide4a"),
                  "4-stage WIDE AND-cascade x^=(ra&rb)^(rc&rd)^re"),
    "t6_wide4b": (_mk_wide(SCHED_WB, "wide_wide4b"),
                  "4-stage WIDE AND-cascade, alternate schedule"),
}

MIX_NP_B11 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B11.items()}

if __name__ == "__main__":
    for name, (fn, desc) in CANDIDATES_B11.items():
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
