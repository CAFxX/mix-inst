"""Round 4, family M: keyed xorshift-multiply sandwiches (xorshift*/fmix-style).

Untried: murmur-fmix64 skeleton but KEYED and with SPARSE constant mults
(round 2 only tried dense 64-bit consts, all over bar). No wide adds.

  M1 xsm_c3: x=val^key; x^=x>>33; x*=C3; x^=rk1; x^=x>>27; x^=x<<17; x^=rk2; x^=x>>29
     C3 = 0x100000000000003F = 2^60+2^6-2^0 (3 CSD terms, odd)
  M2 xsm_sa: shift-ADD multiplies: x=val^key; x^=x>>33; x=(x<<13)+x; x^=rk1;
     x^=x>>27; x=(x<<29)+x; x^=rk2; x^=x>>31     [(2^k+1) odd => bijective]
  M3 xsm_c8: M1 with C8 = 2^63+2^55+2^47+2^39+2^31+2^23+2^15+2^0 (8 CSD terms)
     and a different shift schedule.

rk[i] = ROTL64(key,13*(i+1)) ^ RC[i], RC[i]=(i+1)*0x9E3779B97F4A7C15.

Bijectivity (fixed key): x^=x>>s (s<64) is triangular w/ 1s on diagonal =>
bijective; x*=odd and x+=(x<<k) i.e. *(2^k+1) with k>=1 odd => bijective;
xor-rk bijective. Composition => permutation of 2^64. Final op is always a
downward xorshift so no output bit is a linear wire-through (round-2 bit law:
odd mult copies bit 0 exactly; the trailing x^=x>>s repairs it).
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, rotl64_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
C3 = 0x100000000000003F
C8 = sum(1 << s for s in (63, 55, 47, 39, 31, 23, 15, 0))
assert C3 & 1 and C8 & 1


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def mix_xsm_c3_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    x = x ^ (x >> np.uint64(33))
    x = x * np.uint64(C3)
    x = x ^ _rk_np(k, 0)
    x = x ^ (x >> np.uint64(27))
    x = x ^ ((x << np.uint64(17)) & MASK64)
    x = x ^ _rk_np(k, 1)
    x = x ^ (x >> np.uint64(29))
    return x & MASK64


def mix_xsm_c8_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    x = x ^ (x >> np.uint64(31))
    x = x * np.uint64(C8)
    x = x ^ _rk_np(k, 0)
    x = x ^ (x >> np.uint64(28))
    x = x ^ ((x << np.uint64(23)) & MASK64)
    x = x ^ _rk_np(k, 1)
    x = x ^ (x >> np.uint64(30))
    return x & MASK64


def mix_xsm_sa_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    x = x ^ (x >> np.uint64(33))
    x = (((x << np.uint64(13)) & MASK64) + x) & MASK64
    x = x ^ _rk_np(k, 0)
    x = x ^ (x >> np.uint64(27))
    x = (((x << np.uint64(29)) & MASK64) + x) & MASK64
    x = x ^ _rk_np(k, 1)
    x = x ^ (x >> np.uint64(31))
    return x & MASK64


# ---- scalar versions ----
def _rotl64_s(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_s(key, i):
    return (_rotl64_s(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)) & M64


def mix_xsm_c3_s(v, k):
    x = (v ^ k) & M64
    x = (x ^ (x >> 33)) & M64
    x = (x * C3) & M64
    x = (x ^ _rk_s(k, 0)) & M64
    x = (x ^ (x >> 27)) & M64
    x = (x ^ ((x << 17) & M64)) & M64
    x = (x ^ _rk_s(k, 1)) & M64
    return (x ^ (x >> 29)) & M64


def mix_xsm_c8_s(v, k):
    x = (v ^ k) & M64
    x = (x ^ (x >> 31)) & M64
    x = (x * C8) & M64
    x = (x ^ _rk_s(k, 0)) & M64
    x = (x ^ (x >> 28)) & M64
    x = (x ^ ((x << 23) & M64)) & M64
    x = (x ^ _rk_s(k, 1)) & M64
    return (x ^ (x >> 30)) & M64


def mix_xsm_sa_s(v, k):
    x = (v ^ k) & M64
    x = (x ^ (x >> 33)) & M64
    x = (((x << 13) & M64) + x) & M64
    x = (x ^ _rk_s(k, 0)) & M64
    x = (x ^ (x >> 27)) & M64
    x = (((x << 29) & M64) + x) & M64
    x = (x ^ _rk_s(k, 1)) & M64
    return (x ^ (x >> 31)) & M64


if __name__ == "__main__":
    for s, n in [(mix_xsm_c3_s, mix_xsm_c3_np),
                 (mix_xsm_c8_s, mix_xsm_c8_np),
                 (mix_xsm_sa_s, mix_xsm_sa_np)]:
        check_model_equiv(s, n, n.__name__)
        bijectivity_spotcheck(n, n.__name__)
