"""Track 6, batch 9: hetero `x ^=` with SIMPLE ops (new axis).

Batch 8 (fused) proved: fusing x into the nonlinear (removing outer `x ^=`)
destroys diffusion (both 19.2u candidates S1-FLAGGED with worst|z|>47000).
The outer `x ^=` linear path is load-bearing.

Batch 9 keeps the PROVEN `x ^= F(rots) ^ rk` structure (like al_and6a and het6)
but uses HETEROGENEOUS SIMPLE ops (2-3 rotations, 3-4 gates/stage) instead of
het6's complex ops (4-6 rotations, ~5 gates/stage).

Target: 3.5u/stage. 5 stages = 17.5u, 6 stages = 21u.

Candidates (all x ^= F(rots) ^ rk, rk = rotl(k,13*(i+1)) ^ RC[i]):
  t6_hx5a: 5-stage hetero simple: [ANDXOR, ORXOR, MAJ, ANDXOR, ORXOR]
  t6_hx6a: 6-stage hetero simple: [ANDXOR, ORXOR, MAJ, ANDXOR, ORXOR, MAJ]
  t6_hx5b: 5-stage hetero simple, alternate schedule
  t6_hx6b: 6-stage hetero simple, alternate schedule

Ops (3 rotations each):
  ANDXOR: (ra & rb) ^ rc
  ORXOR:  (ra | rb) ^ rc
  MAJ:    (ra&rb)|(ra&rc)|(rb&rc)
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _andxor(ra, rb, rc):
    return ((ra & rb) ^ rc) & M64


def _orxor(ra, rb, rc):
    return ((ra | rb) ^ rc) & M64


def _maj3(ra, rb, rc):
    return ((ra & rb) | (ra & rc) | (rb & rc)) & M64


OP_FN = {"ANDXOR": _andxor, "ORXOR": _orxor, "MAJ": _maj3}

# 6 stages x 3 rotations (well-spread)
SCHED_HX = [
    (11, 29, 47),
    (23, 41, 7),
    (7, 37, 19),
    (19, 53, 5),
    (5, 31, 13),
    (13, 47, 23),
]
SCHED_HXB = [
    (17, 43, 3),
    (29, 55, 11),
    (5, 39, 23),
    (31, 13, 47),
    (41, 7, 33),
    (19, 51, 9),
]

SEQ_HX5 = ["ANDXOR", "ORXOR", "MAJ", "ANDXOR", "ORXOR"]
SEQ_HX6 = ["ANDXOR", "ORXOR", "MAJ", "ANDXOR", "ORXOR", "MAJ"]


def _hetero_xor_cascade(v, k, seq, sched):
    x = np.uint64(v) ^ np.uint64(k)
    n = len(seq)
    for i in range(n):
        op = seq[i]
        ra, rb, rc = [_rotl64(x, t) for t in sched[i]]
        nl = OP_FN[op](ra, rb, rc)
        rk = _rotl64(np.uint64(k), 13 * (i + 1)) ^ RC64[i % 8]
        x = (x ^ nl ^ rk) & M64
    x = (x ^ (_rotl64(np.uint64(k), 13) >> np.uint64(32))) & M64
    return x


def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f


def _mk_hx(seq, sched, fname):
    def f(v, k):
        return _hetero_xor_cascade(v, k, seq, sched)
    f.__name__ = fname
    return f


CANDIDATES_B9 = {
    "t6_hx5a": (_mk_hx(SEQ_HX5, SCHED_HX, "hetero_hx5a"),
                "hetero x^= 5-stage simple: ANDXOR/ORXOR/MAJ/ANDXOR/ORXOR"),
    "t6_hx6a": (_mk_hx(SEQ_HX6, SCHED_HX, "hetero_hx6a"),
                "hetero x^= 6-stage simple: +MAJ"),
    "t6_hx5b": (_mk_hx(SEQ_HX5, SCHED_HXB, "hetero_hx5b"),
                "hetero x^= 5-stage simple, alternate schedule"),
    "t6_hx6b": (_mk_hx(SEQ_HX6, SCHED_HXB, "hetero_hx6b"),
                "hetero x^= 6-stage simple, alternate schedule"),
}

MIX_NP_B9 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B9.items()}

if __name__ == "__main__":
    for name, (fn, desc) in CANDIDATES_B9.items():
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
