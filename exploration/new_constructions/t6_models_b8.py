"""Track 6, batch 8: FUSED single-op-per-stage constructions (genuinely new axis).

Batch 6 (het6) used `x ^= F(rotations_of_x) ^ rk` — x enters only via the outer
XOR (Track 8's `x ^=` linear-trail concern). Batch 8 FUSES x into the nonlinear
function: `x = F(x, rotations_of_x) ^ rk`.

This is genuinely different from Track 8's fused waves: they XORed 2-3 MUXes per
stage (fz_mux_5: 5.27u/stage). Batch 8 uses ONE op per stage (~3u/stage target).

Per-stage cost estimate: MUX=AND+OR (~2 gates) + XOR rk (~1) ≈ 3u.
6 stages ≈ 18u — potentially under al_and6a's 20.1u frontier.

Candidates (all 6 stages, x = F(x, rots) ^ rk, rk = rotl(k,13*(i+1)) ^ RC[i]):
  t6_fmux6a:    F = MUX(x,ra,rb) = (x&ra)|(~x&rb)
  t6_fmux6b:    F = MUX, alternate rotation schedule
  t6_fchi6a:    F = chi(x,ra,rb) = x ^ (ra & ~rb)   [Keccak chi form]
  t6_fmaj6a:    F = maj(x,ra,rb) = (x&ra)|(x&rb)|(ra&rb)
  t6_fand6a:    F = (x&ra) ^ rb
  t6_fxorand6a: F = (x&ra) ^ (x&rb) ^ rc
  t6_het5a:     5-stage hetero from b6 ops (maj,andor,chi,majxor,xor3and) —
                tests whether 5 stages suffice (t6_aor5b had avalanche PASS
                at 5 stages but 44k-gate S0 timeout; this uses simpler ops)

All include post-whiten x ^= (rotl(k,13) >> 32) for comparability with b6.
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


# Fused ops: x is the first operand, enters nonlinearly.
def _fmux(x, ra, rb):
    return ((x & ra) | ((~x & M64) & rb)) & M64


def _fchi(x, ra, rb):
    return (x ^ (ra & (~rb & M64))) & M64


def _fmaj(x, ra, rb):
    return ((x & ra) | (x & rb) | (ra & rb)) & M64


def _fand(x, ra, rb):
    return ((x & ra) ^ rb) & M64


def _fxorand(x, ra, rb, rc):
    return ((x & ra) ^ (x & rb) ^ rc) & M64


# Rotation schedules: 6 stages. Distinct, well-spread rotations.
SCHED_F2 = [  # 2 rotations per stage (mux/chi/maj/and)
    (11, 29),
    (23, 41),
    (7, 37),
    (19, 53),
    (5, 31),
    (13, 47),
]
SCHED_F2B = [  # alternate schedule for fmux6b
    (17, 43),
    (3, 33),
    (29, 55),
    (11, 39),
    (23, 49),
    (7, 45),
]
SCHED_F3 = [  # 3 rotations per stage (fxorand)
    (11, 29, 47),
    (23, 41, 7),
    (7, 37, 19),
    (19, 53, 5),
    (5, 31, 13),
    (13, 47, 23),
]

# 5-stage hetero schedule (reuse b6-style rotations, 5 stages)
SCHED_HET5 = [
    (11, 23, 37, 5, 17, 29),
    (7, 19, 31, 43, 13, 25),
    (3, 15, 27, 39, 51, 9),
    (21, 33, 45, 1, 35, 47),
    (5, 29, 53, 17, 41, 11),
]
SEQ_HET5 = ["maj", "andor", "chi", "majxor", "xor3and"]
OP_NROTS_B6 = {"maj": 4, "andor": 5, "chi": 3, "majxor": 5, "xor3and": 6}


def _fused_cascade(v, k, fn, sched, nrots):
    x = np.uint64(v) ^ np.uint64(k)
    for i in range(6):
        rots = sched[i][:nrots]
        r = [_rotl64(x, t) for t in rots]
        rk = _rotl64(np.uint64(k), 13 * (i + 1)) ^ RC64[i % 8]
        x = (fn(x, *r) ^ rk) & M64
    x = (x ^ (_rotl64(np.uint64(k), 13) >> np.uint64(32))) & M64
    return x


def _maj(a, b, c):
    return ((a & b) | (a & c) | (b & c)) & M64


def _hetero5_cascade(v, k):
    # 5-stage hetero from b6 ops (same _apply_op semantics as t6_models_b6)
    x = np.uint64(v) ^ np.uint64(k)
    for i, op in enumerate(SEQ_HET5):
        nrots = OP_NROTS_B6[op]
        rots = SCHED_HET5[i][:nrots]
        r = [_rotl64(x, t) for t in rots]
        if op == "maj":
            nl = (_maj(r[0], r[1], r[2]) ^ r[3]) & M64
        elif op == "andor":
            nl = (((r[0] & r[1]) | (r[2] & r[3])) ^ r[4]) & M64
        elif op == "chi":
            nl = (r[0] ^ (r[1] & (~r[2] & M64))) & M64
        elif op == "majxor":
            nl = (_maj(r[0], r[1], r[2]) ^ (r[3] & r[4])) & M64
        elif op == "xor3and":
            nl = (r[0] ^ r[1] ^ r[2] ^ (r[3] & r[4] & r[5])) & M64
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


def _mk_fused(fn, sched, nrots, fname):
    # Named wrapper (never a bare lambda): avoids the '<lambda>' __name__
    # SyntaxError at S1 load time (2026-10-08 lesson).
    def f(v, k):
        return _fused_cascade(v, k, fn, sched, nrots)
    f.__name__ = fname
    return f


def _mk_het5(fname):
    def f(v, k):
        return _hetero5_cascade(v, k)
    f.__name__ = fname
    return f


CANDIDATES_B8 = {
    # Killed 2026-10-09 (pre-synthesis avalanche triage):
    # - t6_fmux6a/b: avalanche avg=10.1, dev=23.25. MUX is a SELECTOR not a
    #   MIXER: output bit i is x_{i+a} or x_{i+b} (chosen by x_i), never a
    #   combination. Single-bit influence grows as ~1.5^stage, not 3^stage.
    #   Structural, not tunable.
    # - t6_fmaj6a: CATASTROPHIC: v=0 and v=1 converge to identical output
    #   after 6 stages. maj(x,rotl(x,11),rotl(x,29)) is a difference
    #   CONTRACTOR (majority vote suppresses small differences). Structural.
    "t6_fchi6a": (_mk_fused(_fchi, SCHED_F2, 2, "fused_fchi6a"),
                  "fused 6-stage chi(x,ra,rb): x^(ra&~rb) [Keccak form]"),
    "t6_fand6a": (_mk_fused(_fand, SCHED_F2, 2, "fused_fand6a"),
                  "fused 6-stage: x=(x&ra)^rb"),
    "t6_fxorand6a": (_mk_fused(_fxorand, SCHED_F3, 3, "fused_fxorand6a"),
                     "fused 6-stage: x=(x&ra)^(x&rb)^rc"),
    "t6_het5a": (_mk_het5("hetero_het5a"),
                 "heterogeneous 5-stage: maj/andor/chi/majxor/xor3and"),
}

MIX_NP_B8 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B8.items()}

if __name__ == "__main__":
    for name, (fn, desc) in CANDIDATES_B8.items():
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
