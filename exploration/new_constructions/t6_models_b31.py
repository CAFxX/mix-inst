"""Track 6, batch 31: the "final-form" probe.

b30 verdict: the 5-stage DIFF wall is NOT about per-stage nonlinear order
(order-3/4 AND3/AND4 S1-killed with LIN near-clean but DIFF catastrophic).
The open hypothesis: the wall is about the FINAL stage's functional form --
a last nonlinear layer with no outer x^= linear path forces every
differential through a full nonlinear map, redistributing differential mass.

Two genuinely new sub-axes (neither tested in any track):

(A) chi-final: 5-stage (and 4-stage) AND cascade on the frontier skeleton
    (pre-whiten x0=v^k, stages x ^= (ra&rb) ^ rot(x,d), close AND pairs
    |a-b|<=2 for SEQ-safety), then FINAL x = chi64(x) ^ rot(k,13).
    chi64(x)_i = x_i ^ (~x_{i+1} & x_{i+2}), indices mod 64.
    NOTE: chi is a permutation only for odd n; at n=64 it is NOT bijective.
    No bijectivity claim -- statistical quality (S1/S2) is the gate.

(B) non-rotational P-box diffusion: 5-stage AND cascade where the linear
    diffusion term is a fixed non-rotation bit permutation P(x)
    (bit-reversal; byte-transpose from batch 21). Still 0-delay wiring, but
    every prior cascade in every track used rotations only. A stronger
    permutation may feed the AND terms a less self-similar bit alignment.

Candidates:
  - t6_chif5a: 5-stage AND + chi-final, sched A
  - t6_chif5b: 5-stage AND + chi-final, sched B (robustness)
  - t6_chif4a: 4-stage AND + chi-final (4-stage wall probe, ~18.5u proj)
  - t6_pbox5a: 5-stage AND + bit-reversal diffusion, sched A
  - t6_pbox5b: 5-stage AND + byte-transpose diffusion, sched A
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _chi64(x):
    """chi64(x)_i = x_i ^ (~x_{i+1} & x_{i+2}), indices mod 64."""
    r1 = _rotl64(x, 63)   # bit i = x_{(i+1) mod 64}
    r2 = _rotl64(x, 62)   # bit i = x_{(i+2) mod 64}
    return (x ^ (~r1 & r2)) & M64


# fixed non-rotation permutations, as index arrays: out[i] = in[P[i]]
def _bitrev_idx():
    return np.array([63 - i for i in range(64)], dtype=np.int64)


def _bytetrans_idx():
    # batch-21 byte-spreading PBOX: out bit 8*j+b <- in bit 8*((j+b)%8)+j
    idx = np.zeros(64, dtype=np.int64)
    for j in range(8):
        for b in range(8):
            idx[8 * j + b] = 8 * ((j + b) % 8) + j
    return idx


_BITREV = _bitrev_idx()
_BYTETR = _bytetrans_idx()
assert len(set(_BITREV.tolist())) == 64 and len(set(_BYTETR.tolist())) == 64


def _pbox64_vec(x, idx):
    # vectorized over arrays
    x = np.asanyarray(x, dtype=np.uint64)
    out = np.zeros_like(x)
    for i in range(64):
        out |= ((x >> np.uint64(idx[i])) & np.uint64(1)) << np.uint64(i)
    return out


# SEQ-co-designed schedules: close AND pairs (|a-b|<=2)
CHF5A = [((1, 2), 7), ((5, 6), 23), ((9, 10), 41), ((13, 14), 29), ((17, 18), 11)]
CHF5B = [((3, 4), 31), ((7, 8), 13), ((11, 12), 37), ((15, 16), 5), ((19, 20), 43)]
CHF4A = [((1, 2), 7), ((5, 6), 23), ((9, 10), 41), ((13, 14), 29)]
PBX5 = [((1, 2),), ((5, 6),), ((9, 10),), ((13, 14),), ((17, 18),)]  # pairs only


def _andcascade(x, sched):
    for ops, d in sched:
        x = (x ^ (_rotl64(x, ops[0]) & _rotl64(x, ops[1])) ^ _rotl64(x, d)) & M64
    return x


def _andcascade_pbox(x, pairs, idx):
    for (ops,) in pairs:
        x = (x ^ (_rotl64(x, ops[0]) & _rotl64(x, ops[1])) ^ _pbox64_vec(x, idx)) & M64
    return x


def t6_chif5a(v, k):
    """5-stage AND + chi-final, sched A."""
    x = _andcascade((v ^ k) & M64, CHF5A)
    return (_chi64(x) ^ _rotl64(k, 13)) & M64


def t6_chif5b(v, k):
    """5-stage AND + chi-final, sched B."""
    x = _andcascade((v ^ k) & M64, CHF5B)
    return (_chi64(x) ^ _rotl64(k, 13)) & M64


def t6_chif4a(v, k):
    """4-stage AND + chi-final (wall probe)."""
    x = _andcascade((v ^ k) & M64, CHF4A)
    return (_chi64(x) ^ _rotl64(k, 13)) & M64


def t6_pbox5a(v, k):
    """5-stage AND + bit-reversal diffusion."""
    x = _andcascade_pbox((v ^ k) & M64, PBX5, _BITREV)
    return (x ^ _rotl64(k, 13)) & M64


def t6_pbox5b(v, k):
    """5-stage AND + byte-transpose diffusion."""
    x = _andcascade_pbox((v ^ k) & M64, PBX5, _BYTETR)
    return (x ^ _rotl64(k, 13)) & M64


CANDIDATES_B31 = {
    "t6_chif5a": (t6_chif5a, "5-stage AND + chi-final, sched A"),
    "t6_chif5b": (t6_chif5b, "5-stage AND + chi-final, sched B"),
    "t6_chif4a": (t6_chif4a, "4-stage AND + chi-final"),
    "t6_pbox5a": (t6_pbox5a, "5-stage AND + bit-reversal diffusion"),
    "t6_pbox5b": (t6_pbox5b, "5-stage AND + byte-transpose diffusion"),
}
