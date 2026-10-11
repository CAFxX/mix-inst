"""Track 6, batch 23: parallel-with-nonlinear-combine (incarnation E).

Genuinely new axis (not a cascade tweak): each stage computes TWO (or three)
independent 2-input AND products IN PARALLEL (same depth-1 as one AND), then
combines them NONLINEARLY at the same gate depth:

  x ^= (p1 & ~p2) ^ re ^ rk        (chi-style combine: AND with inverted input
                                    is ONE AIG node — same depth as plain AND)

p1 = ra&rb, p2 = rc&rd run in parallel; the combine (p1 & ~p2) is nonlinear in
(p1,p2) but costs no extra gate level vs the standard stage
`x ^= (ra&rb)^rc^rk` (3.35u/stage). Estimate: ~3.4-3.6u/stage.

The prize: a STRONGER nonlinear term per stage at the same depth. If the
chi-combine breaks the 5-stage DIFF wall (t6_and5a 17.2u died there), the
5-stage chi variant lands ~17u < 20.1u frontier.

Candidates:
  t6_pchi6a: 6-stage chi-combine (p1&~p2) + linear re   (frontier challenger)
  t6_pchi5a: 5-stage chi-combine                       (DIFF-wall probe)
  t6_pxor6a: 6-stage parallel LINEAR combine            (control: isolates
              nonlinear-vs-linear combine effect)
  t6_pchi6b: 6-stage chi-combine (~p1&p2), alt schedule (axis robustness)

Bijectivity: same `x ^= N(x) ^ rk` skeleton as the established AND-cascade
family; every candidate gated by bijectivity_spotcheck (3 keys x 200k) +
model/impl.c/RTL bit-exactness before S0.
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]

# Schedules: (a,b,c,d,e): p1=ra&rb, p2=rc&rd, linear re
PCHI_SCHED6 = [(5, 17, 29, 41, 53), (11, 23, 37, 47, 7), (3, 19, 31, 43, 59),
               (13, 27, 39, 51, 9), (7, 21, 33, 45, 57), (15, 25, 35, 49, 61)]
PCHI_SCHED5 = [(5, 17, 29, 41, 53), (11, 23, 37, 47, 7), (3, 19, 31, 43, 59),
               (13, 27, 39, 51, 9), (7, 21, 33, 45, 57)]
# (a,b,c,d,e,f): p1=ra&rb, p2=rc&rd, p3=re&rf (linear combine control)
PXOR_SCHED6 = [(5, 17, 29, 41, 53, 61), (11, 23, 37, 47, 7, 59),
               (3, 19, 31, 43, 57, 9), (13, 27, 39, 51, 21, 63),
               (1, 15, 25, 35, 45, 55), (9, 22, 34, 46, 58, 62)]
# alt schedule for the (~p1&p2) variant
PCHI_SCHED6B = [(9, 25, 43, 55, 3), (19, 33, 47, 61, 13), (1, 23, 37, 53, 17),
                (11, 29, 41, 59, 7), (21, 35, 49, 63, 5), (15, 31, 45, 57, 27)]


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


def _pchi(x, k, sched, invert_first):
    """Shared chi-combine stage loop. invert_first=True -> (p1 & ~p2)."""
    for j, s in enumerate(sched):
        a, b, c, d, e = s
        p1 = _rotl64(x, a) & _rotl64(x, b)
        p2 = _rotl64(x, c) & _rotl64(x, d)
        if invert_first:
            comb = p1 & ~p2
        else:
            comb = ~p1 & p2
        x = (x ^ comb ^ _rotl64(x, e) ^ _rk(k, j)) & M64
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def t6_pchi6a(v, k):
    """6-stage parallel chi-combine: x ^= (p1&~p2)^re^rk."""
    x = (v ^ k) & M64
    return _pchi(x, k, PCHI_SCHED6, True)


def t6_pchi5a(v, k):
    """5-stage parallel chi-combine: DIFF-wall probe at ~17u."""
    x = (v ^ k) & M64
    return _pchi(x, k, PCHI_SCHED5, True)


def t6_pchi6b(v, k):
    """6-stage parallel chi-combine: x ^= (~p1&p2)^re^rk, alt schedule."""
    x = (v ^ k) & M64
    return _pchi(x, k, PCHI_SCHED6B, False)


def t6_pxor6a(v, k):
    """6-stage parallel LINEAR combine (control): x ^= p1^p2^p3^rk."""
    x = (v ^ k) & M64
    for j, s in enumerate(PXOR_SCHED6):
        a, b, c, d, e, f = s
        p1 = _rotl64(x, a) & _rotl64(x, b)
        p2 = _rotl64(x, c) & _rotl64(x, d)
        p3 = _rotl64(x, e) & _rotl64(x, f)
        x = (x ^ p1 ^ p2 ^ p3 ^ _rk(k, j)) & M64
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


CANDIDATES_B23 = {
    "t6_pchi6a": (t6_pchi6a, "6-stage parallel chi-combine (p1&~p2), frontier challenger"),
    "t6_pchi5a": (t6_pchi5a, "5-stage parallel chi-combine, DIFF-wall probe"),
    "t6_pxor6a": (t6_pxor6a, "6-stage parallel linear combine (control)"),
    "t6_pchi6b": (t6_pchi6b, "6-stage parallel chi-combine (~p1&p2), alt schedule"),
}
