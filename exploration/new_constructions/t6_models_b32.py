"""Track 6, batch 32: post-cascade structural axes.

Batch-31 verdict: the 4/5-stage DIFF wall holds against AND-order (b30),
final-form nonlinearity (b31A chi-final), and diffusion-permutation shape
(b31B). The wall is a property of the uniform 5-stage AND-cascade skeleton
itself. Batch 32 therefore abandons the uniform cascade skeleton entirely.
Three genuinely new structural axes (none tested in any track):

(A) cross-fed dual-lane cascade: two 64-bit lanes evolve in parallel.
    Lane A: 3-stage (or 4-stage) AND cascade on x0 = v^k (proven skeleton).
    Lane B: 3-stage (4-stage) AND cascade on b0 = rot(k,29), each stage fed
    rot(a_j, s_j) one-way from lane A:
        b_{j+1} = b_j ^ (rb_j & rc_j) ^ rot(b_j, d_j) ^ rot(a_j, s_j).
    Output: out = a_N ^ b_N ^ rot(k,13).
    Bijectivity: a-chain bijective (proven skeleton); each b-stage is
    b -> b ^ F(b) ^ const(a_j), bijective for fixed a_j; composition of
    bijective stages is bijective. The output fold is 2:1 (fine for a
    finalizer). Crit path ~= N stages + 3-operand fold XOR (~11.8u at N=3).
    The lanes are NOT a cascade -- differentials propagate through two
    coupled recurrences with a one-way nonlinear cross-feed.

(B) AND-sandwich stage: the stage function is genuinely new --
    x ^= rot(x,a) ^ (rot(x,b) & rot(x,c)) ^ rot(x,d),
    i.e. TWO direct linear rotations with the AND product BETWEEN them,
    vs al_and6a's one linear rotation + AND product. 4 XOR operands + 1 AND
    (2-level XOR2 tree). Frontier key schedule (pre-whiten + final).
    (b,c) close (|b-c|<=2) for SEQ-safety.

(C) skip-coupled cascade: 4/5-stage cascade with residual coupling on the
    x-STATE (batch 24 coupled the t-terms; this is different):
        x_j = x_{j-1} ^ t_{j-1} ^ rot(x_{j-1}, d_j) ^ rot(x_{j-2}, s_j),
    x_0 = v^k, x_{-1} = 0, t_{j-1} = rot(x_{j-1},a_j) & rot(x_{j-1},b_j).
    Each stage is x -> x ^ const(x_{j-2}) -- bijective. The skip gives
    differentials a linear bypass around the stage's AND (distinct from the
    per-stage x^= path, which stays local).

Candidates:
  - t6_lane3a: 3+3 lanes, sched A
  - t6_lane3b: 3+3 lanes, sched B (robustness)
  - t6_lane4a: 4+4 lanes, sched A (quality-safety variant)
  - t6_sand5a: 5-stage sandwich, sched A
  - t6_sand5b: 5-stage sandwich, sched B (robustness)
  - t6_sand4a: 4-stage sandwich, sched C (wall probe)
  - t6_skip4a: 4-stage skip-coupled
  - t6_skip5a: 5-stage skip-coupled
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


# (A) lane schedules: (a_pairs, b_pairs, feed_rotations)
LANE3A_A = [((1, 2), 7), ((5, 6), 23), ((9, 10), 41)]
LANE3A_B = [((13, 14), 29), ((17, 18), 11), ((21, 22), 37)]
LANE3A_S = [3, 17, 31]

LANE3B_A = [((3, 4), 13), ((7, 8), 31), ((11, 12), 5)]
LANE3B_B = [((15, 16), 43), ((19, 20), 27), ((23, 24), 9)]
LANE3B_S = [23, 7, 37]

LANE4A_A = [((1, 2), 7), ((5, 6), 23), ((9, 10), 41), ((13, 14), 29)]
LANE4A_B = [((17, 18), 11), ((21, 22), 37), ((25, 26), 3), ((29, 30), 19)]
LANE4A_S = [3, 17, 31, 43]


def _lanes(x0, b0, sa, sb, feed):
    a = x0
    b = b0
    for j, (((pa, qa), da), ((pb, qb), db), s) in enumerate(zip(sa, sb, feed)):
        an = (a ^ (_rotl64(a, pa) & _rotl64(a, qa)) ^ _rotl64(a, da)) & M64
        bn = (b ^ (_rotl64(b, pb) & _rotl64(b, qb)) ^ _rotl64(b, db)
              ^ _rotl64(a, s)) & M64
        a, b = an, bn
    return a, b


def t6_lane3a(v, k):
    a, b = _lanes((v ^ k) & M64, _rotl64(k, 29), LANE3A_A, LANE3A_B, LANE3A_S)
    return (a ^ b ^ _rotl64(k, 13)) & M64


def t6_lane3b(v, k):
    a, b = _lanes((v ^ k) & M64, _rotl64(k, 29), LANE3B_A, LANE3B_B, LANE3B_S)
    return (a ^ b ^ _rotl64(k, 13)) & M64


def t6_lane4a(v, k):
    a, b = _lanes((v ^ k) & M64, _rotl64(k, 29), LANE4A_A, LANE4A_B, LANE4A_S)
    return (a ^ b ^ _rotl64(k, 13)) & M64


# (B) sandwich schedules: (a, (b, c), d)
SAND5A = [(3, (1, 2), 7), (11, (5, 6), 23), (19, (9, 10), 41),
          (27, (13, 14), 29), (35, (17, 18), 11)]
SAND5B = [(5, (3, 4), 13), (17, (7, 8), 31), (29, (11, 12), 5),
          (41, (15, 16), 43), (9, (19, 20), 27)]
SAND4A = [(7, (1, 2), 19), (23, (5, 6), 11), (39, (9, 10), 3),
          (15, (13, 14), 47)]


def _sandwich(x, sched):
    for a, (b, c), d in sched:
        x = (x ^ _rotl64(x, a) ^ (_rotl64(x, b) & _rotl64(x, c))
             ^ _rotl64(x, d)) & M64
    return x


def t6_sand5a(v, k):
    return (_sandwich((v ^ k) & M64, SAND5A) ^ _rotl64(k, 13)) & M64


def t6_sand5b(v, k):
    return (_sandwich((v ^ k) & M64, SAND5B) ^ _rotl64(k, 13)) & M64


def t6_sand4a(v, k):
    return (_sandwich((v ^ k) & M64, SAND4A) ^ _rotl64(k, 13)) & M64


# (C) skip-coupled schedules: ((a, b), d, s)
SKIP4A = [((1, 2), 7, 13), ((5, 6), 23, 29), ((9, 10), 41, 3),
          ((13, 14), 29, 47)]
SKIP5A = [((1, 2), 7, 13), ((5, 6), 23, 29), ((9, 10), 41, 3),
          ((13, 14), 29, 47), ((17, 18), 11, 59)]


def _skipcascade(x0, sched):
    xm1 = np.zeros_like(np.asanyarray(x0, dtype=np.uint64))
    x = np.asanyarray(x0, dtype=np.uint64)
    for (a, b), d, s in sched:
        xn = (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rotl64(x, d)
              ^ _rotl64(xm1, s)) & M64
        xm1, x = x, xn
    return x


def t6_skip4a(v, k):
    return (_skipcascade((v ^ k) & M64, SKIP4A) ^ _rotl64(k, 13)) & M64


def t6_skip5a(v, k):
    return (_skipcascade((v ^ k) & M64, SKIP5A) ^ _rotl64(k, 13)) & M64


CANDIDATES_B32 = {
    "t6_lane3a": (t6_lane3a, "3+3 cross-fed dual-lane cascade, sched A"),
    "t6_lane3b": (t6_lane3b, "3+3 cross-fed dual-lane cascade, sched B"),
    "t6_lane4a": (t6_lane4a, "4+4 cross-fed dual-lane cascade, sched A"),
    "t6_sand5a": (t6_sand5a, "5-stage AND-sandwich x^=ra^(rb&rc)^rd, sched A"),
    "t6_sand5b": (t6_sand5b, "5-stage AND-sandwich x^=ra^(rb&rc)^rd, sched B"),
    "t6_sand4a": (t6_sand4a, "4-stage AND-sandwich, sched C (wall probe)"),
    "t6_skip4a": (t6_skip4a, "4-stage skip-coupled cascade (x-state residual)"),
    "t6_skip5a": (t6_skip5a, "5-stage skip-coupled cascade (x-state residual)"),
}
