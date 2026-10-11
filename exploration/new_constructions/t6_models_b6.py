"""Track 6, batch 6: heterogeneous cascades (genuinely new axis).

Batch 5 used HOMOGENEOUS cascades (same op every stage): maj6, andor6, etc.
Batch 6 uses HETEROGENEOUS cascades (different op per stage). This is a
genuinely new structural axis, not a parameter tweak.

Rationale: different boolean functions have different algebraic properties.
- maj: symmetric, balanced, good diffusion
- andor: (a&b)|(c&d) — different nonlinearity profile
- chi: x ^= (y & ~z) — asymmetric, from Keccak
- xor3and: linear XOR + cubic AND term

Mixing them may achieve better overall properties than any single op,
or may allow fewer stages by combining complementary strengths.

Structure: 6 stages, each stage uses a different op in sequence.
Schedules reuse batch-5 rotation sets for comparability.

Candidates:
  t6_het6a: maj -> andor -> chi -> majxor -> xor3and -> maj
  t6_het6b: chi -> maj -> andor -> xor3and -> majxor -> chi
  t6_het6c: andor -> xor3and -> maj -> chi -> majxor -> andor
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


def _maj(a, b, c):
    return ((a & b) | (a & c) | (b & c)) & M64


def _chi(a, b, c):
    # Keccak chi: a ^= (b & ~c)
    return (a ^ (b & (~c & M64))) & M64


def _apply_op(op, r):
    """Apply op to rotated values r (list). Returns the nonlinear term."""
    if op == "maj":
        # r[0..3]: maj(r0,r1,r2) ^ r3
        maj = _maj(r[0], r[1], r[2])
        return (maj ^ r[3]) & M64
    elif op == "andor":
        # r[0..4]: ((r0&r1)|(r2&r3)) ^ r4
        return (((r[0] & r[1]) | (r[2] & r[3])) ^ r[4]) & M64
    elif op == "chi":
        # r[0..2]: chi(r0,r1,r2)
        return _chi(r[0], r[1], r[2])
    elif op == "majxor":
        # r[0..4]: maj(r0,r1,r2) ^ (r3&r4)
        maj = _maj(r[0], r[1], r[2])
        return (maj ^ (r[3] & r[4])) & M64
    elif op == "xor3and":
        # r[0..5]: r0^r1^r2 ^ (r3&r4&r5)
        return (r[0] ^ r[1] ^ r[2] ^ (r[3] & r[4] & r[5])) & M64
    else:
        raise ValueError(f"unknown op {op}")


# Rotation schedules: reuse batch-5 sets for comparability
# SCHED6: 6 stages x 4 rotations (for maj)
# SCHED6_5: 6 stages x 5 rotations (for andor/majxor)
# SCHED6_6: 6 stages x 6 rotations (for xor3and)
# For heterogeneous, we use the max (6) and slice per op
SCHED6_HET = [
    (11, 23, 37, 5, 17, 29),
    (7, 19, 31, 43, 13, 25),
    (3, 15, 27, 39, 51, 9),
    (21, 33, 45, 1, 35, 47),
    (5, 29, 53, 17, 41, 11),
    (13, 37, 61, 23, 47, 19),
]

# Op sequences for each candidate (6 stages)
SEQ_A = ["maj", "andor", "chi", "majxor", "xor3and", "maj"]
SEQ_B = ["chi", "maj", "andor", "xor3and", "majxor", "chi"]
SEQ_C = ["andor", "xor3and", "maj", "chi", "majxor", "andor"]

# Rotations needed per op
OP_NROTS = {"maj": 4, "andor": 5, "chi": 3, "majxor": 5, "xor3and": 6}


def _hetero_cascade(v, k, seq):
    x = np.uint64(v) ^ np.uint64(k)
    for i, op in enumerate(seq):
        nrots = OP_NROTS[op]
        rots = SCHED6_HET[i][:nrots]
        r = [_rotl64(x, t) for t in rots]
        nl = _apply_op(op, r)
        rk = _rotl64(np.uint64(k), 13 * (i + 1)) ^ RC64[i % 8]
        x = (x ^ nl ^ rk) & M64
    # post-whiten
    x = (x ^ (_rotl64(np.uint64(k), 13) >> np.uint64(32))) & M64
    return x


def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f


def _mk_hetero(seq, fname):
    # Named wrapper (never a bare lambda): avoids the '<lambda>' __name__
    # SyntaxError at S1 load time (2026-10-08 lesson).
    def f(v, k):
        return _hetero_cascade(v, k, seq)
    f.__name__ = fname
    return f


CANDIDATES_B6 = {
    "t6_het6a": (_mk_hetero(SEQ_A, "hetero_het6a"), "heterogeneous cascade A: maj/andor/chi/majxor/xor3and/maj"),
    "t6_het6b": (_mk_hetero(SEQ_B, "hetero_het6b"), "heterogeneous cascade B: chi/maj/andor/xor3and/majxor/chi"),
    "t6_het6c": (_mk_hetero(SEQ_C, "hetero_het6c"), "heterogeneous cascade C: andor/xor3and/maj/chi/majxor/andor"),
}

MIX_NP_B6 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B6.items()}

if __name__ == "__main__":
    for name, (fn, desc) in CANDIDATES_B6.items():
        a = fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))
        b = fn(np.uint64(1), np.uint64(0x123456789ABCDEF0))
        assert a != b, name
        # Quick avalanche check
        v0 = np.uint64(0x123456789ABCDEF0)
        k0 = np.uint64(0xFEDCBA9876543210)
        o0 = fn(v0, k0)
        flips = []
        for i in range(64):
            v1 = v0 ^ (np.uint64(1) << np.uint64(i))
            o1 = fn(v1, k0)
            flips.append(bin(int(o0 ^ o1)).count('1'))
        avg = sum(flips) / len(flips)
        print(f"{name}: ok ({desc}); avalanche avg={avg:.1f}")
