"""Track 6, batch 20: AND-cascade + S-box super-stage hybrid.

Last structural idea: 4 uniform AND-stages (provide linear terms for LIN-
safety and baseline diffusion) + 1 S-box+P-box super-stage (provides strong
nonlinearity). The S-box stage is the "6th AND-depth equivalent" but stronger.

  4x [x ^= (ra&rb)^rc^rk] (3.35u each = 13.4u)
  1x [x ^= rk; x = SBOX16(x); x = PBOX(x)] (~4u)
  Total est ~17.4u (theoretical; heterogeneity may cost more).

Candidates:
  t6_hyb5e: 4 AND + S-box super-stage LAST.
  t6_hyb5f: S-box super-stage FIRST + 4 AND.

If the heterogeneity penalty pushes these over 20.1u, the structural search
is exhausted and the frontier stands.
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
PBOX = [(16 * i) % 63 if i < 63 else 63 for i in range(64)]


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


def _sbox16(x):
    y = np.zeros_like(x)
    for i in range(16):
        y |= SBOX_MIDORI0[((x >> np.uint64(4 * i)) & np.uint64(0xF))] << np.uint64(4 * i)
    return y & M64


def _pbox(x):
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << np.uint64(PBOX[i])
    return y & M64


AND_SCHED = [(3, 11, 23), (17, 29, 41), (7, 31, 47), (23, 43, 59)]


def _and_stage(x, k, sched_idx, rk_idx):
    a, b, c = AND_SCHED[sched_idx]
    return (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rotl64(x, c) ^ _rk(k, rk_idx)) & M64


def _sbox_stage(x, k, j):
    x = (x ^ _rk(k, j)) & M64
    x = _sbox16(x)
    return _pbox(x)


def t6_hyb5e(v, k):
    """4 AND-stages + S-box super-stage LAST."""
    x = v ^ k
    for j in range(4):
        x = _and_stage(x, k, j, j)
    x = _sbox_stage(x, k, 4)
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def t6_hyb5f(v, k):
    """S-box super-stage FIRST + 4 AND-stages."""
    x = v ^ k
    x = _sbox_stage(x, k, 0)
    for j in range(4):
        x = _and_stage(x, k, j, j + 1)
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


CANDIDATES_B20 = {
    "t6_hyb5e": (t6_hyb5e, "4 AND-stages + S-box+P-box super-stage last"),
    "t6_hyb5f": (t6_hyb5f, "S-box+P-box super-stage first + 4 AND-stages"),
}
