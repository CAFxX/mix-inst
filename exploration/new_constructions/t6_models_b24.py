"""Track 6, batch 24: cross-stage nonlinear coupling (incarnation E).

New axis (not a cascade tweak): each stage feeds its nonlinear product
t_j = (ra_j & rb_j) FORWARD into the next stage:

  t_j   = rot(x_j,a_j) & rot(x_j,b_j)
  x_{j+1} = x_j ^ t_j ^ rot(x_j,c_j) ^ rk_j ^ rot(t_{j-1}, s_j),  t_{-1} = 0

A differential now propagates through TWO paths (the x-chain and the t-chain)
— a second-order recurrence, qualitatively different from the memoryless
cascade. Bijectivity: t_{j-1} is stage-constant, so each stage is the proven
`x ^= N(x) ^ const` skeleton in x_j. The extra term is one XOR input
(free wiring for the rotation); estimated cost ~+0.4-0.5u/stage over the
3.35u baseline.

The prize: if coupling buys the diffusion of 6 stages in 5, the 5-stage
variant lands ~19u < 20.1u frontier. The 4-stage probe tests whether coupling
doubles the per-stage diffusion (4 x ~3.8 = ~15u would smash the frontier
IF quality holds — high risk, high reward).

Candidates:
  t6_xc5a: 5-stage cross-coupled            (frontier challenger)
  t6_xc6a: 6-stage cross-coupled            (control: per-stage cost + quality floor)
  t6_xc5b: 5-stage cross-coupled, alt sched  (axis robustness)
  t6_xc4a: 4-stage cross-coupled            (aggressive diffusion probe)
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]

# Schedules: (a, b, c, s): t=ra&rb, linear rc, coupled rot(t_prev, s)
XC_SCHED5 = [(5, 17, 29, 7), (11, 23, 37, 13), (3, 19, 31, 19),
             (13, 27, 39, 23), (7, 21, 33, 29)]
XC_SCHED6 = [(5, 17, 29, 7), (11, 23, 37, 13), (3, 19, 31, 19),
             (13, 27, 39, 23), (7, 21, 33, 29), (15, 25, 35, 31)]
XC_SCHED5B = [(9, 25, 43, 3), (19, 33, 47, 11), (1, 23, 37, 17),
              (11, 29, 41, 21), (21, 35, 49, 27)]
XC_SCHED4 = [(5, 17, 29, 7), (11, 23, 37, 13), (3, 19, 31, 19),
             (13, 27, 39, 23)]


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


def _xc(x, k, sched):
    t_prev = np.uint64(0)
    if not np.ndim(x) == 0:
        t_prev = np.zeros_like(x)
    for j, s in enumerate(sched):
        a, b, c, rot = s
        t = _rotl64(x, a) & _rotl64(x, b)
        x = (x ^ t ^ _rotl64(x, c) ^ _rk(k, j) ^ _rotl64(t_prev, rot)) & M64
        t_prev = t
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def t6_xc5a(v, k):
    """5-stage cross-coupled cascade (frontier challenger)."""
    x = (v ^ k) & M64
    return _xc(x, k, XC_SCHED5)


def t6_xc6a(v, k):
    """6-stage cross-coupled cascade (control)."""
    x = (v ^ k) & M64
    return _xc(x, k, XC_SCHED6)


def t6_xc5b(v, k):
    """5-stage cross-coupled cascade, alternate schedule."""
    x = (v ^ k) & M64
    return _xc(x, k, XC_SCHED5B)


def t6_xc4a(v, k):
    """4-stage cross-coupled cascade (aggressive diffusion probe)."""
    x = (v ^ k) & M64
    return _xc(x, k, XC_SCHED4)


CANDIDATES_B24 = {
    "t6_xc5a": (t6_xc5a, "5-stage cross-coupled cascade, frontier challenger"),
    "t6_xc6a": (t6_xc6a, "6-stage cross-coupled cascade, control"),
    "t6_xc5b": (t6_xc5b, "5-stage cross-coupled cascade, alt schedule"),
    "t6_xc4a": (t6_xc4a, "4-stage cross-coupled cascade, aggressive probe"),
}
