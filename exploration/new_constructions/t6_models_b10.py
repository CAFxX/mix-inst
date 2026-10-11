"""Track 6, batch 10: 5-stage AND-cascade (x ^= (ra&rb)^rc).

Rationale: al_and6a (Track 3) is 6-stage at 20.1u (3.35u/stage) and passes ALL
gates. 5 stages target ~16.8u. The 5-stage AND-cascade is UNTESTED — if quality
holds, it's a new frontier. Track 3's supervisor is stale 5h+; parent directed
Track 6 to push toward 20u.

Structure (matches al_and6a exactly, minus one stage):
  x = v ^ k
  5 stages: x ^= (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)
  x ^= rotl(k,13)

Candidates:
  t6_and5a: stages [(1,2,13), (7,19,5), (3,11,29), (17,31,7), (11,23,37)]
            (first 5 of al_and6a's schedule)
  t6_and5b: stages [(5,13,29), (11,23,41), (7,17,37), (19,31,11), (3,29,43)]
            (new schedule)
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


STAGES_A = [(1, 2, 13), (7, 19, 5), (3, 11, 29), (17, 31, 7), (11, 23, 37)]
STAGES_B = [(5, 13, 29), (11, 23, 41), (7, 17, 37), (19, 31, 11), (3, 29, 43)]


def _and5_cascade(v, k, stages):
    x = (np.uint64(v) ^ np.uint64(k)) & M64
    for (a, b, c) in stages:
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rotl64(x, c)) & M64
    x = (x ^ _rotl64(np.uint64(k), 13)) & M64
    return x


def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f


def _mk_and5(stages, fname):
    def f(v, k):
        return _and5_cascade(v, k, stages)
    f.__name__ = fname
    return f


CANDIDATES_B10 = {
    "t6_and5a": (_mk_and5(STAGES_A, "and_and5a"),
                 "5-stage AND-cascade x^=(ra&rb)^rc (al_and6a schedule, 5 stages)"),
    "t6_and5b": (_mk_and5(STAGES_B, "and_and5b"),
                 "5-stage AND-cascade x^=(ra&rb)^rc (new schedule)"),
}

MIX_NP_B10 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B10.items()}

if __name__ == "__main__":
    for name, (fn, desc) in CANDIDATES_B10.items():
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
