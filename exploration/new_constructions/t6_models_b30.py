"""Track 6, batch 30: wide-AND + spread, frontier key schedule.

Batch-29 root cause (measured): the +1.4u/stage vs al_and6a is NOT the AND3 --
it is the t6 per-stage-rk convention. `x ^ t ^ r ^ rk` is a 4-operand XOR
that ABC chains as 3 XOR2 levels (+2u); al_and6a's `x ^ t ^ r` (3 operands,
pre-whiten + final key only) holds 2 levels. The AND3 itself costs +0.2u
(1.7 vs 1.5). This batch ports the batch-29 stages onto the frontier's key
schedule: pre-whiten x0 = v^k, stages x ^= (AND) ^ rot(x,d), final
out = xN ^ rot(k,13). Projected: 23.7 - 5*1.4 ~= 16.7u for 5-stage AND3.

  - t6_wand3_5c: 5-stage AND3+spread, al key schedule, sched A
  - t6_wand3_5d: 5-stage AND3+spread, al key schedule, sched B (robustness)
  - t6_wand3_4b: 4-stage AND3+spread, al key schedule (order-3 wall test)
  - t6_wand4_5b: 5-stage AND4+spread, al key schedule (order-4 density probe)

Bijectivity: x ^= N(x) (no per-stage constant needed; pre-whiten+final keep
the keyed-permutation structure, same as the frontier).
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _u64(hi, lo):
    return (np.uint64(hi) << np.uint64(32)) | np.uint64(lo)


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


# entries: (and_operands_tuple, spread_rotation) -- same schedules as b29
WAND3_5A = [((1, 2, 3), 13), ((11, 12, 13), 5), ((5, 6, 7), 29),
            ((17, 18, 19), 7), ((25, 26, 27), 37)]
WAND3_5B = [((3, 4, 5), 23), ((13, 14, 15), 41), ((7, 8, 9), 17),
            ((21, 22, 23), 11), ((29, 30, 31), 43)]
WAND3_4A = [((1, 2, 3), 13), ((11, 12, 13), 5), ((5, 6, 7), 29),
            ((17, 18, 19), 7)]
WAND4_5A = [((1, 2, 3, 4), 13), ((11, 12, 13, 14), 29), ((21, 22, 23, 24), 7),
            ((31, 32, 33, 34), 37), ((41, 42, 43, 44), 17)]


def _wide(x, k, sched):
    for j, (ops, d) in enumerate(sched):
        t = _rotl64(x, ops[0])
        for a in ops[1:]:
            t = t & _rotl64(x, a)
        x = (x ^ t ^ _rotl64(x, d)) & M64
    return (x ^ _rotl64(k, 13)) & M64


def t6_wand3_5c(v, k):
    """5-stage AND3+spread, al key schedule, sched A."""
    return _wide((v ^ k) & M64, k, WAND3_5A)


def t6_wand3_5d(v, k):
    """5-stage AND3+spread, al key schedule, sched B (robustness)."""
    return _wide((v ^ k) & M64, k, WAND3_5B)


def t6_wand3_4b(v, k):
    """4-stage AND3+spread, al key schedule (order-3 wall test)."""
    return _wide((v ^ k) & M64, k, WAND3_4A)


def t6_wand4_5b(v, k):
    """5-stage AND4+spread, al key schedule (order-4 density probe)."""
    return _wide((v ^ k) & M64, k, WAND4_5A)


CANDIDATES_B30 = {
    "t6_wand3_5c": (t6_wand3_5c, "5-stage AND3+spread, al key schedule, sched A"),
    "t6_wand3_5d": (t6_wand3_5d, "5-stage AND3+spread, al key schedule, sched B"),
    "t6_wand3_4b": (t6_wand3_4b, "4-stage AND3+spread, al key schedule"),
    "t6_wand4_5b": (t6_wand4_5b, "5-stage AND4+spread, al key schedule"),
}
