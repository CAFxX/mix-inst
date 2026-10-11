"""Track 6, batch 18: S-box + P-box SPN (new paradigm).

Batches 8-17 exhausted AND-cascade variants and several new structures.
Untested paradigm: classic SPN with 4-bit S-boxes and a REAL bit-permutation
(P-box), not rotations. Batch 15 proved rotations don't diffuse for S-boxes
(cyclic shifts preserve adjacency); a P-box gives exponential spread.

Design: PRESENT-style. 16 parallel Midori Sb0 4-bit S-boxes (~3u) + pLayer
P(i) = 16*i mod 63 (0u, wiring) + key xor (1u) = ~4u/round.
  4 rounds = ~16u, 5 rounds = ~20u, 6 rounds = ~24u.

PRESENT needs 31 rounds for crypto, but our bar is S1 statistical. Tests:
  t6_sboxp4a: 4 rounds. Est ~16u. Boundary test.
  t6_sboxp5a: 5 rounds. Est ~20u. Tie-or-win.
  t6_sboxp6a: 6 rounds. Est ~24u. Quality control (if 6 passes but 4/5 fail,
               we learn the round requirement for this family).

All: x = val ^ key; per round: x ^= rk_j; x = SBOX16(x); x = PBOX(x);
post-whiten x ^= rotl64(key,13) >> 32.
rk_j = rotl64(key,13*(j+1)) ^ RC64[j%8].
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]

SBOX_MIDORI0 = np.array([0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7,
                         0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6],
                        dtype=np.uint64)

# PRESENT pLayer: out[P(i)] = in[i], P(i) = 16*i mod 63 (i<63), P(63)=63.
PBOX = [(16 * i) % 63 if i < 63 else 63 for i in range(64)]
# Inverse: for model we apply out[P(i)] = in[i].


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


def _postwhite(x, k):
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def _sbox16(x):
    y = np.zeros_like(x)
    for i in range(16):
        y |= SBOX_MIDORI0[((x >> np.uint64(4 * i)) & np.uint64(0xF))] << np.uint64(4 * i)
    return y & M64


def _pbox(x):
    # out[P(i)] = in[i]
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << np.uint64(PBOX[i])
    return y & M64


def _spn(v, k, nrounds):
    x = v ^ k
    for j in range(nrounds):
        x = (x ^ _rk(k, j)) & M64
        x = _sbox16(x)
        x = _pbox(x)
    return _postwhite(x, k)


def t6_sboxp4a(v, k):
    """4-round S-box+P-box SPN."""
    return _spn(v, k, 4)


def t6_sboxp5a(v, k):
    """5-round S-box+P-box SPN."""
    return _spn(v, k, 5)


def t6_sboxp6a(v, k):
    """6-round S-box+P-box SPN (quality control)."""
    return _spn(v, k, 6)


CANDIDATES_B18 = {
    "t6_sboxp4a": (t6_sboxp4a, "4-round Midori-Sb0 + PRESENT pLayer SPN"),
    "t6_sboxp5a": (t6_sboxp5a, "5-round Midori-Sb0 + PRESENT pLayer SPN"),
    "t6_sboxp6a": (t6_sboxp6a, "6-round Midori-Sb0 + PRESENT pLayer SPN (QC)"),
}
