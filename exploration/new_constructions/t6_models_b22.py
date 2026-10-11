"""Track 6, batch 22: higher-degree AND cascade (incarnation D).

Key insight: t6_xor3and6 (34.3u) was `x ^= ra^rb^rc^(rd&re&rf)` — THREE linear
XORs plus triple-AND (5.7u/stage). But a SINGLE triple-AND with ONE linear term:
  x ^= (ra&rb&rc) ^ rd ^ rk
has the SAME gate depth as al_and6a's `x ^= (ra&rb)^rc^rk` (AND → XOR → XOR → XOR)
but CUBIC nonlinearity vs quadratic. If Yosys hits ~3.35u/stage, we get stronger
mixing per stage at identical latency.

The prize: 5-stage triple-AND might pass DIFF where 5-stage AND (17.2u) died.
5 stages × 3.35u ≈ 16.8u < 20.1u frontier.

Candidates:
  t6_and3_6a: 6-stage triple-AND (control: measures per-stage cost vs AND)
  t6_and3_5a: 5-stage triple-AND (tests cubic vs 5-stage DIFF wall)
  t6_and4_6a: 6-stage quad-AND (quartic; even stronger, same depth)

Avalanche triage gates S0.
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]

# Schedules: (a,b,c,d) for triple-AND + linear; (a,b,c,d,e) for quad-AND + linear
AND3_SCHED6 = [(3, 11, 23, 41), (17, 29, 41, 7), (7, 31, 47, 23),
               (23, 43, 59, 11), (11, 37, 53, 5), (5, 19, 61, 29)]
AND3_SCHED5 = [(3, 11, 23, 41), (17, 29, 41, 7), (7, 31, 47, 23),
               (23, 43, 59, 11), (11, 37, 53, 5)]
AND4_SCHED6 = [(3, 11, 23, 41, 53), (17, 29, 41, 7, 19), (7, 31, 47, 23, 5),
               (23, 43, 59, 11, 37), (11, 37, 53, 5, 61), (5, 19, 61, 29, 43)]


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


def t6_and3_6a(v, k):
    """6-stage triple-AND: x ^= (ra&rb&rc)^rd^rk."""
    x = (v ^ k) & M64
    for j in range(6):
        a, b, c, d = AND3_SCHED6[j]
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b) & _rotl64(x, c))
             ^ _rotl64(x, d) ^ _rk(k, j)) & M64
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def t6_and3_5a(v, k):
    """5-stage triple-AND: tests cubic vs 5-stage DIFF wall."""
    x = (v ^ k) & M64
    for j in range(5):
        a, b, c, d = AND3_SCHED5[j]
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b) & _rotl64(x, c))
             ^ _rotl64(x, d) ^ _rk(k, j)) & M64
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def t6_and4_6a(v, k):
    """6-stage quad-AND: x ^= (ra&rb&rc&rd)^re^rk."""
    x = (v ^ k) & M64
    for j in range(6):
        a, b, c, d, e = AND4_SCHED6[j]
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b) & _rotl64(x, c) & _rotl64(x, d))
             ^ _rotl64(x, e) ^ _rk(k, j)) & M64
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


CANDIDATES_B22 = {
    "t6_and3_6a": (t6_and3_6a, "6-stage triple-AND (cubic control)"),
    "t6_and3_5a": (t6_and3_5a, "5-stage triple-AND (vs DIFF wall)"),
    "t6_and4_6a": (t6_and4_6a, "6-stage quad-AND (quartic)"),
}
