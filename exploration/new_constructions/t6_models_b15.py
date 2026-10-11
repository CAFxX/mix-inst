"""Track 6, batch 15: genuinely new axes beyond the cascade (post-14-batch restart).

Batches 8-14 exhausted: homogeneous AND-cascade (20.1u floor), fused
single-op (S1-dead), hetero simple ops (dominated), 5-stage (DIFF-dead),
wide 4-stage (dominated), Feistel (dominated), per-stage rk (dominated),
hetero-strength (DIFF-dead). Findings: outer x^= load-bearing; 6 AND-depths
minimum for DIFF; rc linear term load-bearing per stage.

Batch 15 probes:
  t6_norc6a : 6-stage `x ^= (ra&rb) ^ rk` — NO linear rc term. Clean test of
              whether rc is load-bearing for QUALITY at 6 stages. ~2.4u/stg.
  t6_norc6b : same, alternate schedule (schedule sensitivity of no-rc).
  t6_norc7a : 7-stage no-rc — if 6 fails DIFF but 7 passes at ~17u, frontier.
  t6_norc5a : 5-stage no-rc — 5-stage barrier for the no-rc family.
  t6_wide6a : 6-stage `x ^= (ra&rb)^(rc&rd)^re ^ rk` — two PARALLEL AND terms
              per stage (parallel nonlinear work per gate-delay).
  t6_split3a: 3 super-stages: 64-bit state split into 32-bit halves; each
              half runs a 2-stage AND-cascade IN PARALLEL; halves cross.
              6 AND-depths per half in ~3 super-stage delays.
  t6_quad3a : 4x16-bit lanes; each lane a 2-stage AND-cascade in parallel;
              full cross every super-stage. 16-bit stages ~2.5u.
  t6_sboxrot6: 6 rounds Midori-Sb0 nibble layer + rotation + key xor; NO
              linear mixing layer (diffusion via rotation across nibbles).

All: x = val ^ key; rk_j = rotl64(key,13*(j+1)) ^ RC64[j%8];
post-whiten x ^= rotl64(key,13) >> 32 (comparability with b6/b8/b9).
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint64(0xFFFFFFFF)
M16 = np.uint64(0xFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]

SBOX_MIDORI0 = np.array([0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7,
                         0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6],
                        dtype=np.uint64)


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rotl32(x, r):
    r %= 32
    x = x & M32
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & M32


def _rotl16(x, r):
    r %= 16
    x = x & M16
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(16 - r))) & M16


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


def _postwhite(x, k):
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def _sbox_nibbles(x, sbox):
    y = np.zeros_like(x)
    for i in range(16):
        y |= sbox[((x >> np.uint64(4 * i)) & np.uint64(0xF))] << np.uint64(4 * i)
    return y & M64


# --- schedules (all rotations within a stage distinct) ---
SCHED_NORC6A = [(1, 23), (5, 37), (11, 43), (17, 53), (29, 7), (41, 13)]
SCHED_NORC6B = [(7, 31), (13, 41), (19, 47), (23, 59), (3, 17), (11, 29)]
SCHED_NORC7A = [(1, 23), (5, 37), (11, 43), (17, 53), (29, 7), (41, 13), (43, 19)]
SCHED_NORC5A = [(1, 23), (5, 37), (11, 43), (17, 53), (29, 7)]
SCHED_WIDE6A = [(3, 11, 23, 37, 53), (7, 17, 29, 43, 59),
                (13, 27, 41, 5, 31), (19, 33, 47, 11, 61),
                (23, 39, 53, 17, 7), (29, 45, 59, 23, 13)]
# split3a: base triples per (super-stage, sub-stage); lane offset added mod 32
SPLIT_BASE = [[(3, 11, 23), (13, 29, 7)],
              [(17, 5, 27), (23, 9, 15)],
              [(29, 13, 3), (7, 19, 25)]]
SPLIT_CROSS = [(5, 9), (11, 15), (17, 21)]
# quad3a: base triples per (super-stage, sub-stage); lane offset added mod 16
QUAD_BASE = [[(3, 9, 13), (7, 2, 11)],
             [(11, 5, 1), (13, 8, 4)],
             [(6, 12, 2), (9, 4, 14)]]
QUAD_CROSS = [(3, 7), (5, 11), (9, 13)]
SBOX_ROTS = [7, 23, 41, 11, 29, 53]


def _norc_cascade(v, k, sched):
    x = v ^ k
    for j, (a, b) in enumerate(sched):
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rk(k, j)) & M64
    return _postwhite(x, k)


def t6_norc6a(v, k):
    """6-stage AND-cascade, no linear rc term."""
    return _norc_cascade(v, k, SCHED_NORC6A)


def t6_norc6b(v, k):
    """6-stage AND-cascade no-rc, alternate schedule."""
    return _norc_cascade(v, k, SCHED_NORC6B)


def t6_norc7a(v, k):
    """7-stage AND-cascade, no linear rc term."""
    return _norc_cascade(v, k, SCHED_NORC7A)


def t6_norc5a(v, k):
    """5-stage AND-cascade, no linear rc term."""
    return _norc_cascade(v, k, SCHED_NORC5A)


def t6_wide6a(v, k):
    """6-stage, two parallel AND terms: x ^= (ra&rb)^(rc&rd)^re ^ rk."""
    x = v ^ k
    for j, (a, b, c, d, e) in enumerate(SCHED_WIDE6A):
        nl = ((_rotl64(x, a) & _rotl64(x, b)) ^
              (_rotl64(x, c) & _rotl64(x, d)) ^ _rotl64(x, e))
        x = (x ^ nl ^ _rk(k, j)) & M64
    return _postwhite(x, k)


def t6_split3a(v, k):
    """3 super-stages: parallel 32-bit 2-stage cascades per half + cross."""
    x = v ^ k
    for s in range(3):
        lo = x & M32
        hi = (x >> np.uint64(32)) & M32
        for t in range(2):
            j = 2 * s + t
            b1, b2, b3 = SPLIT_BASE[s][t]
            # lo uses base triple, hi uses base triple offset by +7 (mod 32)
            p = ((b1) % 32, (b2) % 32, (b3) % 32)
            q = ((b1 + 7) % 32, (b2 + 7) % 32, (b3 + 7) % 32)
            lo = (lo ^ (_rotl32(lo, p[0]) & _rotl32(lo, p[1])) ^
                  _rotl32(lo, p[2]) ^ (_rk(k, j) & M32)) & M32
            hi = (hi ^ (_rotl32(hi, q[0]) & _rotl32(hi, q[1])) ^
                  _rotl32(hi, q[2]) ^ (_rk(k, j) & M32)) & M32
            hi = hi & M32
        r1, r2 = SPLIT_CROSS[s]
        nlo = (lo ^ _rotl32(hi, r1) ^ (_rk(k, 6 + 2 * s) & M32)) & M32
        nhi = (hi ^ _rotl32(lo, r2) ^ (_rk(k, 7 + 2 * s) & M32)) & M32
        x = (nlo | (nhi << np.uint64(32))) & M64
    return _postwhite(x, k)


def t6_quad3a(v, k):
    """3 super-stages: 4 parallel 16-bit 2-stage cascades + full cross."""
    x = v ^ k
    for s in range(3):
        lanes = [(x >> np.uint64(16 * i)) & M16 for i in range(4)]
        for t in range(2):
            j = 2 * s + t
            b1, b2, b3 = QUAD_BASE[s][t]
            new = []
            for i in range(4):
                p1, p2, p3 = (b1 + 5 * i) % 16, (b2 + 5 * i) % 16, (b3 + 5 * i) % 16
                li = lanes[i]
                li = (li ^ (_rotl16(li, p1) & _rotl16(li, p2)) ^
                      _rotl16(li, p3) ^ (_rk(k, j) & M16)) & M16
                new.append(li)
            lanes = new
        c1, c2 = QUAD_CROSS[s]
        out = []
        for i in range(4):
            ni = (lanes[i] ^ _rotl16(lanes[(i + 1) % 4], c1) ^
                  _rotl16(lanes[(i + 2) % 4], c2) ^
                  (_rk(k, 6 + 2 * s + i) & M16)) & M16
            out.append(ni)
        x = (out[0] | (out[1] << np.uint64(16)) |
             (out[2] << np.uint64(32)) | (out[3] << np.uint64(48))) & M64
    return _postwhite(x, k)


def t6_sboxrot6(v, k):
    """6 rounds: key xor, Midori-Sb0 nibble layer, rotation. No linear layer."""
    x = v ^ k
    for j in range(6):
        x = (x ^ _rk(k, j)) & M64
        x = _sbox_nibbles(x, SBOX_MIDORI0)
        x = _rotl64(x, SBOX_ROTS[j])
    return _postwhite(x, k)


CANDIDATES_B15 = {
    "t6_norc6a": (t6_norc6a, "6-stage AND-cascade, no linear rc term"),
    "t6_norc6b": (t6_norc6b, "6-stage AND-cascade no-rc, alt schedule"),
    "t6_norc7a": (t6_norc7a, "7-stage AND-cascade, no linear rc term"),
    "t6_norc5a": (t6_norc5a, "5-stage AND-cascade, no linear rc term"),
    "t6_wide6a": (t6_wide6a, "6-stage dual parallel AND terms + linear"),
    "t6_split3a": (t6_split3a, "3 super-stages, parallel 32-bit cascades + cross"),
    "t6_quad3a": (t6_quad3a, "3 super-stages, 4 parallel 16-bit cascades + cross"),
    "t6_sboxrot6": (t6_sboxrot6, "6 rounds Midori-Sb0 + rotation, no linear layer"),
}
